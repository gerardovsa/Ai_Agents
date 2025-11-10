# Supabase Integration Module

Python integration for Supabase backend services - Database, Authentication, Storage, and more.

**Created:** October 23, 2025  
**Status:** ✅ Ready to Use

---

## 🚀 Quick Start

### 1. Get Your Supabase Credentials

1. **Go to:** https://supabase.com/dashboard
2. **Select your project** (or create new one)
3. **Go to:** Settings → API
4. **Copy:**
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **Anon/Public Key** (starts with `eyJ...`)

### 2. Set Environment Variables

```bash
# Windows PowerShell
$env:SUPABASE_URL = "https://your-project.supabase.co"
$env:SUPABASE_KEY = "your-anon-public-key"

# Linux/Mac
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-public-key"
```

Or create a `.env` file:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-public-key
```

### 3. Test Connection

```bash
python test_supabase_connection.py
```

---

## 📦 Features

### ✅ Database Operations (PostgREST)
- **Select** - Query data with filters
- **Insert** - Add new rows
- **Update** - Modify existing rows
- **Delete** - Remove rows
- **RPC** - Call PostgreSQL functions
- **Query Builder** - Fluent API for complex queries

### ✅ Authentication
- **Sign Up** - Register new users
- **Sign In** - Email/password authentication
- **Sign Out** - Revoke tokens
- **Get User** - Fetch user details

### ✅ Storage (File Management)
- **Upload** - Upload files to buckets
- **Download** - Download files
- **List** - List files in bucket
- **Delete** - Remove files
- **Public URLs** - Get public file URLs

### ✅ Utilities
- **Health Check** - Verify connectivity
- **CLI Interface** - Command-line operations

---

## 💻 Usage Examples

### Python API

#### Connect to Supabase
```python
from supabase_client import SupabaseClient

client = SupabaseClient(
    url="https://your-project.supabase.co",
    key="your-anon-key"
)

# Or use environment variables
client = SupabaseClient()  # Auto-loads from SUPABASE_URL and SUPABASE_KEY
```

#### Query Data
```python
# Select all users
users = client.select('users')

# Select with filters
active_users = client.select('users', filters={'status': 'active'})

# Using query builder
users = client.query('users') \
    .select('id, name, email') \
    .eq('status', 'active') \
    .order('created_at', ascending=False) \
    .limit(10) \
    .execute()
```

#### Insert Data
```python
# Insert single row
new_user = client.insert('users', {
    'name': 'John Doe',
    'email': 'john@example.com',
    'status': 'active'
})

# Insert multiple rows
new_users = client.insert('users', [
    {'name': 'Alice', 'email': 'alice@example.com'},
    {'name': 'Bob', 'email': 'bob@example.com'}
])
```

#### Update Data
```python
# Update rows
updated = client.update(
    'users',
    {'status': 'inactive'},
    filters={'id': 123}
)
```

#### Delete Data
```python
# Delete rows
deleted = client.delete('users', filters={'id': 123})
```

#### Call Database Functions
```python
# Call PostgreSQL function
result = client.rpc('calculate_total', {
    'user_id': 123,
    'month': 10
})
```

#### Authentication
```python
# Sign up new user
auth = client.sign_up('user@example.com', 'password123', {
    'full_name': 'John Doe'
})

# Sign in
session = client.sign_in('user@example.com', 'password123')
access_token = session['access_token']

# Get user info
user = client.get_user(access_token)

# Sign out
client.sign_out(access_token)
```

#### File Storage
```python
# Upload file
result = client.upload_file(
    bucket='avatars',
    path='user123/profile.jpg',
    file_path='/local/path/image.jpg',
    content_type='image/jpeg'
)

# Download file
content = client.download_file(
    bucket='avatars',
    path='user123/profile.jpg',
    output_path='/local/save/image.jpg'
)

# List files
files = client.list_files('avatars', path='user123/')

# Get public URL
url = client.get_public_url('avatars', 'user123/profile.jpg')
print(f"Public URL: {url}")

