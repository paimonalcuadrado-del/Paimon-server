# Paimon Cloud Storage Server

A fully optimized Python backend server that acts as an intermediary storage API between a C++ client (Geode mod) and multiple cloud storage providers (MEGA, Google Drive, Dropbox, etc.).

## 🚀 Features

- **FastAPI-powered** - Async/await support for high performance
- **Multiple cloud storage providers** - Currently supports MEGA, easily extensible for others
- **Secure authentication** - Custom header-based authentication (X-Auth-Token)
- **Efficient file handling** - Temporary storage with automatic cleanup
- **Robust error handling** - Comprehensive error handling and logging
- **Production-ready** - Structured, modular, and maintainable code
- **Health checks** - Built-in `/ping` and `/status` endpoints

## 📋 Requirements

- Python 3.8+
- MEGA account (for MEGA storage service)

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/paimonalcuadrado-del/Paimon-server.git
cd Paimon-server
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. Update `.env` file with your credentials:
```env
AUTH_TOKEN=your-secret-auth-token-here
MEGA_EMAIL=your-mega-email@example.com
MEGA_PASSWORD=your-mega-password
```

## 🏃 Running the Server

### Using uvicorn directly:
```bash
uvicorn server:app --host 0.0.0.0 --port 8080
```

### Using the Python script:
```bash
python server.py
```

The server will start on `http://0.0.0.0:8080`

## 📡 API Endpoints

### GET /ping
Simple connectivity test endpoint.

**Response:**
```json
{
  "message": "Server running"
}
```

### GET /status
Health check endpoint with server information.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "Paimon Cloud Storage API",
  "temp_dir": "temp_uploads",
  "supported_services": ["mega"]
}
```

### POST /upload
Upload a file to the specified cloud storage service.

**Headers:**
- `X-Auth-Token`: Your authentication token (required)

**Query Parameters:**
- `service`: Cloud storage service to use (default: "mega")

**Body:**
- `file`: File to upload (multipart/form-data)

**Example using curl:**
```bash
curl -X POST "http://localhost:8080/upload?service=mega" \
  -H "X-Auth-Token: your-secret-auth-token-here" \
  -F "file=@/path/to/your/file.txt"
```

**Example using C++ libcurl:**
```cpp
CURL *curl = curl_easy_init();
if(curl) {
    struct curl_httppost *formpost = NULL;
    struct curl_httppost *lastptr = NULL;
    struct curl_slist *headerlist = NULL;
    
    // Add authentication header
    headerlist = curl_slist_append(headerlist, "X-Auth-Token: your-secret-auth-token-here");
    
    // Add file to form
    curl_formadd(&formpost, &lastptr,
                 CURLFORM_COPYNAME, "file",
                 CURLFORM_FILE, "/path/to/file.txt",
                 CURLFORM_END);
    
    curl_easy_setopt(curl, CURLOPT_URL, "http://localhost:8080/upload?service=mega");
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headerlist);
    curl_easy_setopt(curl, CURLOPT_HTTPPOST, formpost);
    
    CURLcode res = curl_easy_perform(curl);
    
    curl_easy_cleanup(curl);
    curl_formfree(formpost);
    curl_slist_free_all(headerlist);
}
```

**Success Response:**
```json
{
  "status": "success",
  "message": "File uploaded successfully",
  "filename": "file.txt",
  "service": "mega",
  "link": "https://mega.nz/file/xxxxx"
}
```

**Error Response:**
```json
{
  "detail": "Error message"
}
```

## 🏗️ Project Structure

```
Paimon-server/
├── server.py              # Main FastAPI application
├── config.py              # Configuration management
├── services/              # Cloud storage service modules
│   ├── __init__.py
│   └── mega.py           # MEGA service implementation
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🔐 Security

- Authentication is required for all upload operations via `X-Auth-Token` header
- Temporary files are automatically cleaned up after upload
- Credentials are stored in environment variables (never commit `.env` to git)
- Input validation on all endpoints

## 🛠️ Adding New Storage Services

To add a new storage provider:

1. Create a new service file in `services/` (e.g., `services/googledrive.py`)
2. Implement the service class with an `upload_file` async method
3. Update the `server.py` to handle the new service in the `/upload` endpoint
4. Add required credentials to `.env.example` and `config.py`

Example service structure:
```python
class NewStorageService:
    async def upload_file(self, file_path: str) -> Optional[str]:
        # Upload logic here
        return file_link
```

## 📝 Logging

The server logs all important operations:
- Upload start and completion
- Authentication failures
- Upload errors
- File cleanup operations

Log level can be configured in `.env`:
```env
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 🧪 Testing

### Run the test suite:
```bash
python test_server.py
```

This will test all endpoints including:
- `/ping` - Connectivity test
- `/status` - Health check
- `/upload` - File upload with various scenarios (auth, validation, etc.)

### Manual testing with curl:

Test the server with curl:

```bash
# Test ping endpoint
curl http://localhost:8080/ping

# Test status endpoint
curl http://localhost:8080/status

# Test file upload
curl -X POST "http://localhost:8080/upload?service=mega" \
  -H "X-Auth-Token: your-secret-auth-token-here" \
  -F "file=@test.txt"
```

### C++ Client Example

A complete C++ client example is provided in `client_example.cpp`. Compile and use it:

```bash
# Compile
g++ -o client client_example.cpp -lcurl

# Test connectivity
./client ping

# Upload a file
./client /path/to/file.txt
```

## 📦 Dependencies

- **fastapi** - Modern, fast web framework
- **uvicorn** - ASGI server
- **python-dotenv** - Environment variable management
- **mega.py** - MEGA cloud storage client
- **aiofiles** - Async file operations
- **python-multipart** - Multipart form data parsing
- **pydantic** - Data validation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 👥 Authors

- paimonalcuadrado-del

## 🐛 Known Issues

### MEGA.py Compatibility (Python 3.12+)
If you encounter an `AttributeError: module 'asyncio' has no attribute 'coroutine'` error when using Python 3.12+, this is due to a compatibility issue with the `tenacity` dependency of `mega.py`. 

**Workaround:**
1. The server will still start and all endpoints will work
2. MEGA uploads will fail until the dependency is updated
3. To fix: Wait for `mega.py` to update its `tenacity` dependency, or use Python 3.11 or earlier

The server is designed to handle this gracefully and will log warnings about MEGA not being available.

## 🗺️ Roadmap

- [ ] Add Google Drive support
- [ ] Add Dropbox support
- [ ] Add OneDrive support
- [ ] Implement file download endpoint
- [ ] Add file metadata retrieval
- [ ] Implement rate limiting
- [ ] Add comprehensive test suite
- [ ] Add Docker support
