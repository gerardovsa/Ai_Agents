# Supabase API - Complete Documentation

**Python Client for Supabase Backend Services**

---

## 📚 Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Database Operations](#database-operations)
3. [Authentication](#authentication)
4. [Storage](#storage)
5. [Advanced Features](#advanced-features)
6. [Best Practices](#best-practices)
7. [Error Handling](#error-handling)

---

## Installation & Setup

### Initialize Client

```python
from supabase_client import SupabaseClient

# Using environment variables (recommended)
client = SupabaseClient()

# Or explicit credentials
client = SupabaseClient(
    url="https://your-project.supabase.co",
    key="your-anon-key"
)

# With service key for admin operations
client = SupabaseClient(
    url="https://your-project.supabase.co",
    key="your-anon-key",
    service_key="your-service-key"  # Optional, for admin ops
)
```

---

## Database Operations

### Basic CRUD

#### Select (Read)
```python
# Get all rows
all_users = client.select('users')

# Get specific columns
users = client.select('users', columns='id, name, email')

# With filters
active_users = client.select('users', filters={'status': 'active'})
```

#### Insert (Create)
```python
# Single row
new_user = client.insert('users', {
    'name': 'John Doe',
    'email': 'john@example.com',
    'age': 30
})

# Multiple rows
new_users = client.insert('users', [
    {'name': 'Alice', 'email': 'alice@example.com'},
    {'name': 'Bob', 'email': 'bob@example.com'}
])
```

#### Update
```python
# Update by ID
updated = client.update(
    'users',
    {'status': 'inactive', 'updated_at': 'NOW()'},
    filters={'id': 123}
)

# Update multiple rows
updated = client.update(
    'users',
    {'status': 'verified'},
    filters={'email_verified': True}
)
```

#### Delete
```python
# Delete by ID
deleted = client.delete('users', filters={'id': 123})

# Delete with condition
deleted = client.delete('users', filters={'status': 'inactive'})
```

### Query Builder

Fluent API for complex queries:

```python
# Basic query
users = client.query('users') \
    .select('*') \
    .execute()

# With filters
users = client.query('users') \
    .select('id, name, email') \
    .eq('status', 'active') \
    .execute()

# Multiple conditions
users = client.query('users') \
    .select('*') \
    .eq('status', 'active') \
    .gt('age', 18) \
    .order('created_at', ascending=False) \
    .limit(10) \
    .execute()

# Pattern matching
users = client.query('users') \
    .select('*') \
    .like('email', '%@gmail.com') \
    .execute()
```

#### Available Query Methods

- `.eq(column, value)` - Equal to
- `.neq(column, value)` - Not equal to
- `.gt(column, value)` - Greater than
- `.lt(column, value)` - Less than
- `.like(column, pattern)` - Pattern match
- `.order(column, ascending=True)` - Sort results
- `.limit(count)` - Limit results

### PostgreSQL Functions (RPC)

```python
# Call function without parameters
result = client.rpc('get_user_count')

# Call function with parameters
result = client.rpc('calculate_order_total', {
    'order_id': 123,
    'apply_discount': True
})

# Complex business logic
stats = client.rpc('generate_monthly_report', {
    'user_id': 456,
    'month': 10,
    'year': 2025
})
```

---

## Authentication

### Sign Up

```python
# Basic signup
result = client.sign_up(
    email='user@example.com',
    password='securePassword123'
)

# With metadata
result = client.sign_up(
    email='user@example.com',
    password='securePassword123',
    metadata={
        'full_name': 'John Doe',
        'age': 30,
        'company': 'Acme Inc'
    }
)

# Extract user info
user_id = result['user']['id']
email = result['user']['email']
```

### Sign In

```python
# Email/password login
session = client.sign_in(
    email='user@example.com',
    password='securePassword123'
)

# Extract tokens
access_token = session['access_token']
refresh_token = session['refresh_token']

# User info
user = session['user']
print(f"Logged in as: {user['email']}")
```

### Get User Info

```python
# Get current user from token
access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
user = client.get_user(access_token)

print(f"User ID: {user['id']}")
print(f"Email: {user['email']}")
print(f"Metadata: {user['user_metadata']}")
```

### Sign Out

```python
# Revoke access token
client.sign_out(access_token)
```

---

## Storage

### Upload Files

```python
# Upload file
result = client.upload_file(
    bucket='avatars',
    path='user123/profile.jpg',
    file_path='/local/path/image.jpg'
)

# Upload with content type
result = client.upload_file(
    bucket='documents',
    path='reports/2025/report.pdf',
    file_path='/local/report.pdf',
    content_type='application/pdf'
)

print(f"File uploaded: {result}")
```

### Download Files

```python
# Download to memory
content = client.download_file(
    bucket='avatars',
    path='user123/profile.jpg'
)

# Download to file
content = client.download_file(
    bucket='avatars',
    path='user123/profile.jpg',
    output_path='/local/save/profile.jpg'
)
```

### List Files

```python
# List all files in bucket
files = client.list_files('avatars')

# List files in specific path
files = client.list_files('avatars', path='user123/')

# Display files
for file in files:
    print(f"- {file['name']} ({file['metadata']['size']} bytes)")
```

### Delete Files

```python
# Delete single file
client.delete_file('avatars', 'user123/old_profile.jpg')
```

### Public URLs

```python
# Get public URL
url = client.get_public_url('avatars', 'user123/profile.jpg')
print(f"Access file at: {url}")

# Use in HTML
html = f'<img src="{url}" alt="Profile">'
```

---

## Advanced Features

### Health Check

```python
# Check connectivity
health = client.health_check()

if health['accessible']:
    print(f"✅ Supabase is online: {health['status']}")
else:
    print(f"❌ Cannot reach Supabase: {health['error']}")
```

### Complex Queries

```python
# Join-like query (use database views)
# Create view in SQL Editor first:
# CREATE VIEW user_orders AS
#     SELECT users.name, orders.total
#     FROM users JOIN orders ON users.id = orders.user_id;

results = client.select('user_orders')

# Aggregation (use RPC function)
total = client.rpc('sum_column', {
    'table_name': 'orders',
    'column_name': 'amount'
})
```

### Batch Operations

```python
# Insert multiple rows efficiently
users = [
    {'name': f'User {i}', 'email': f'user{i}@example.com'}
    for i in range(100)
]
client.insert('users', users)

# Update in batches
for batch in chunks(user_ids, size=50):
    client.update('users', {'processed': True}, filters={'id': batch})
```

---

## Best Practices

### 1. Environment Variables

```python
# ✅ Good - Use environment variables
client = SupabaseClient()

# ❌ Bad - Hardcoded credentials
client = SupabaseClient(
    url="https://hardcoded.supabase.co",
    key="hardcoded-key-123"
)
```

### 2. Error Handling

```python
# ✅ Good - Handle errors gracefully
try:
    users = client.select('users')
except Exception as e:
    print(f"Error fetching users: {e}")
    users = []

# ❌ Bad - No error handling
users = client.select('users')  # May crash
```

### 3. Row Level Security

```sql
-- Always enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can read own data"
    ON users FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own data"
    ON users FOR UPDATE
    USING (auth.uid() = id);
```

### 4. Connection Reuse

```python
# ✅ Good - Reuse client instance
client = SupabaseClient()

for item in items:
    client.insert('logs', item)

# ❌ Bad - Creating new client each time
for item in items:
    client = SupabaseClient()  # Wasteful
    client.insert('logs', item)
```

### 5. Use Query Builder

```python
# ✅ Good - Fluent, readable
users = client.query('users') \
    .select('id, name') \
    .eq('status', 'active') \
    .order('created_at') \
    .execute()

# ❌ Less maintainable - Manual filtering
all_users = client.select('users')
active = [u for u in all_users if u['status'] == 'active']
```

---

## Error Handling

### Common Errors

#### Connection Errors
```python
try:
    health = client.health_check()
    if not health['accessible']:
        print("Supabase not reachable")
except Exception as e:
    print(f"Connection error: {e}")
```

#### Authentication Errors
```python
try:
    session = client.sign_in(email, password)
except Exception as e:
    if 'Invalid login' in str(e):
        print("Wrong email or password")
    else:
        print(f"Auth error: {e}")
```

#### Permission Errors
```python
try:
    data = client.select('admin_table')
except Exception as e:
    if 'permission denied' in str(e).lower():
        print("You don't have access to this table")
        print("Check Row Level Security policies")
    else:
        raise
```

### Retry Logic

```python
import time

def query_with_retry(client, table, max_retries=3):
    """Query with automatic retry on failure."""
    for attempt in range(max_retries):
        try:
            return client.select(table)
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Retry {attempt + 1}/{max_retries} in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
```

---

## Examples by Use Case

### User Management System

```python
# Register user
user = client.sign_up('john@example.com', 'password123', {
    'full_name': 'John Doe',
    'role': 'member'
})

# Create user profile
client.insert('profiles', {
    'user_id': user['user']['id'],
    'bio': 'Software developer',
    'avatar_url': 'https://...'
})

# Update profile
client.update('profiles', 
    {'bio': 'Senior developer'},
    filters={'user_id': user['user']['id']}
)

# Get user with profile
profile = client.query('profiles') \
    .select('*, users(email, created_at)') \
    .eq('user_id', user_id) \
    .execute()
```

### File Upload System

```python
# Upload user document
result = client.upload_file(
    bucket='documents',
    path=f'users/{user_id}/resume.pdf',
    file_path=local_file_path
)

# Save metadata to database
client.insert('documents', {
    'user_id': user_id,
    'filename': 'resume.pdf',
    'path': f'users/{user_id}/resume.pdf',
    'size': os.path.getsize(local_file_path),
    'mime_type': 'application/pdf'
})

# Get public URL
url = client.get_public_url('documents', f'users/{user_id}/resume.pdf')
```

### Analytics System

```python
# Log event
client.insert('events', {
    'user_id': user_id,
    'event_type': 'page_view',
    'page': '/dashboard',
    'timestamp': datetime.now().isoformat()
})

# Get analytics via RPC
stats = client.rpc('get_user_stats', {
    'user_id': user_id,
    'start_date': '2025-10-01',
    'end_date': '2025-10-31'
})
```

---

**For more examples, see `test_supabase_connection.py`**

**Last Updated:** October 23, 2025
