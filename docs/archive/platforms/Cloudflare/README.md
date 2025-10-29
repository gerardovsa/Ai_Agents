# Utility Scripts

This folder contains utility scripts for managing Cloudflare Workers, DNS, and infrastructure.

---

## 📊 Monitoring Scripts

### `check-workers.js`
**Purpose:** List all deployed Workers and their status

**Usage:**
```bash
node scripts/check-workers.js
```

**Output:**
- Worker name, creation/modification dates
- Route information (if accessible)
- Zone-specific routes

---

### `domain-status.js`
**Purpose:** View DNS records and domain configuration

**Usage:**
```bash
node scripts/domain-status.js
```

**Output:**
- Zone status (Active/Paused)
- Name servers
- All DNS records (A, AAAA, CNAME, TXT, etc.)
- Proxy status (Orange/Gray cloud)

---

### `test-live-worker.js`
**Purpose:** Test Worker endpoints and connectivity

**Usage:**
```bash
node scripts/test-live-worker.js
```

**Tests:**
- Workers.dev URL health check
- Custom domain connectivity
- Backend server status

---

### `check-permissions.js`
**Purpose:** Verify API token permissions

**Usage:**
```bash
node scripts/check-permissions.js
```

**Checks:**
- Token validity
- Available permissions
- Account access

---

## 🔧 Management Scripts

### `add-route.js`
**Purpose:** Add Worker route via API

**Usage:**
```bash
node scripts/add-route.js
```

**Action:**
- Creates route for `mustcare.valorsynergysuite.com/*`
- Links route to `mustcare-worker`
- Provides manual steps if API fails

---

### `fix-dns-for-worker.js`
**Purpose:** Fix DNS conflicts with Worker routes

**Usage:**
```bash
node scripts/fix-dns-for-worker.js
```

**Action:**
- Finds A record for mustcare subdomain
- Changes from Proxied (Orange) to DNS-only (Gray)
- Or provides manual instructions

---

### `create-placeholder-record.js`
**Purpose:** Create placeholder A record for Worker

**Usage:**
```bash
node scripts/create-placeholder-record.js
```

**Action:**
- Creates A record pointing to `192.0.2.1`
- Sets Proxied status (required for Workers)
- Allows Worker routes to function

---

### `delete-a-record.js`
**Purpose:** Delete A record to let Worker handle all traffic

**Usage:**
```bash
node scripts/delete-a-record.js
```

**Warning:** Only use if Worker should handle ALL traffic

---

## 🛠️ Troubleshooting Scripts

### `fix-worker-now.js`
**Purpose:** Quick fix for broken Workers (deletes Worker)

**Usage:**
```bash
node scripts/fix-worker-now.js
```

**Warning:** This DELETES the Worker - use only in emergencies

---

### `reset-worker.js`
**Purpose:** Reset Worker to default state

**Usage:**
```bash
node scripts/reset-worker.js
```

**Action:**
- Attempts to reset Worker configuration
- Provides recovery steps

---

### `manage-worker.js`
**Purpose:** Interactive Worker management

**Usage:**
```bash
node scripts/manage-worker.js
```

**Features:**
- List Workers
- View Worker details
- Manage routes

---

## 🧪 Testing Scripts

### `quick-test.js`
**Purpose:** Quick API connectivity test

**Usage:**
```bash
node scripts/quick-test.js
```

**Tests:**
- API token validity
- Basic API access
- Account information

---

### `test-client.js`
**Purpose:** Test Cloudflare AI client

**Usage:**
```bash
node scripts/test-client.js
```

**Tests:**
- AI text generation
- Error diagnostics
- API responses

---

## 📝 Script Categories

### Production-Safe (Run Anytime)
- ✅ `check-workers.js`
- ✅ `domain-status.js`
- ✅ `test-live-worker.js`
- ✅ `check-permissions.js`
- ✅ `quick-test.js`
- ✅ `test-client.js`

### Use With Caution
- ⚠️ `add-route.js` - Creates new route
- ⚠️ `fix-dns-for-worker.js` - Modifies DNS
- ⚠️ `create-placeholder-record.js` - Creates DNS record

### Emergency Only
- 🚨 `delete-a-record.js` - Deletes DNS record
- 🚨 `fix-worker-now.js` - Deletes Worker
- 🚨 `reset-worker.js` - Resets Worker

---

## 🔐 Environment Variables

All scripts require environment variables from `.env`:

```env
CLOUDFLARE_API_TOKEN=your_token
CLOUDFLARE_AI_AGENT_TOKEN=your_token
CLOUDFLARE_ACCOUNT_ID=d31a1c9ec65f373f4008216c30b071cc
```

Scripts automatically load from `.env` file.

---

## 📖 Related Documentation

- [MustCare Worker Documentation](../docs/MUSTCARE_WORKER_DOCUMENTATION.md)
- [Error Resolution Log](../docs/ERROR_RESOLUTION_LOG.md)
- [Main README](../README.md)

---

**Last Updated:** October 23, 2025
