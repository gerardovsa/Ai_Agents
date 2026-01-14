# Scheduler Worker Duplication Fix

## 🐛 Problem

APScheduler `_check_pending_approvals` job runs **twice every minute** because Gunicorn has 2 workers, and each worker starts its own scheduler instance.

```
INFO:apscheduler.executors.default:Running job "AutomationScheduler._check_pending_approvals 
(scheduled at 2025-12-09 01:12:21.573164+00:00)  ← Worker 1

INFO:apscheduler.executors.default:Running job "AutomationScheduler._check_pending_approvals 
(scheduled at 2025-12-09 01:12:21.582101+00:00)  ← Worker 2 (9ms later)
```

## ✅ Solution Options

### Option 1: Single-Worker Scheduler (Recommended)

Use a **post_fork** hook to only start scheduler in one worker:

**Create:** `gunicorn_config.py`

```python
"""
Gunicorn configuration for AI_agents Flask app
Ensures scheduler only runs in worker #1 to prevent duplicate jobs
"""
import os
import multiprocessing

# Worker configuration
workers = 2  # 1 CPU × 2
worker_class = 'geventwebsocket.gunicorn.workers.GeventWebSocketWorker'
bind = f"0.0.0.0:{os.getenv('PORT', '10000')}"
timeout = 120
keepalive = 5

# Logging
loglevel = 'info'
accesslog = '-'
errorlog = '-'

# Scheduler control - only start in worker #1
def post_fork(server, worker):
    """
    Called after worker process is forked
    Only start scheduler in the first worker to prevent duplicate jobs
    """
    from AI_infrastructure.scheduler import start_scheduler
    
    # worker.age is unique per worker, starts at 0
    if worker.age == 0:  # First worker only
        print(f"[SCHEDULER] Starting in worker {worker.pid} (age={worker.age})")
        start_scheduler()
    else:
        print(f"[SCHEDULER] Skipping in worker {worker.pid} (age={worker.age}) - already running in worker 0")
```

**Update:** `startup.sh`

```bash
# Before:
exec gunicorn \
    --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker \
    --workers 2 \
    --bind 0.0.0.0:$PORT \
    ...

# After:
exec gunicorn \
    --config gunicorn_config.py \
    AI_infrastructure.flask_app:app
```

### Option 2: Separate Scheduler Process

Run scheduler in a **separate container/service** (like a cron job):

**Create:** `scheduler_daemon.py`

```python
"""
Standalone scheduler daemon - runs independently of Flask workers
"""
import time
from AI_infrastructure.scheduler import start_scheduler

if __name__ == '__main__':
    print("[SCHEDULER DAEMON] Starting...")
    scheduler = start_scheduler()
    
    try:
        # Keep alive forever
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("[SCHEDULER DAEMON] Stopping...")
        scheduler.stop()
```

**Run separately:**
```bash
# In a separate terminal or background process
python scheduler_daemon.py &
```

### Option 3: Disable Scheduler Entirely (If Not Needed)

If you're not using automation approvals yet:

**Update:** `AI_infrastructure/scheduler.py`

```python
def start(self):
    """Start the scheduler"""
    # TEMPORARILY DISABLED - Enable when automation workflows are ready
    logger.warning("Scheduler disabled - automation workflows not yet active")
    return
    
    # ... existing code
```

## 🎯 Recommended Fix: Option 1

**Pros:**
- ✅ Simple configuration change
- ✅ Scheduler runs in same process as Flask (shared memory)
- ✅ No additional containers/processes needed
- ✅ Works with Render auto-deploy

**Cons:**
- ⚠️ If worker #1 crashes, scheduler stops until restart

## 📋 Implementation Steps

1. Create `gunicorn_config.py` in AI_agents root
2. Update `startup.sh` to use `--config gunicorn_config.py`
3. Test locally: `gunicorn --config gunicorn_config.py AI_infrastructure.flask_app:app`
4. Commit and push to v10
5. Check logs - should see only **1** scheduler instance

## 🧪 Verification

After deployment, check logs for:

```bash
# Should see ONCE per minute:
INFO:apscheduler.executors.default:Running job "AutomationScheduler._check_pending_approvals
(trigger: interval[0:01:00], next run at: ...)

# Should see on startup:
[SCHEDULER] Starting in worker XXXXX (age=0)
[SCHEDULER] Skipping in worker YYYYY (age=1) - already running in worker 0
```

## 🔍 Current Frequency Summary

**Health Checks:** Every 5 seconds  
- **Source:** Render load balancer  
- **Purpose:** Keep-alive and health monitoring  
- **Impact:** Minimal (~0.5ms response time)  
- **Action:** ✅ No change needed (standard behavior)

**Approval Checks:** Every 1 minute × 2 workers  
- **Source:** APScheduler in each Gunicorn worker  
- **Purpose:** Monitor automation approval workflow  
- **Impact:** Duplicate DB queries and log spam  
- **Action:** ⚠️ **FIX WITH OPTION 1** (single-worker scheduler)

---

**Status:** Ready to implement  
**Priority:** Medium (cosmetic issue, not breaking functionality)  
**Effort:** 10 minutes (create config file + update startup.sh)
