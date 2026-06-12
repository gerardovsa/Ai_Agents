# Platform Credential Auto-Registration System

## 🎯 Overview

This system automatically detects new platforms from tool schemas and manages their credentials in the `user_platform_credentials` table.

---

## 📦 Table Structure (After Migration)

```sql
CREATE TABLE ai_infrastructure.user_platform_credentials (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  platform TEXT NOT NULL,              -- 'pinecone', 'voyager', 'stripe', etc.
  credentials JSONB NOT NULL,          -- All credentials in one JSON object
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  metadata JSONB,                      -- Additional platform-specific metadata
  UNIQUE(user_id, platform)            -- One row per user per platform
);
```

### Key Changes from Original:
1. ✅ **JSONB credentials column** - All secrets in one JSON object
2. ✅ **SERIAL id** - Auto-increment (no manual ID management)
3. ✅ **UNIQUE constraint** - Prevents duplicate user+platform rows
4. ✅ **Auto-updated timestamps** - Trigger updates `updated_at` automatically
5. ✅ **GIN index on credentials** - Fast JSONB queries

---

## 🔄 How Platforms Auto-Register

### Step 1: Tool Schema Declaration

When creating a new tool, declare credential requirements in the schema:

**Example: `tools/schemas/stripe_tools.json`**
```json
{
  "platform": "stripe",
  "description": "Stripe payment processing API",
  "credentials_required": {
    "api_key": {
      "type": "secret_key",
      "display_name": "Secret Key",
      "description": "Stripe secret key (sk_live_... or sk_test_...)",
      "required": true,
      "pattern": "^sk_(test|live)_[A-Za-z0-9]{24,}$"
    },
    "publishable_key": {
      "type": "public_key",
      "display_name": "Publishable Key",
      "description": "Stripe publishable key (pk_live_... or pk_test_...)",
      "required": false,
      "pattern": "^pk_(test|live)_[A-Za-z0-9]{24,}$"
    },
    "webhook_secret": {
      "type": "webhook_secret",
      "display_name": "Webhook Secret",
      "description": "Webhook signing secret (whsec_...)",
      "required": false
    }
  },
  "metadata_schema": {
    "environment": {
      "type": "enum",
      "values": ["test", "live"],
      "default": "test"
    },
    "account_id": {
      "type": "string",
      "description": "Stripe account ID (optional)"
    }
  },
  "tools": [
    {
      "name": "stripe_create_customer",
      "description": "Create a new Stripe customer",
      ...
    }
  ]
}
```

### Step 2: Platform Discovery

The system auto-discovers platforms from schemas:

**`AI_infrastructure/core/platform_registry.py`** (Create this file)
```python
"""
Platform Registry - Auto-discovers platforms from tool schemas
"""
import json
from pathlib import Path
from typing import Dict, List, Optional

class PlatformRegistry:
    """Manages platform discovery and credential schemas"""
    
    def __init__(self):
        self.schemas_dir = Path(__file__).parent.parent.parent / 'tools' / 'schemas'
        self._platforms_cache = None
    
    def discover_platforms(self) -> List[str]:
        """
        Auto-discover all platforms from tool schemas
        
        Returns:
            List of platform names (e.g., ['pinecone', 'stripe', 'voyager'])
        """
        if self._platforms_cache:
            return self._platforms_cache
        
        platforms = set()
        for schema_file in self.schemas_dir.glob('*_tools.json'):
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema = json.load(f)
                    platform = schema.get('platform')
                    if platform:
                        platforms.add(platform)
            except Exception as e:
                print(f"⚠️  Error loading schema {schema_file.name}: {e}")
        
        self._platforms_cache = sorted(platforms)
        return self._platforms_cache
    
    def get_platform_schema(self, platform: str) -> Optional[Dict]:
        """
        Get full schema for a platform
        
        Args:
            platform: Platform name (e.g., 'pinecone')
        
        Returns:
            Schema dict or None if not found
        """
        schema_file = self.schemas_dir / f'{platform}_tools.json'
        if not schema_file.exists():
            return None
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_credentials_schema(self, platform: str) -> Dict:
        """
        Get credential requirements for platform
        
        Args:
            platform: Platform name
        
        Returns:
            Dict of credential requirements
        """
        schema = self.get_platform_schema(platform)
        if not schema:
            return {}
        
        return schema.get('credentials_required', {})
    
    def get_metadata_schema(self, platform: str) -> Dict:
        """
        Get metadata schema for platform
        
        Args:
            platform: Platform name
        
        Returns:
            Dict of metadata field definitions
        """
        schema = self.get_platform_schema(platform)
        if not schema:
            return {}
        
        return schema.get('metadata_schema', {})
    
    def validate_credentials(self, platform: str, credentials: Dict) -> tuple[bool, List[str]]:
        """
        Validate credentials against platform schema
        
        Args:
            platform: Platform name
            credentials: Credentials dict to validate
        
        Returns:
            (is_valid, error_messages)
        """
        schema = self.get_credentials_schema(platform)
        if not schema:
            return True, []  # No schema = no validation
        
        errors = []
        
        # Check required fields
        for field, config in schema.items():
            if config.get('required', False) and field not in credentials:
                errors.append(f"Missing required field: {field}")
        
        # Check patterns
        import re
        for field, value in credentials.items():
            if field in schema:
                pattern = schema[field].get('pattern')
                if pattern and not re.match(pattern, str(value)):
                    errors.append(f"Invalid format for {field}")
        
        return len(errors) == 0, errors
    
    def get_platform_display_info(self, platform: str) -> Dict:
        """
        Get display information for platform (for UI)
        
        Returns:
            Dict with name, description, icon, etc.
        """
        schema = self.get_platform_schema(platform)
        if not schema:
            return {
                'name': platform.title(),
                'description': f'{platform} platform integration'
            }
        
        return {
            'name': schema.get('display_name', platform.title()),
            'description': schema.get('description', ''),
            'icon': schema.get('icon', 'key'),
            'docs_url': schema.get('docs_url', '')
        }

# Global instance
platform_registry = PlatformRegistry()
```

