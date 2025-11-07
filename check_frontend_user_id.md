# Frontend User ID Diagnostic Guide

**Issue:** printing@inhouseprint.com.au logged in but can't see threads

**Root Cause:** Frontend may be passing wrong user_id to API

---

## Quick Check in Browser Console

**Open browser console (F12) and run:**

```javascript
// Check what's stored in localStorage
console.log('Auth Token:', localStorage.getItem('authToken'));
console.log('User Profile:', localStorage.getItem('userProfile'));

// Parse user profile
const userProfile = JSON.parse(localStorage.getItem('userProfile'));
console.log('User ID:', userProfile?.id);
console.log('Email:', userProfile?.email);
console.log('Username:', userProfile?.username);

// Check what UserAuth thinks
console.log('UserAuth.user:', UserAuth.user);
console.log('UserAuth.token:', UserAuth.token ? 'EXISTS' : 'MISSING');
```

**Expected Result:**
```
User ID: 14
Email: printing@inhouseprint.com.au
Username: printing
```

---

## Check Network Tab

1. Open DevTools (F12)
2. Go to **Network** tab
3. Filter for: `threads`
4. Look for: `/api/threads/list?user_id=X`

**Question: What user_id is being sent?**
- If user_id=1 → Wrong! Should be 14
- If user_id=14 → Correct! (But then why no threads showing?)
- If no user_id → Missing parameter!

---

## Where Frontend Gets user_id

**File:** `business-ai-platform-v2.html`

**Line ~14960 (ThreadManager.loadThreadsFromBackend):**

```javascript
async loadThreadsFromBackend() {
    try {
        // Get user_id from UserAuth
        const userId = UserAuth.user?.id;  // ← THIS SHOULD BE 14
        
        if (!userId) {
            console.error('No user ID available');
            return;
        }
        
        const response = await fetch(
            `${API_BASE_URL}/api/threads/list?user_id=${userId}`,  // ← SENDS user_id
            {
                headers: UserAuth.getAuthHeaders()
            }
        );
        
        // Process threads...
    }
}
```

**The problem is likely:**
- `UserAuth.user` is null/undefined
- `UserAuth.user.id` is wrong (1 instead of 14)
- JWT token doesn't have correct user_id

---

## Fix Options

### Option 1: Check JWT Token Payload

**In browser console:**

```javascript
function parseJwt(token) {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
}

const token = localStorage.getItem('authToken');
const payload = parseJwt(token);
console.log('JWT Payload:', payload);
console.log('JWT user_id:', payload.user_id);
```

**Expected:** `user_id: 14`

---

### Option 2: Force User ID in Console (TEMPORARY FIX)

**Run in browser console:**

```javascript
// Manually set correct user ID
UserAuth.user = {
    id: 14,
    username: 'printing',
    email: 'printing@inhouseprint.com.au'
};

// Save to localStorage
localStorage.setItem('userProfile', JSON.stringify(UserAuth.user));

// Reload threads
ThreadManager.loadThreadsFromBackend();
```

---

### Option 3: Re-Login

1. Logout (clear localStorage)
2. Login again with Microsoft OAuth
3. Backend should return correct JWT with user_id=14

**Run in console to logout:**

```javascript
UserAuth.logout();
```

Then click "Sign in with Microsoft 365" again.

---

## Expected API Call

**Correct:**
```
GET /api/threads/list?user_id=14
Response: 6 threads (Outlook Emails, New Chat, etc.)
```

**Wrong:**
```
GET /api/threads/list?user_id=1
Response: 0 threads (User 1 has no threads now)
```

---

## Next Steps

1. **Check console:** What user_id does frontend think you are?
2. **Check network:** What user_id is being sent to API?
3. **If wrong user_id:** Logout and re-login
4. **If correct user_id but no threads:** Check ThreadManager code

---

## Contact Points

**Backend API (Working):**
- ✅ User 14 exists in both databases
- ✅ 6 threads assigned to User 14
- ✅ API returns threads correctly

**Frontend (Needs Check):**
- ❓ Is UserAuth.user.id = 14?
- ❓ Is localStorage userProfile correct?
- ❓ Is JWT token payload correct?

---

**Run these checks and report back what you find!**