# Delete file
client.delete_file('avatars', 'user123/profile.jpg')
```

### Command Line Interface

```bash
# Check connectivity
python supabase_client.py health

# List all rows
python supabase_client.py list users

# Select specific columns
python supabase_client.py select users "id,name,email"

# Insert data
python supabase_client.py insert users '{"name":"John","email":"john@example.com"}'

# Call database function
python supabase_client.py rpc my_function '{"param1":"value1"}'

# Authentication
python supabase_client.py auth-signup user@example.com password123
python supabase_client.py auth-signin user@example.com password123

# Storage
python supabase_client.py storage-list avatars
python supabase_client.py storage-upload avatars user1/photo.jpg /path/to/photo.jpg
python supabase_client.py storage-download avatars user1/photo.jpg ./downloaded.jpg
```

---

## 🏗️ Setup Your Database

### Create a Test Table

Go to Supabase Dashboard → SQL Editor and run:

```sql
-- Create test table
CREATE TABLE test_table (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Enable Row Level Security (RLS)
ALTER TABLE test_table ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (for testing)
CREATE POLICY "Allow all operations" ON test_table
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Insert test data
INSERT INTO test_table (name, email) VALUES
    ('Alice Johnson', 'alice@example.com'),
    ('Bob Smith', 'bob@example.com'),
    ('Charlie Brown', 'charlie@example.com');
```

### Create a Storage Bucket

1. Go to: Storage → Create Bucket
2. Name: `test-files` or `avatars`
3. Set to **Public** if you want public URLs
4. Click **Create Bucket**

---

## 🔐 Security Notes

### Anon Key vs Service Key

- **Anon/Public Key:** For client-side operations, respects Row Level Security (RLS)
- **Service Key:** For server-side admin operations, bypasses RLS (**use carefully!**)

### Row Level Security (RLS)

Always enable RLS on your tables:

```sql
ALTER TABLE your_table ENABLE ROW LEVEL SECURITY;

-- Example: Users can only read their own data
CREATE POLICY "Users can read own data" ON your_table
    FOR SELECT
    USING (auth.uid() = user_id);
```

### Environment Variables

**Never commit API keys to git!** Use `.gitignore`:

```gitignore
.env
*.env
.env.local
```

---

## 🛠️ Troubleshooting

### "Table does not exist"
- Create the table in Supabase Dashboard → SQL Editor
- Ensure table name matches exactly (case-sensitive)

### "Permission denied"
- Enable Row Level Security policies
- Check if anon key has required permissions
- Use service key for admin operations (set `SUPABASE_SERVICE_KEY`)

### "Invalid API key"
- Verify `SUPABASE_KEY` is correct
- Get fresh key from Settings → API
- Ensure using correct project URL

### "Connection timeout"
- Check internet connectivity
- Verify project URL is correct
- Check if Supabase project is paused (free tier)

---

## 📖 Additional Resources

### Supabase Documentation
- **Official Docs:** https://supabase.com/docs
- **API Reference:** https://supabase.com/docs/reference
- **SQL Editor:** https://supabase.com/docs/guides/database

### Python Client
- **Official Python Client:** https://github.com/supabase-community/supabase-py
- **PostgREST API:** https://postgrest.org/en/stable/

### Examples
- See `test_supabase_connection.py` for working examples
- Check Supabase Dashboard → API docs for your project's specific endpoints

---

## 📊 Status

- **Client:** ✅ Complete and functional
- **Database Operations:** ✅ All operations supported
- **Authentication:** ✅ Sign up, sign in, sign out
- **Storage:** ✅ Upload, download, list, delete
- **CLI:** ✅ Command-line interface available
- **Testing:** ✅ Test script included

**Last Updated:** October 23, 2025

---

## 🔗 Quick Links

- **Supabase Dashboard:** https://supabase.com/dashboard
- **Project Settings:** https://supabase.com/dashboard/project/_/settings/api
- **SQL Editor:** https://supabase.com/dashboard/project/_/sql
- **Storage:** https://supabase.com/dashboard/project/_/storage

---

**Built for AI Agents Backend Integration**