### Step 3: Auto-Registration in UserAuthManager

Update `AI_infrastructure/auth/user_auth.py`:

```python
from core.platform_registry import platform_registry

class UserAuthManager:
    # ... existing code ...
    
    def save_platform_credentials(self, user_id: int, platform: str, 
                                  credentials: Dict, metadata: Dict = None) -> Dict:
        """
        Save credentials for a platform (auto-validates against schema)
        
        Args:
            user_id: User ID
            platform: Platform name (must exist in tool schemas)
            credentials: Dict of credentials (e.g., {'api_key': '...', 'secret': '...'})
            metadata: Optional metadata dict
        
        Returns:
            {'success': bool, 'error': str (optional)}
        """
        # Auto-validate against platform schema
        is_valid, errors = platform_registry.validate_credentials(platform, credentials)
        if not is_valid:
            return {'success': False, 'error': '; '.join(errors)}
        
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Check if exists
            cursor.execute("""
                SELECT id FROM ai_infrastructure.user_platform_credentials
                WHERE user_id = %s AND platform = %s
            """, (user_id, platform))
            
            existing = cursor.fetchone()
            
            credentials_json = json.dumps(credentials)
            metadata_json = json.dumps(metadata) if metadata else None
            
            if existing:
                # Update
                cursor.execute("""
                    UPDATE ai_infrastructure.user_platform_credentials
                    SET credentials = %s::jsonb,
                        metadata = %s::jsonb,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (credentials_json, metadata_json, existing[0]))
            else:
                # Insert (id auto-increments)
                cursor.execute("""
                    INSERT INTO ai_infrastructure.user_platform_credentials
                    (user_id, platform, credentials, metadata)
                    VALUES (%s, %s, %s::jsonb, %s::jsonb)
                """, (user_id, platform, credentials_json, metadata_json))
            
            conn.commit()
            conn.close()
            
            return {'success': True}
        
        except Exception as e:
            print(f"❌ Save credentials error: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_platform_credentials(self, user_id: int, platform: str) -> Optional[Dict]:
        """
        Get credentials for a platform
        
        Args:
            user_id: User ID
            platform: Platform name
        
        Returns:
            Credentials dict or None
        """
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT credentials 
            FROM ai_infrastructure.user_platform_credentials
            WHERE user_id = %s 
              AND platform = %s 
              AND is_active = TRUE
        """, (user_id, platform))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        # Return as dict (psycopg2 converts jsonb to dict automatically)
        return row[0] if isinstance(row[0], dict) else json.loads(row[0])
    
    def list_user_platforms(self, user_id: int) -> List[Dict]:
        """
        List all platforms with credentials for user
        
        Returns:
            List of dicts with platform, has_credentials, credential_count
        """
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        # Get platforms with credentials
        cursor.execute("""
            SELECT platform, credentials, metadata, created_at, updated_at
            FROM ai_infrastructure.user_platform_credentials
            WHERE user_id = %s AND is_active = TRUE
            ORDER BY platform
        """, (user_id,))
        
        user_platforms = []
        for row in cursor.fetchall():
            platform = row[0]
            credentials = row[1] if isinstance(row[1], dict) else json.loads(row[1])
            
            user_platforms.append({
                'platform': platform,
                'has_credentials': True,
                'credential_count': len(credentials),
                'credential_keys': list(credentials.keys()),
                'created_at': row[3],
                'updated_at': row[4],
                **platform_registry.get_platform_display_info(platform)
            })
        
        conn.close()
        return user_platforms
```

### Step 4: Flask API Routes

Create `AI_infrastructure/routes/platform_credentials_routes.py`:

