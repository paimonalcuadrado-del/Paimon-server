# Deployment Guide

## Quick Start with Docker (Recommended)

### Create a Dockerfile:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "server.py"]
```

### Build and run:
```bash
docker build -t paimon-server .
docker run -p 8080:8080 --env-file .env paimon-server
```

## Manual Deployment

### 1. Prerequisites
- Python 3.8+ (Python 3.13+ requires using the provided `constraints.txt` file)
- pip package manager
- Virtual environment (recommended)

**Note for Python 3.13+:** The `mega.py` dependency includes `pathlib==1.0.1` which conflicts with the standard library. Use the provided `constraints.txt` file during installation to prevent this issue.

### 2. Setup
```bash
# Clone repository
git clone https://github.com/paimonalcuadrado-del/Paimon-server.git
cd Paimon-server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --constraint constraints.txt -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with your credentials
```

### 3. Configuration
Edit `.env` file with your settings:
```env
AUTH_TOKEN=your-strong-secret-token-here
MEGA_EMAIL=your-mega-email@example.com
MEGA_PASSWORD=your-mega-password
HOST=0.0.0.0
PORT=8080
TEMP_UPLOAD_DIR=temp_uploads
LOG_LEVEL=INFO
```

### 4. Run the Server

#### Development Mode:
```bash
python server.py
```

#### Production Mode with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:8080
```

#### As a systemd service (Linux):
Create `/etc/systemd/system/paimon-server.service`:
```ini
[Unit]
Description=Paimon Cloud Storage Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/Paimon-server
Environment="PATH=/path/to/Paimon-server/venv/bin"
ExecStart=/path/to/Paimon-server/venv/bin/python server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable paimon-server
sudo systemctl start paimon-server
sudo systemctl status paimon-server
```

## Cloud Deployment

### Render
The project includes a `render.yaml` configuration file for easy deployment.

**Option 1: Using render.yaml (Recommended)**
1. Connect your GitHub repository to Render
2. Render will automatically detect the `render.yaml` file
3. Set the environment variables in Render dashboard:
   - `AUTH_TOKEN`
   - `MEGA_EMAIL`
   - `MEGA_PASSWORD`
4. Deploy

**Option 2: Manual Configuration**
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure:
   - **Environment:** Python 3
   - **Build Command:** `pip install --constraint constraints.txt -r requirements.txt`
   - **Start Command:** `gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:$PORT`
4. Set environment variables as above
5. Deploy

**Important Notes:**
- Always use the `constraints.txt` file during installation to avoid dependency conflicts, especially on newer Python versions.
- If you have an existing Render service that was created before `render.yaml` was added, you may need to manually update the Start Command in the Render dashboard to: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:$PORT`
- For new deployments, Render will automatically use the `render.yaml` configuration.

### AWS EC2
1. Launch an EC2 instance (Amazon Linux 2 or Ubuntu)
2. Install Python 3.11 or 3.12
3. Follow manual deployment steps
4. Configure security group to allow inbound traffic on port 8080
5. (Optional) Set up Nginx as reverse proxy

### Heroku
```bash
# Create Procfile
echo "web: uvicorn server:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
heroku create paimon-server
heroku config:set AUTH_TOKEN=your-token
heroku config:set MEGA_EMAIL=your-email
heroku config:set MEGA_PASSWORD=your-password
git push heroku main
```

### DigitalOcean App Platform
1. Connect your GitHub repository
2. Set environment variables in dashboard
3. Deploy with one click

## Reverse Proxy Setup (Nginx)

### Nginx configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeout for large file uploads
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
        send_timeout 600;
        
        # Increase max body size for file uploads
        client_max_body_size 100M;
    }
}
```

### Enable HTTPS with Let's Encrypt:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Performance Tuning

### For high-traffic deployments:
```bash
# Run with multiple workers
uvicorn server:app --host 0.0.0.0 --port 8080 --workers 4

# Or with Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:8080
```

### Optimize temp directory:
- Use SSD storage for `temp_uploads`
- Mount tmpfs for temporary files (RAM disk)
```bash
sudo mount -t tmpfs -o size=2G tmpfs /path/to/temp_uploads
```

## Monitoring

### Log files:
- Application logs: stdout/stderr
- Access logs: Nginx/proxy logs
- System logs: systemd journal (`journalctl -u paimon-server`)

### Health checks:
```bash
# Simple health check
curl http://localhost:8080/status

# Monitoring with uptime check services
# Use /ping or /status endpoints
```

## Security Best Practices

1. **Use strong authentication tokens**
   - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

2. **Enable HTTPS** in production
   - Use Let's Encrypt or cloud provider SSL

3. **Firewall rules**
   - Only expose necessary ports
   - Use security groups/firewall rules

4. **Regular updates**
   - Keep dependencies updated: `pip install --upgrade -r requirements.txt`
   - Monitor for security advisories

5. **Environment variables**
   - Never commit `.env` to version control
   - Use secret management services in production

## Troubleshooting

### Server won't start:
```bash
# Check if port is in use
netstat -tulpn | grep 8080

# Check Python version
python --version  # Should be 3.8-3.11

# Verify dependencies
pip list
```

### MEGA uploads failing:
- Verify MEGA credentials in `.env`
- Check MEGA account is active
- Ensure Python version is 3.11 or earlier

### High memory usage:
- Reduce number of workers
- Implement file size limits
- Use streaming uploads for large files

## Backup and Recovery

### Backup configuration:
```bash
# Backup .env file securely
cp .env .env.backup

# Backup entire directory
tar -czf paimon-server-backup.tar.gz /path/to/Paimon-server
```

### Database backup (if implemented):
```bash
# Add database backup commands here when implemented
```

## Scaling

For high-traffic scenarios:
1. Use load balancer (Nginx, HAProxy, AWS ELB)
2. Deploy multiple instances
3. Use shared storage for temp files (NFS, S3)
4. Implement caching (Redis)
5. Use CDN for static content
