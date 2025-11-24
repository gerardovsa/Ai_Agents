# Supabase CLI & Edge Functions Setup Guide

**Date:** November 24, 2025  
**Project:** InHouse AI Agents  
**Supabase Project ID:** `ryoicrdifiqhqpsnjmdo`

---

## Access Token

**CLI Access Token:** `sbp_26cffc137c96e97f6f9cb8b84fc1caa30ab9d452`  
**Added to:** `.env.master` as `SUPABASE_ACCESS_TOKEN`

---

## Installation

### Install Supabase CLI

**Windows (PowerShell):**
```powershell
# Install via Scoop
scoop bucket add supabase https://github.com/supabase/scoop-bucket.git
scoop install supabase

# Or install via npm
npm install -g supabase
```

**Verify installation:**
```powershell
supabase --version
```

---

## Authentication

### Login to Supabase

```powershell
# Option 1: Login interactively (opens browser)
supabase login

# Option 2: Login with access token
$env:SUPABASE_ACCESS_TOKEN = "sbp_26cffc137c96e97f6f9cb8b84fc1caa30ab9d452"
supabase login
```

**Verify login:**
```powershell
supabase projects list
```

Expected output:
```
┌────────────────────────┬──────────────────────────┬──────────────────┐
│ PROJECT NAME           │ PROJECT ID               │ ORGANIZATION     │
├────────────────────────┼──────────────────────────┼──────────────────┤
│ InHouse                │ ryoicrdifiqhqpsnjmdo     │ ...              │
└────────────────────────┴──────────────────────────┴──────────────────┘
```

---

## Edge Functions

### Create a New Function

```powershell
# Navigate to your project
cd C:\Users\gpoli\GIT\AI_agents

# Create function
supabase functions new hello-world
```

This creates:
```
AI_agents/
└── supabase/
    └── functions/
        └── hello-world/
            └── index.ts
```

### Function Template (TypeScript)

```typescript
// supabase/functions/hello-world/index.ts

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req) => {
  const { name } = await req.json()
  const data = {
    message: `Hello ${name}!`,
    timestamp: new Date().toISOString()
  }

  return new Response(
    JSON.stringify(data),
    { headers: { "Content-Type": "application/json" } },
  )
})
```

### Deploy Function

```powershell
# Deploy to Supabase
supabase functions deploy hello-world --project-ref ryoicrdifiqhqpsnjmdo

# Or deploy all functions
supabase functions deploy --project-ref ryoicrdifiqhqpsnjmdo
```

### Invoke Function

**Using curl:**
```powershell
curl -L -X POST 'https://ryoicrdifiqhqpsnjmdo.supabase.co/functions/v1/hello-world' `
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ5b2ljcmRpZmlxaHFwc25qbWRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI2NjQyNDUsImV4cCI6MjA3ODI0MDI0NX0.tbDfmZDiQFU2iccPwrUj3S19sCqUlne25CNlt0BGm7c' `
  --data '{"name":"InHouse"}'
```

**Using JavaScript:**
```javascript
const { data, error } = await supabaseClient.functions.invoke('hello-world', {
  body: { name: 'InHouse' }
})
```

**Using Python:**
```python
from supabase import create_client

supabase = create_client(
    'https://ryoicrdifiqhqpsnjmdo.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
)

response = supabase.functions.invoke('hello-world', {'name': 'InHouse'})
```

---

## Useful Examples

### 1. Heartbeat Function (Keep-Alive)

**File:** `supabase/functions/heartbeat/index.ts`

```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req) => {
  const data = {
    event: 'heartbeat',
    timestamp: new Date().toISOString(),
    message: 'Server heartbeat - connection alive'
  }

  return new Response(
    JSON.stringify(data),
    { 
      headers: { 
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      } 
    },
  )
})
```

**Deploy:**
```powershell
supabase functions deploy heartbeat --project-ref ryoicrdifiqhqpsnjmdo
```

**Call from frontend:**
```javascript
// Every 60 seconds
setInterval(async () => {
  const { data } = await supabaseClient.functions.invoke('heartbeat')
  console.log('💓 Heartbeat:', data)
}, 60000)
```

### 2. Database Query Function

**File:** `supabase/functions/query-threads/index.ts`

```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

serve(async (req) => {
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL') ?? '',
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
  )

  const { data, error } = await supabase
    .from('sessions.threads')
    .select('*')
    .limit(10)

  if (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    )
  }

  return new Response(
    JSON.stringify({ threads: data }),
    { headers: { "Content-Type": "application/json" } }
  )
})
```

### 3. AI Processing Function

**File:** `supabase/functions/ai-process/index.ts`

```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req) => {
  const { text } = await req.json()
  
  // Call OpenAI/Claude/etc.
  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${Deno.env.get('OPENAI_API_KEY')}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'gpt-4',
      messages: [{ role: 'user', content: text }]
    })
  })

  const data = await response.json()

  return new Response(
    JSON.stringify({ result: data.choices[0].message.content }),
    { headers: { "Content-Type": "application/json" } }
  )
})
```

---

## Environment Variables

### Set Function Secrets

```powershell
# Set secrets for Edge Functions
supabase secrets set OPENAI_API_KEY=sk-... --project-ref ryoicrdifiqhqpsnjmdo
supabase secrets set ANTHROPIC_API_KEY=sk-ant-... --project-ref ryoicrdifiqhqpsnjmdo

