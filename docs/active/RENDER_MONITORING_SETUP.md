# Render Monitoring Setup — June 15, 2026

> Step-by-step guide for the new Render service that tracks
> `cleanup/root-md-cleanup` (commit `884d8ed8` and later).
> Mirrors the existing v11 service spec: 1 CPU, 2 GB RAM, 10 GB
> attached disk.

This guide assumes you have already created the new Web Service in
Render (connected to `gerardovsa/Ai_Agents` branch `cleanup/root-md-cleanup`,
Dockerfile at `./Dockerfile`, health check path `/health`).

The order below is deliberate — each step builds on the prior one.

---

## 1. Build filters — speed up cleanup-round deploys

The cleanup round will generate many commits in `archive/`, `docs/`,
`*.md`, `tests/`, and other non-runtime paths. Without a filter, every
commit triggers a fresh Docker build (5-10 min) and BGE model
re-download (3-5 min the first time, but wasted cycles on every
re-deploy of an unchanged container).

**Path:** `Settings → Build Filters → Ignored Paths`

Add these (one per line):

```
archive/**
docs/**
*.md
tests/**
tools/testing/**
.claude/**
.github/**
```

> ⚠️ **Do NOT** ignore `requirements.txt` or `Dockerfile` at the root —
> those DO need a rebuild. The ignored paths above only match if
> they're at the root or in the listed subdirs, which is exactly what
> we want.

**Verify after a test commit:** push a no-op change to one of the
ignored paths; the new service should NOT show a new build in the
Render dashboard.

---

## 2. Environment variables

**Path:** `Environment → Environment Variables`

### 2a. Copy from the v11 service (REQUIRED)

Open the v11 service's Environment tab and copy every variable.
Critical ones (per CLAUDE.md §3):

```
ANTHROPIC_API_KEY
OPENAI_API_KEY
DEEPSEEK_API_KEY_1
MINIMAX_API_KEY                    # from org vault per migration 051
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
MICROSOFT_CLIENT_ID
MICROSOFT_CLIENT_SECRET
JWT_SECRET
SECRET_KEY
SUPABASE_URL
SUPABASE_SERVICE_KEY
USE_SUPABASE
FRONTEND_URL
CREDENTIAL_ENCRYPTION_KEY          # MUST match v11 exactly — see §2b
```

### 2b. CREDENTIAL_ENCRYPTION_KEY — the silent-killer

The Fernet key **must be identical** to v11. The org vault table
(`organisation_platform_credentials`) holds encrypted values that can
only be decrypted with the exact same key. If the new service starts
with a different key, every integration lookup (Pinecone, Xero,
Shopify, etc.) will fail with `InvalidToken` — silently, with no
startup error.

**Verify after first deploy:** call `GET /api/admin/diagnostics` and
check the `vault` probe returns `status: healthy`. If it returns
`status: unhealthy` with `error: roundtrip mismatch`, the key
mismatch is the cause.

### 2c. New monitoring-related env vars (recommended)

```
# Sentry — error tracking
SENTRY_DSN=https://<key>@<org>.ingest.sentry.io/<project>
SENTRY_ENVIRONMENT=staging
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_SEND_PII=true

# Slack — alerts (use the same webhook the v11 service uses, or
# create a new channel for the cleanup instance)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T.../B.../...

# Debug agent (only needed if you run it as a Render cron or worker)
PLATFORM_BASE_URL=https://<your-new-service>.onrender.com
DEBUG_AGENT_INTERVAL_SEC=300
DEBUG_AGENT_AUTO_HEAL=false
```

`SENTRY_DSN` and `SLACK_WEBHOOK_URL` are both OPTIONAL — the platform
runs normally without them; you just lose error aggregation and Slack
alerting respectively.

---

## 3. Build filter (already in §1) + first deploy

Hit **Save Changes** and let the first deploy run. Expected timing:

| Phase | Time |
|---|---|
| `pip install` (Docker layer 2) | 2-4 min |
| `npm install` (layer 3) | 30-60 s |
| `COPY .` (layer 4) | 5-15 s |
| Container start + BGE download | 1-3 min |
| `/health` returns 200 | ~5-10 min total |

Watch the deploy log for:

```
[INIT] BGE model loaded from snapshot
[VECTOR_DB] pgvector extension active
```

If BGE is downloaded fresh (no cache), add another 3-5 min.

---

## 4. OAuth redirect URIs (the gotcha)

The new service gets a different URL like `ai-agents-cleanup.onrender.com`.
Before users can log in with Google/Microsoft on the new service, you
MUST add the new callback URLs to each provider's allowed redirect list.

### Google

**Path:** Google Cloud Console → APIs & Services → Credentials →
OAuth 2.0 Client IDs → your client → Authorized redirect URIs

Add:
```
https://<your-new-service>.onrender.com/oauth/google/callback
https://<your-new-service>.onrender.com/api/auth/google/callback
```

