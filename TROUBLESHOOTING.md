# Troubleshooting Guide

This guide helps resolve common issues when deploying or running the Paimon Cloud Storage Server.

## Build/Installation Issues

### Python 3.13+ Metadata Preparation Error

**Error Message:**
```
Preparing metadata (pyproject.toml): finished with status 'error'
error: subprocess-exited-with-error
...
Running `maturin pep517 write-dist-info ...`
error: failed to create directory `/usr/local/cargo/registry/cache/...`
Caused by: Read-only file system (os error 30)
```

**Root Causes:**
1. **Pydantic Compatibility**: Older versions of pydantic (< 2.8.0) and pydantic-core (< 2.18.3) don't have pre-built wheels for Python 3.13, requiring Rust compilation which fails in read-only environments.
2. **Pathlib Backport**: The `mega.py` package depends on `pathlib==1.0.1`, which is an unmaintained backport that conflicts with the Python standard library on Python 3.13+.

**Solution:**
The requirements have been updated to use pydantic 2.10.4+ which includes pre-built wheels for Python 3.13. Additionally, use the provided `constraints.txt` file when installing dependencies:

```bash
pip install --constraint constraints.txt -r requirements.txt
```

The constraints file prevents installation of the pathlib backport, allowing pip to use the standard library version instead.

**Verification:**
Run the included test script to verify pathlib is from the standard library:
```bash
python test_pathlib.py
```

Expected output:
```
✅ PASSED: pathlib is from the Python standard library
```

### Render Deployment Failure

**Issue:**
Build fails on Render with Python 3.13 due to pathlib dependency conflict.

**Solution:**
The repository includes a `render.yaml` configuration file that:
1. Specifies Python 3.12.3 (more stable for this application)
2. Uses the constraints file during installation
3. Configures proper health checks

**Manual Configuration (if not using render.yaml):**
- **Build Command:** `pip install --constraint constraints.txt -r requirements.txt`
- **Python Version:** 3.12.3 or 3.11.x
- **Start Command:** `gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:$PORT`

### Render ModuleNotFoundError: No module named 'your_application'

**Error Message:**
```
==> Running 'gunicorn your_application.wsgi'
...
ModuleNotFoundError: No module named 'your_application'
```

**Root Cause:**
This error occurs when Render is using a cached or default configuration instead of the `render.yaml` file. The command `gunicorn your_application.wsgi` is a placeholder/template that should be replaced with the actual application command.

**Solutions:**

**1. For Existing Services (Most Common):**
If you created the Render service before the `render.yaml` file was added, you need to manually update the Start Command in the Render dashboard:

1. Go to your Render Dashboard
2. Select your service
3. Go to "Settings"
4. Under "Build & Deploy", update the **Start Command** to:
   ```
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:$PORT
   ```
5. Save changes and trigger a manual deploy

**2. For New Deployments:**
If you're creating a new service, ensure the `render.yaml` file is present in your repository root before connecting to Render. Render will automatically detect and use it.

**3. Verify render.yaml Configuration:**
Ensure your `render.yaml` file has the correct structure:
```yaml
services:
  - type: web
    name: paimon-server
    env: python
    plan: free
    region: oregon
    buildCommand: pip install --constraint constraints.txt -r requirements.txt
    startCommand: gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:$PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.3
      - key: AUTH_TOKEN
        sync: false
      - key: MEGA_EMAIL
        sync: false
      - key: MEGA_PASSWORD
        sync: false
    healthCheckPath: /ping
```

**Important Notes:**
- Use `env: python` (not `runtime: python`)
- The start command must reference `server:app` (the FastAPI application object in server.py)
- Do not use `python server.py` for production deployments on Render; always use gunicorn with uvicorn workers

### Docker Build Issues

**Issue:**
Docker build fails with similar pathlib/maturin errors.

**Solution:**
The Dockerfile has been updated to:
1. Use Python 3.11-slim base image
2. Include constraints.txt during build
3. Use the constraints file when installing dependencies

Rebuild your Docker image:
```bash
docker build -t paimon-server .
```

## Runtime Issues

### MEGA Upload Failures (asyncio.coroutine AttributeError)

**Error Message:**
```
AttributeError: module 'asyncio' has no attribute 'coroutine'
```

**Root Cause:**
The `tenacity` dependency used by `mega.py` has compatibility issues with asyncio changes in Python 3.12+. The `asyncio.coroutine` decorator was removed in Python 3.11.

**Workaround:**
1. Server will start and health endpoints will work
2. Only MEGA upload functionality is affected
3. Consider using Python 3.11 until mega.py updates its dependencies

**Alternative:**
Wait for `mega.py` to update its `tenacity` dependency, or contribute a fix to the mega.py project.

### Missing Environment Variables

**Error:**
Authentication failures or configuration errors at startup.

**Solution:**
Ensure all required environment variables are set:
```bash
AUTH_TOKEN=your-secret-token
MEGA_EMAIL=your-mega-email@example.com
MEGA_PASSWORD=your-mega-password
```

Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
nano .env
```

### Port Already in Use

**Error:**
```
OSError: [Errno 98] Address already in use
```

**Solution:**
Another process is using port 8080. Either:
1. Stop the other process: `lsof -ti:8080 | xargs kill`
2. Use a different port by setting the `PORT` environment variable

### Permission Denied for temp_uploads

**Error:**
```
PermissionError: [Errno 13] Permission denied: 'temp_uploads'
```

**Solution:**
Create the directory with proper permissions:
```bash
mkdir -p temp_uploads
chmod 755 temp_uploads
```

## Testing Issues

### Tests Fail to Import Modules

**Issue:**
Test suite cannot find server modules.

**Solution:**
Ensure you've installed dependencies:
```bash
pip install --constraint constraints.txt -r requirements.txt
```

Run tests from the project root:
```bash
python test_server.py
```

## Performance Issues

### Slow File Uploads

**Possible Causes:**
1. Network bandwidth limitations
2. Large file size
3. MEGA API rate limiting

**Solutions:**
1. Check your internet connection speed
2. Consider implementing file size limits
3. Add retry logic for transient failures (already implemented via tenacity)

### High Memory Usage

**Solutions:**
1. Reduce number of uvicorn workers
2. Implement file size limits in the application
3. Use streaming uploads for large files (current implementation uses temporary files)

## Getting Help

If you encounter issues not covered in this guide:

1. Check the [Known Issues](README.md#-known-issues) section in README.md
2. Review [DEPLOYMENT.md](DEPLOYMENT.md) for deployment-specific guidance
3. Open an issue on GitHub with:
   - Python version (`python --version`)
   - Operating system
   - Full error message
   - Steps to reproduce

## Quick Verification Commands

Run these commands to verify your setup:

```bash
# Check Python version
python --version

# Verify pathlib is from stdlib
python test_pathlib.py

# Check dependencies are installed
pip list | grep -E "(fastapi|uvicorn|mega\.py)"

# Test server starts
python server.py &
sleep 2
curl http://localhost:8080/ping
kill %1

# Run test suite
python test_server.py
```