# List secrets
supabase secrets list --project-ref ryoicrdifiqhqpsnjmdo
```

### Access Secrets in Functions

```typescript
const openaiKey = Deno.env.get('OPENAI_API_KEY')
const supabaseUrl = Deno.env.get('SUPABASE_URL')
const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')
```

---

## Local Development

### Start Local Supabase

```powershell
cd C:\Users\gpoli\GIT\AI_agents

# Initialize Supabase (first time only)
supabase init

# Start local Supabase
supabase start

# This starts:
# - PostgreSQL database (port 5432)
# - Studio (http://localhost:54323)
# - API (http://localhost:54321)
# - Edge Functions (port 54321)
```

### Test Functions Locally

```powershell
# Serve function locally
supabase functions serve hello-world

# Invoke locally
curl -L -X POST 'http://localhost:54321/functions/v1/hello-world' `
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' `
  --data '{"name":"Local Test"}'
```

---

## Monitoring & Debugging

### View Function Logs

```powershell
# Real-time logs
supabase functions logs hello-world --project-ref ryoicrdifiqhqpsnjmdo

# Or view in Dashboard
# https://supabase.com/dashboard/project/ryoicrdifiqhqpsnjmdo/functions
```

### Function Analytics

Go to: [Supabase Dashboard → Edge Functions](https://supabase.com/dashboard/project/ryoicrdifiqhqpsnjmdo/functions)

View:
- Invocation count
- Error rate
- Response times
- Recent logs

---

## Common Commands

```powershell
# List functions
supabase functions list --project-ref ryoicrdifiqhqpsnjmdo

# Delete function
supabase functions delete hello-world --project-ref ryoicrdifiqhqpsnjmdo

# Download function
supabase functions download hello-world --project-ref ryoicrdifiqhqpsnjmdo

# Get function URL
echo "https://ryoicrdifiqhqpsnjmdo.supabase.co/functions/v1/hello-world"
```

---

## GitHub Examples

Browse examples: [Supabase Edge Functions Examples](https://github.com/supabase/supabase/tree/master/examples/edge-functions/supabase/functions)

**Popular examples:**
- `stripe-webhooks` - Handle Stripe webhooks
- `send-email` - Send emails via SMTP
- `generate-image` - AI image generation
- `og-images` - Dynamic Open Graph images
- `openai` - OpenAI integration

**Clone examples:**
```powershell
git clone https://github.com/supabase/supabase.git
cd supabase/examples/edge-functions
```

---

## Best Practices

### 1. ✅ Use TypeScript

```typescript
// Define types
interface RequestBody {
  name: string
  email: string
}

interface ResponseData {
  success: boolean
  message: string
}

serve(async (req: Request): Promise<Response> => {
  const body: RequestBody = await req.json()
  const data: ResponseData = {
    success: true,
    message: `Hello ${body.name}!`
  }
  return new Response(JSON.stringify(data))
})
```

### 2. ✅ Handle CORS

```typescript
serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
        'Access-Control-Allow-Headers': 'authorization, content-type'
      }
    })
  }

  // Your function logic...
  const data = { message: 'Success' }

  return new Response(JSON.stringify(data), {
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*'
    }
  })
})
```

### 3. ✅ Error Handling

```typescript
serve(async (req) => {
  try {
    const body = await req.json()
    
    if (!body.name) {
      throw new Error('name is required')
    }

    const data = { message: `Hello ${body.name}!` }
    return new Response(JSON.stringify(data), { status: 200 })

  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { 
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      }
    )
  }
})
```

### 4. ✅ Use Secrets for API Keys

```typescript
// ❌ DON'T
const apiKey = 'sk-123456789'

// ✅ DO
const apiKey = Deno.env.get('OPENAI_API_KEY')
if (!apiKey) {
  throw new Error('OPENAI_API_KEY not set')
}
```

### 5. ✅ Set Timeouts

```typescript
const controller = new AbortController()
const timeoutId = setTimeout(() => controller.abort(), 10000) // 10s timeout

try {
  const response = await fetch('https://api.example.com', {
    signal: controller.signal
  })
  clearTimeout(timeoutId)
  return response
} catch (error) {
  if (error.name === 'AbortError') {
    return new Response('Request timeout', { status: 408 })
  }
  throw error
}
```

---

## Troubleshooting

### ❌ "Function not found"

**Solution:**
```powershell
# Verify function is deployed
supabase functions list --project-ref ryoicrdifiqhqpsnjmdo

# Redeploy
supabase functions deploy function-name --project-ref ryoicrdifiqhqpsnjmdo
```

### ❌ "Authorization required"

**Solution:**
```powershell
# Check you're passing ANON_KEY in Authorization header
curl -H 'Authorization: Bearer YOUR_ANON_KEY' ...
```

### ❌ "Environment variable not set"

**Solution:**
```powershell
# Set secret
supabase secrets set VAR_NAME=value --project-ref ryoicrdifiqhqpsnjmdo

# Redeploy function (needed after setting secrets)
supabase functions deploy function-name --project-ref ryoicrdifiqhqpsnjmdo
```

---

## Next Steps

1. ✅ Install Supabase CLI (`scoop install supabase`)
2. ✅ Login with access token (`supabase login`)
3. ✅ Create first function (`supabase functions new test-function`)
4. ✅ Deploy function (`supabase functions deploy test-function --project-ref ryoicrdifiqhqpsnjmdo`)
5. ✅ Test function (curl or JavaScript)
6. ✅ Browse examples on GitHub
7. ✅ Build your own functions!

---

**Last Updated:** November 24, 2025  
**Documentation:** https://supabase.com/docs/guides/functions  
**Examples:** https://github.com/supabase/supabase/tree/master/examples/edge-functions
