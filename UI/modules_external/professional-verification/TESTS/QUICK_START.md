# Quick Start - Computer Use Testing

## One-Line Setup

```powershell
cd c:\Users\gpoli\GIT\AI_agents\UI\modules_external\professional-verification\TESTS
.\build-and-test.ps1
```

That's it! This will:
1. ✅ Check Docker is running
2. ✅ Build the mini Docker image (~400MB)
3. ✅ Start the container
4. ✅ Have Claude browse isb.eco using Computer Use
5. ✅ Save a screenshot
6. ✅ Show you the results

## What Was Created

### Mini Docker Setup (Isolated from Main Project)
- `Dockerfile.computer-use` - Minimal Ubuntu + Chrome + VNC
- `docker-compose.yml` - Easy container management
- `start-browser.sh` - Container startup script
- `build-and-test.ps1` - One-command build and test

### Test Scripts
- `test_computer_use_auto.py` - Automated test (no user input needed)
- `demo_computer_use_live.py` - Interactive demo

### Documentation
- `README_DOCKER.md` - Complete Docker setup guide
- `QUICK_START.md` - This file

## Manual Steps (If Script Fails)

### 1. Build Docker Image
```powershell
docker-compose build
```

### 2. Start Container
```powershell
docker-compose up -d
```

### 3. Run Test
```powershell
python test_computer_use_auto.py
```

## What The Test Does

1. **Loads .env file** - Gets your Anthropic API key
2. **Checks Docker** - Verifies container is running
3. **Starts Claude** - Sends task: "Visit isb.eco and tell me what they do"
4. **Claude browses** - Takes screenshots, moves mouse, types, clicks
5. **Extracts info** - Claude reads the page and summarizes
6. **Saves screenshot** - Final view saved as PNG
7. **Shows results** - Prints Claude's findings and action log

## Expected Output

```
COMPUTER USE AUTOMATED TEST
====================================================================

✅ API key found
✅ Docker is running
✅ Container 'computer-use-test' is running
✅ Using test Docker container directly
✅ Anthropic client initialized

STARTING TEST - Claude will browse isb.eco
====================================================================

📦 Using container: computer-use-test

💬 Task: Visit https://isb.eco and tell me what they do...

🤖 Claude is working...
   Iteration 1: tool_use 📸
   Iteration 2: tool_use 🖱️ ⌨️
   Iteration 3: tool_use 👆
   Iteration 4: tool_use 📸
   Iteration 5: end_turn ✅ DONE

====================================================================
CLAUDE'S FINDINGS
====================================================================

The Institute of Sustainable Biodiversity (ISB) is an Australian 
organization focused on biodiversity conservation and sustainable 
environmental practices. They work on research, education, and 
policy development related to protecting ecosystems and species.

📸 Screenshot saved: test_screenshot_20251218_143052.png

====================================================================
ACTIONS PERFORMED
====================================================================
   1. Screenshot
   2. Move (500, 300)
   3. Type: https://isb.eco
   4. Click
   5. Screenshot

====================================================================
✅ TEST PASSED
====================================================================

Total iterations: 5
Total actions: 5
```

## Verify It Works

After the test completes:

1. **Check screenshot** - Opens in any image viewer
   ```powershell
   ii test_screenshot_*.png
   ```

2. **View container logs**
   ```powershell
   docker logs computer-use-test
   ```

3. **Connect with VNC** (optional)
   - Install [VNC Viewer](https://www.realvnc.com/en/connect/download/viewer/)
   - Connect to: `localhost:5900`
   - Password: `computeruse`
   - See exactly what Claude sees in real-time!

## Production Use

Once testing works, use the full tools:

```python
from auto_database_entry import auto_enter_verification_results

# Claude will fill your CRM/database automatically
result = await auto_enter_verification_results(
    verification_data={
        'name': 'Gregory Dutton',
        'company': 'ISB',
        'email': 'gregory.dutton@isb.eco',
        'score': 42.3
    },
    target_system='crm',
    target_url='https://your-crm.com/contacts/new',
    form_fields={'name': 'name', 'company': 'company', ...}
)
```

## Cleanup

```powershell
# Stop container
docker-compose down

# Remove everything
docker-compose down --rmi all --volumes
```

## Troubleshooting

**"Cannot connect to Docker daemon"**
- Start Docker Desktop
- Wait for it to fully start
- Try again

**"Container exits immediately"**
```powershell
docker logs computer-use-test
docker-compose build --no-cache
docker-compose up -d
```

**"Test hangs"**
```powershell
docker restart computer-use-test
Start-Sleep -Seconds 10
python test_computer_use_auto.py
```

---

**Ready?** Run `.\build-and-test.ps1` and watch Claude use a computer! 🚀
