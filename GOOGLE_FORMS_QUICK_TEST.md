# Google Forms - Quick Test Guide

## ✅ All Fixes Applied - Ready for Testing

---

## Quick Setup (OAuth Authentication)

**Step 1: Authenticate with Google**
```
Open browser: http://localhost:5001/api/auth/google/login?user_id=12
```

**Step 2: Verify authentication worked**
```powershell
# Check if credentials exist
python -c "import sys; sys.path.insert(0, 'AI_infrastructure'); from auth.credential_injector import get_user_forms_service; print('Testing...'); service = get_user_forms_service(user_id=12); print('✅ Authenticated!')"
```

---

## Quick Tests

### Test 1: Basic Form Creation
```powershell
python -c "
import sys
sys.path.insert(0, 'AI_infrastructure')
from tools.registry_v3 import RegistryV3

r = RegistryV3()
result = r.execute_tool(
    'google_forms_create_form',
    title='Test Form - Quick Test',
    description='Testing the two-step creation fix',
    shareable=True,
    _user_id=12,
    _injected_credentials=True
)
print(f'✅ Form created: {result[\"form_id\"]}')
print(f'URL: {result[\"responder_uri\"]}')
"
```

### Test 2: Complete Form with Questions
```powershell
python -c "
import sys
sys.path.insert(0, 'AI_infrastructure')
from tools.registry_v3 import RegistryV3

r = RegistryV3()
result = r.execute_tool(
    'google_forms_create_complete_form',
    title='Customer Survey',
    description='Quick survey test',
    questions=[
        {'type': 'text', 'text': 'Your name?', 'required': True},
        {'type': 'multiple_choice', 'text': 'How satisfied?', 'options': ['Very', 'Somewhat', 'Not'], 'required': True}
    ],
    shareable=True,
    _user_id=12,
    _injected_credentials=True
)
print(f'✅ Form created with {len(result.get(\"questions\", []))} questions')
print(f'URL: {result[\"responder_uri\"]}')
"
```

### Test 3: AI Form Generation
```powershell
python -c "
import sys
sys.path.insert(0, 'AI_infrastructure')
from tools.registry_v3 import RegistryV3

r = RegistryV3()
result = r.execute_tool(
    'google_forms_ai_generate_form',
    prompt='Create a restaurant feedback survey with 5 questions',
    form_type='survey',
    shareable=True,
    ai_model='gpt-4',
    _user_id=12,
    _injected_credentials=True
)
print(f'✅ AI generated {result.get(\"questions_count\")} questions')
print(f'URL: {result[\"responder_uri\"]}')
"
```

---

## Verify Fixes Are Loaded

```powershell
# Check function has fixes
python test_direct_import.py

# Expected output:
# ✅ ALL FIXES PRESENT IN LOADED FUNCTION
```

---

## Troubleshooting

### Error: "access_token required"
**Fix**: Authenticate first via OAuth flow  
```
http://localhost:5001/api/auth/google/login?user_id=12
```

### Error: HTTP 400 "Only info.title can be set"
**Fix**: Fixes not loaded - clear cache and restart
```powershell
Remove-Item google_workspace\__pycache__\*.pyc -Force
Get-Process python* | Stop-Process -Force
```

### Error: HTTP 500 "Internal error"
**Fix**: Service account not configured - use OAuth instead
```
Use OAuth flow above, don't use service account for Forms API
```

---

## Success Criteria

✅ Test 1: Basic form created with description  
✅ Test 2: Complete form with questions created  
✅ Test 3: AI generated form created  
✅ No HTTP 400 errors  
✅ No BadRequestError from OpenAI  
✅ Forms accessible at returned URLs

---

**Quick Status Check**:
```powershell
python -c "
import sys
sys.path.insert(0, 'google_workspace')
from google_forms import google_forms_create_form
import inspect
src = inspect.getsource(google_forms_create_form)
print('Fix 1 (two-step):', 'STEP 1' in src and 'STEP 2' in src)
print('Fix 2 (title-only):', \"'title': title\" in src and \"'documentTitle'\" not in src.split('batchUpdate')[0])
print('Fix 3 (batchUpdate):', 'batchUpdate' in src)
"
```

Expected: All `True` ✅
