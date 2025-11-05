#!/usr/bin/env python3
"""
Verify that all requirements from the problem statement are met
"""
import os
import sys
from pathlib import Path

def check_file_exists(filename, description):
    """Check if a file exists"""
    if Path(filename).exists():
        print(f"✓ {description}: {filename}")
        return True
    else:
        print(f"✗ MISSING {description}: {filename}")
        return False

def check_content_in_file(filename, content, description):
    """Check if content exists in file"""
    try:
        with open(filename, 'r') as f:
            file_content = f.read()
            if content in file_content:
                print(f"✓ {description}")
                return True
            else:
                print(f"✗ MISSING {description}")
                return False
    except FileNotFoundError:
        print(f"✗ File not found for check: {filename}")
        return False

print("=" * 70)
print("Requirements Verification")
print("=" * 70)

checks = []

# Core files
print("\n📁 Core Files:")
checks.append(check_file_exists("server.py", "Main server file"))
checks.append(check_file_exists("config.py", "Configuration management"))
checks.append(check_file_exists("requirements.txt", "Dependencies file"))
checks.append(check_file_exists(".env.example", "Environment example"))
checks.append(check_file_exists(".gitignore", "Git ignore file"))
checks.append(check_file_exists("README.md", "Documentation"))

# Service modules
print("\n📦 Service Modules:")
checks.append(check_file_exists("services/__init__.py", "Services package"))
checks.append(check_file_exists("services/mega.py", "MEGA service"))

# Testing and examples
print("\n🧪 Testing & Examples:")
checks.append(check_file_exists("test_server.py", "Test suite"))
checks.append(check_file_exists("client_example.cpp", "C++ client example"))
checks.append(check_file_exists("run_demo.sh", "Demo script"))

# Deployment
print("\n🚀 Deployment:")
checks.append(check_file_exists("Dockerfile", "Docker configuration"))
checks.append(check_file_exists("docker-compose.yml", "Docker Compose"))
checks.append(check_file_exists("DEPLOYMENT.md", "Deployment guide"))

# Check server.py content
print("\n🔍 Server Features:")
checks.append(check_content_in_file("server.py", "FastAPI", "Uses FastAPI"))
checks.append(check_content_in_file("server.py", "async", "Async/await support"))
checks.append(check_content_in_file("server.py", "aiofiles", "Async file operations"))
checks.append(check_content_in_file("server.py", "X-Auth-Token", "Authentication header"))
checks.append(check_content_in_file("server.py", "logging", "Logging support"))
checks.append(check_content_in_file("server.py", "asynccontextmanager", "Lifespan management"))

# Check endpoints
print("\n🌐 Required Endpoints:")
checks.append(check_content_in_file("server.py", '@app.get("/ping")', "/ping endpoint"))
checks.append(check_content_in_file("server.py", '@app.get("/status")', "/status endpoint"))
checks.append(check_content_in_file("server.py", '@app.post("/upload")', "/upload endpoint"))

# Check error handling
print("\n🛡️ Error Handling:")
checks.append(check_content_in_file("server.py", "HTTPException", "HTTP exception handling"))
checks.append(check_content_in_file("server.py", "exception_handler", "Global exception handler"))
checks.append(check_content_in_file("server.py", "try:", "Try-catch blocks"))

# Check MEGA service
print("\n☁️ MEGA Service:")
checks.append(check_content_in_file("services/mega.py", "class MegaService", "MEGA service class"))
checks.append(check_content_in_file("services/mega.py", "async def upload_file", "Async upload"))
checks.append(check_content_in_file("services/mega.py", "run_in_executor", "Thread pool execution"))

# Check cleanup
print("\n🧹 Cleanup:")
checks.append(check_content_in_file("server.py", "finally:", "Cleanup in finally block"))
checks.append(check_content_in_file("server.py", "os.unlink", "File deletion"))

# Check dependencies
print("\n📚 Dependencies:")
required_deps = [
    "fastapi",
    "uvicorn",
    "python-dotenv",
    "mega.py",
    "aiofiles",
    "python-multipart",
    "pydantic"
]
for dep in required_deps:
    checks.append(check_content_in_file("requirements.txt", dep, f"Dependency: {dep}"))

# Summary
print("\n" + "=" * 70)
total = len(checks)
passed = sum(checks)
failed = total - passed

print(f"Results: {passed}/{total} checks passed")
if failed > 0:
    print(f"❌ {failed} checks failed")
    sys.exit(1)
else:
    print("✅ All requirements verified!")
    sys.exit(0)