```python
"""
Platform Credentials Routes - Generic credential management for all platforms
"""
from flask import Blueprint, request, jsonify
from auth.user_auth import UserAuthManager
from core.platform_registry import platform_registry

credentials_bp = Blueprint('platform_credentials', __name__)

@credentials_bp.route('/api/platforms/list', methods=['GET'])
def list_platforms():
    """List all available platforms from tool schemas"""
    try:
        platforms = platform_registry.discover_platforms()
        
        platform_info = []
        for platform in platforms:
            info = platform_registry.get_platform_display_info(platform)
            cred_schema = platform_registry.get_credentials_schema(platform)
            
            platform_info.append({
                'platform': platform,
                'required_credentials': list(cred_schema.keys()),
                **info
            })
        
        return jsonify({
            'success': True,
            'platforms': platform_info,
            'count': len(platforms)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@credentials_bp.route('/api/platforms/<platform>/schema', methods=['GET'])
def get_platform_schema(platform):
    """Get credential schema for a platform"""
    try:
        cred_schema = platform_registry.get_credentials_schema(platform)
        meta_schema = platform_registry.get_metadata_schema(platform)
        
        if not cred_schema:
            return jsonify({
                'success': False,
                'error': f'Platform {platform} not found'
            }), 404
        
        return jsonify({
            'success': True,
            'platform': platform,
            'credentials_schema': cred_schema,
            'metadata_schema': meta_schema
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@credentials_bp.route('/api/credentials/save', methods=['POST'])
def save_credentials():
    """Save credentials for any platform"""
    try:
        user_id = request.json.get('user_id', 1)
        platform = request.json.get('platform')
        credentials = request.json.get('credentials', {})
        metadata = request.json.get('metadata', {})
        
        if not platform or not credentials:
            return jsonify({
                'success': False,
                'error': 'Missing platform or credentials'
            }), 400
        
        auth_manager = UserAuthManager()
        result = auth_manager.save_platform_credentials(
            user_id, platform, credentials, metadata
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@credentials_bp.route('/api/credentials/<platform>', methods=['GET'])
def get_credentials(platform):
    """Get credentials for a platform"""
    try:
        user_id = request.args.get('user_id', 1, type=int)
        
        auth_manager = UserAuthManager()
        credentials = auth_manager.get_platform_credentials(user_id, platform)
        
        if credentials:
            # Mask sensitive values
            masked = {k: f"{'*' * 20}{v[-8:]}" if len(v) > 8 else "***" 
                     for k, v in credentials.items()}
            
            return jsonify({
                'success': True,
                'platform': platform,
                'credentials': masked,
                'has_credentials': True
            })
        else:
            return jsonify({
                'success': False,
                'has_credentials': False
            }), 404
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@credentials_bp.route('/api/credentials/user/<int:user_id>', methods=['GET'])
def list_user_credentials(user_id):
    """List all platforms with credentials for user"""
    try:
        auth_manager = UserAuthManager()
        platforms = auth_manager.list_user_platforms(user_id)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'platforms': platforms,
            'count': len(platforms)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

---

## 📝 Example Usage

### Adding a New Platform (Mailchimp)

**1. Create tool schema:**
```json
// tools/schemas/mailchimp_tools.json
{
  "platform": "mailchimp",
  "description": "Mailchimp email marketing API",
  "credentials_required": {
    "api_key": {
      "type": "api_key",
      "display_name": "API Key",
      "description": "Mailchimp API key from Account → Extras → API Keys",
      "required": true,
      "pattern": "^[a-f0-9]{32}-us[0-9]{1,2}$"
    },
    "server_prefix": {
      "type": "string",
      "display_name": "Server Prefix",
      "description": "Server prefix (e.g., 'us19' from API key)",
      "required": true
    }
  },
  "metadata_schema": {
    "account_name": {
      "type": "string"
    }
  },
  "tools": [...]
}
```

**2. Save credentials (auto-validated):**
```python
auth_manager = UserAuthManager()
result = auth_manager.save_platform_credentials(
    user_id=1,
    platform='mailchimp',
    credentials={
        'api_key': 'abc123...456-us19',
        'server_prefix': 'us19'
    },
    metadata={'account_name': 'MustCare Marketing'}
)
```

**3. Query credentials in tool:**
```python
def mailchimp_send_campaign(campaign_id, **kwargs):
    user_id = kwargs.get('_user_id')
    auth_manager = UserAuthManager()
    
    creds = auth_manager.get_platform_credentials(user_id, 'mailchimp')
    if not creds:
        raise Exception("Mailchimp credentials not found")
    
    api_key = creds['api_key']
    server_prefix = creds['server_prefix']
    
    # Use credentials...
```

---

## ✅ Summary

**Yes, create ONE universal credentials table with JSONB!**

### Benefits:
1. ✅ **Auto-discovery** - New platforms detected from schemas
2. ✅ **Schema validation** - Credentials validated before save
3. ✅ **One row per platform** - Simple, clean data model
4. ✅ **JSONB flexibility** - Any credential structure supported
5. ✅ **Fast queries** - GIN index on credentials JSONB
6. ✅ **Type safety** - Platform registry enforces schemas

### Migration Path:
1. Run `01_improve_credentials_table.sql` in Supabase
2. Create `platform_registry.py`
3. Update `user_auth.py` with new methods
4. Create `platform_credentials_routes.py`
5. Register blueprint in `flask_app.py`
6. Update tool implementations to use new pattern

Your existing Pinecone/Voyager/OpenAI credentials will be automatically migrated to the new JSONB format!
