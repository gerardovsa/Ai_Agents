# Flask Application Deployment Guide

This example shows how to deploy a Flask application to Render.com.

## Files in This Example

- `render.yaml` - Render configuration file with extensive inline comments
- `README.md` - This file

## Quick Start

1. **Copy configuration to your project:**
   ```bash
   cp render.yaml /path/to/your/flask/project/
   ```

2. **Customize render.yaml:**
   - Change `name` to your app name
   - Update `region` (oregon, singapore, frankfurt, ohio)
   - Add your environment variables

3. **Ensure requirements.txt includes:**
   ```
   flask>=2.3.0
   gunicorn==21.2.0
   python-dotenv
   ```

4. **Deploy:**
   ```bash
   # Via CLI
   python render_universal_cli.py blueprint deploy render.yaml
   
   # OR via dashboard
   # Commit render.yaml, push to GitHub
   # Connect repo at https://dashboard.render.com/select-repo
   ```

## Flask App Requirements

### 1. Correct Port Binding

Your Flask app must bind to `0.0.0.0` and use the `PORT` environment variable:

```python
import os
from flask import Flask

app = Flask(__name__)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
```

Or let Gunicorn handle it (recommended):
```yaml
startCommand: gunicorn app:app --bind 0.0.0.0:$PORT
```

### 2. Health Check Endpoint

Create a `/health` endpoint:

```python
from datetime import datetime
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'my-flask-app'
    }), 200
```

### 3. Environment Variables

Use environment variables for configuration:

```python
import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///dev.db')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    REDIS_URL = os.getenv('REDIS_URL')

app.config.from_object(Config)
```

### 4. Database Configuration

For PostgreSQL:

```python
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql://localhost/mydb'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
```

Add to requirements.txt:
```
psycopg2-binary==2.9.9
flask-sqlalchemy==3.1.1
```

## Common Patterns

### API with CORS

```python
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

# Configure CORS
allowed_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
CORS(app, origins=allowed_origins)

@app.route('/api/data')
def get_data():
    return {'message': 'Hello from Flask API'}
```

Add to requirements.txt:
```
flask-cors==4.0.0
```

### With Redis Caching

```python
import os
import redis
from flask import Flask

app = Flask(__name__)

# Configure Redis
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
redis_client = redis.from_url(redis_url)

@app.route('/cached-data')
def cached_data():
    # Try to get from cache
    cached = redis_client.get('my_data')
    if cached:
        return cached
    
    # If not in cache, compute and cache
    data = compute_expensive_data()
    redis_client.setex('my_data', 3600, data)  # Cache for 1 hour
    return data
```

### With Background Tasks (Celery)

```python
from celery import Celery
import os

app = Flask(__name__)

# Configure Celery
app.config['CELERY_BROKER_URL'] = os.getenv('REDIS_URL')
app.config['CELERY_RESULT_BACKEND'] = os.getenv('REDIS_URL')

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@celery.task
def process_data(data_id):
    # Long-running task
    pass

@app.route('/process', methods=['POST'])
def process():
    task = process_data.delay(request.json['data_id'])
    return {'task_id': task.id}
```

## Troubleshooting

### Build Fails

1. **Check requirements.txt:**
   ```bash
   pip install -r requirements.txt  # Test locally
   ```

2. **Common missing packages:**
   - `gunicorn` - Always required
   - `psycopg2-binary` - For PostgreSQL
   - `redis` - For Redis

### App Won't Start

1. **Check logs:**
   ```bash
   python render_universal_cli.py logs tail <service-id>
   ```

2. **Verify port binding:**
   - Must use `0.0.0.0`, not `localhost`
   - Must use `$PORT` environment variable

3. **Check startCommand:**
   - Should be: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - If your app instance is named differently, adjust accordingly

### 502 Bad Gateway

1. **App might be taking too long to start:**
   - Optimize imports
   - Move heavy initialization to after server starts

2. **App might be crashing on startup:**
   - Check logs for Python exceptions
   - Test locally with same Python version

### Database Connection Issues

1. **Verify DATABASE_URL is set:**
   ```bash
   python render_universal_cli.py env list <service-id>
   ```

2. **Use correct format:**
   ```
   postgresql://user:password@host:5432/database
   ```

3. **Add connection pooling:**
   ```python
   from sqlalchemy.pool import QueuePool
   
   app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
       'poolclass': QueuePool,
       'pool_size': 10,
       'pool_recycle': 3600,
       'pool_pre_ping': True
   }
   ```

## Performance Optimization

### 1. Use Gunicorn Workers

```yaml
startCommand: gunicorn app:app --bind 0.0.0.0:$PORT --workers 4 --threads 2
```

Workers calculation: `(2 × CPU cores) + 1`

### 2. Enable Connection Pooling

For databases and Redis connections, always use pooling.

### 3. Use Caching

Cache expensive operations:
- Database queries
- API responses
- Rendered templates

### 4. Optimize Static Files

For production, serve static files via CDN:
- Upload to S3/CloudFront
- Or use Flask-Assets with compression

### 5. Monitor Performance

```bash
python render_universal_cli.py metrics all <service-id>
```

## Next Steps

1. **Add environment variables:**
   ```bash
   python render_universal_cli.py env upload <service-id> .env.production
   ```

2. **Set up custom domain:**
   - Add domain in Render dashboard
   - Update DNS records
   - SSL certificate auto-provisioned

3. **Enable monitoring:**
   - Set up Sentry for error tracking
   - Use New Relic or DataDog for APM

4. **Set up CI/CD:**
   - GitHub Actions for automated testing
   - Automatic deploy on merge to main

## Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Render Flask Guide](https://render.com/docs/deploy-flask)
- [Flask Best Practices](https://flask.palletsprojects.com/en/latest/deploying/)