(Check `AI_infrastructure/routes/oauth_routes.py` for the exact path
if either doesn't match — search for `redirect_uri` in the file.)

### Microsoft

**Path:** Azure Portal → App registrations → your app → Authentication
→ Redirect URIs → Add URI

Add:
```
https://<your-new-service>.onrender.com/oauth/microsoft/callback
https://<your-new-service>.onrender.com/api/auth/microsoft/callback
```

---

## 5. Smoke-test the new service

Once the deploy is healthy, verify each layer:

| # | Test | Expected | Endpoint |
|---|---|---|---|
| 1 | Service is up | `200 OK` from `/` (the SPA) | `curl -I https://<svc>.onrender.com/` |
| 2 | Health check | `{"status":"healthy","providers":["anthropic","deepseek","openai","MiniMax"],...}` | `curl https://<svc>.onrender.com/health` |
| 3 | Login round-trips | Login screen renders, JWT issued | open in browser |
| 4 | Sidebar modules load | Org-aware modules appear | open in browser after login |
| 5 | AI chat works | Send a message, get a response | open in browser |
| 6 | Vault decrypt | `/api/admin/diagnostics` returns `vault.status: healthy` | auth required |
| 7 | Sentry wires up | If `SENTRY_DSN` set, deploy log shows `[SENTRY] Initialized` | check deploy log |
| 8 | All 4 providers listed | `/health` providers list has MiniMax | `curl .../health` |

**If test 6 fails:** the CREDENTIAL_ENCRYPTION_KEY is mismatched —
copy it again from the v11 service. See §2b.

**If test 7 fails:** the DSN is wrong or the Sentry project was
deleted. Re-create the DSN at sentry.io → Settings → Client Keys.

---

## 6. Render alerts (built-in, no code)

**Path:** `Alerts → New Alert Policy`

| Alert name | Condition | Action |
|---|---|---|
| Service down | `HTTP check /health` fails 3x in a row | Email + Slack webhook |
| High memory | Memory > 85% for 5 min | Email |
| High CPU | CPU > 95% for 10 min | Email |
| Deploy failed | Build exits non-zero | Slack webhook |
| Disk pressure | Disk > 85% (Render surfaces this on persistent disks) | Email |

For Slack, paste the same `SLACK_WEBHOOK_URL` you used for the debug
agent in §2c.

---

## 7. Run the debug agent (optional but recommended)

The debug agent is a standalone Python CLI — it can run as a Render
cron job, a sidecar background worker, or manually from your laptop.

### Option A: Render Cron Job (recommended)

**Path:** `New → Cron Job`

| Field | Value |
|---|---|
| Branch | `cleanup/root-md-cleanup` |
| Command | `cd /app && python -m monitoring.debug_agent check --use-render` |
| Schedule | `*/5 * * * *` (every 5 min) |
| Env vars | `RENDER_API_KEY`, `RENDER_SERVICE_ID`, `PLATFORM_BASE_URL=<this-svc>`, `SLACK_WEBHOOK_URL`, `SENTRY_DSN` |

### Option B: Sidecar Background Worker

**Path:** `New → Background Worker`

Same env vars, but the command is a long-running loop:

```bash
cd /app && python -m monitoring.debug_agent daemon --interval 300 --use-render
```

Add `--auto-heal` if you want the agent to restart the service on
sustained failure (default: 3 consecutive failures).

### Option C: Manual one-shot (from your laptop)

```bash
git clone https://github.com/gerardovsa/Ai_Agents.git
cd Ai_Agents
git checkout cleanup/root-md-cleanup
pip install -r requirements.txt
export PLATFORM_BASE_URL=https://<your-new-svc>.onrender.com
export DEBUG_AGENT_AUTH_TOKEN=<a-jwt-from-an-admin-user>
export RENDER_API_KEY=<from-render-dashboard>
export RENDER_SERVICE_ID=<from-render-dashboard>
python -m monitoring.debug_agent check --use-render
```

This runs once and exits with code 0 (healthy) / 1 (degraded) / 2
(unhealthy) — perfect for CI.

---

## 8. Rollback (the safety net)

The new service inherits Render's default: **last 3 successful
deploys are kept**. To roll back:

**Path:** Service dashboard → Deploys → click a previous deploy →
"Roll back to this deploy"

This is the same flow as v11 — no new procedure to learn.

If you want to nuke the new service entirely and go back to v11-only:
**Service Settings → Danger Zone → Delete Service**. The v11 service
is unaffected.

---

## Reference — env vars cheat sheet

| Var | Required? | Purpose |
|---|---|---|
| `CREDENTIAL_ENCRYPTION_KEY` | **YES** | Must match v11 exactly. See §2b. |
| `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` | **YES** | Database. |
| `JWT_SECRET`, `SECRET_KEY` | **YES** | Auth. |
| `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `DEEPSEEK_API_KEY_1`, `MINIMAX_API_KEY` | **YES** (any one is enough) | AI providers. |
| `SENTRY_DSN` | optional | Error tracking. |
| `SLACK_WEBHOOK_URL` | optional | Alert sink. |
| `RENDER_API_KEY`, `RENDER_SERVICE_ID` | optional | Enables debug-agent auto-heal. |
| `PLATFORM_BASE_URL` | optional | For the debug agent to know its own URL. |
| `DEBUG_AGENT_AUTH_TOKEN` | optional | JWT for `/api/admin/diagnostics` probes. |

---

## Reference — new endpoints added in commit `884d8ed8`

| Endpoint | Method | Auth | Purpose |
|---|---|---|---|
| `/api/admin/diagnostics` | GET | required | Deep probe (DB, pgvector, vault, memory, all 4 AI providers, tool registry) |
| `/api/admin/diagnostics/summary` | GET | required | Lightweight probe (DB, vault, memory) — safe to poll every 30-60s |
| `/api/admin/diagnostics/provider/<name>` | GET | required | Single-provider probe (name: `anthropic` \| `openai` \| `deepseek` \| `minimax`) |
| `/health` | GET | none | Existing — providers list now includes `MiniMax` |

**Why auth on diagnostics?** It exposes internal probe details
(connection pool state, vault ciphertext prefix, deploy SHA). A
service account JWT is sufficient — no admin role required.
