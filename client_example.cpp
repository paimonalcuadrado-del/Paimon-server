/**
 * Example C++ client using libcurl to interact with Paimon Cloud Storage Server
 * Compile with: g++ -o client client_example.cpp -lcurl
 */

#include <curl/curl.h>
#include <iostream>
#include <string>

// Callback function for receiving response data
size_t WriteCallback(void* contents, size_t size, size_t nmemb, std::string* userp) {
    size_t totalSize = size * nmemb;
    userp->append((char*)contents, totalSize);
    return totalSize;
}

// Test server connectivity with /ping endpoint
bool testPing(const std::string& serverUrl) {
    CURL* curl = curl_easy_init();
    if (!curl) {
        std::cerr << "Failed to initialize CURL" << std::endl;
        return false;
    }

    std::string response;
    std::string url = serverUrl + "/ping";

    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

    CURLcode res = curl_easy_perform(curl);
    curl_easy_cleanup(curl);

    if (res != CURLE_OK) {
        std::cerr << "Ping failed: " << curl_easy_strerror(res) << std::endl;
        return false;
    }

    std::cout << "Ping response: " << response << std::endl;
    return true;
}

// Upload a file to the server
bool uploadFile(const std::string& serverUrl, const std::string& authToken, 
                const std::string& filePath, const std::string& service = "mega") {
    CURL* curl = curl_easy_init();
    if (!curl) {
        std::cerr << "Failed to initialize CURL" << std::endl;
        return false;
    }

    // Prepare the form data
    struct curl_httppost* formpost = NULL;
    struct curl_httppost* lastptr = NULL;

    // Add file to form
    curl_formadd(&formpost, &lastptr,
                 CURLFORM_COPYNAME, "file",
                 CURLFORM_FILE, filePath.c_str(),
                 CURLFORM_END);

    // Prepare authentication header
    struct curl_slist* headerlist = NULL;
    std::string authHeader = "X-Auth-Token: " + authToken;
    headerlist = curl_slist_append(headerlist, authHeader.c_str());

    // Prepare URL with service parameter
    std::string url = serverUrl + "/upload?service=" + service;

    // Response data
    std::string response;

    // Set curl options
    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headerlist);
    curl_easy_setopt(curl, CURLOPT_HTTPPOST, formpost);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

    // Perform the request
    CURLcode res = curl_easy_perform(curl);

    // Get HTTP response code
    long httpCode = 0;
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &httpCode);

    // Cleanup
    curl_easy_cleanup(curl);
    curl_formfree(formpost);
    curl_slist_free_all(headerlist);

    if (res != CURLE_OK) {
        std::cerr << "Upload failed: " << curl_easy_strerror(res) << std::endl;
        return false;
    }

    std::cout << "HTTP Status Code: " << httpCode << std::endl;
    std::cout << "Upload response: " << response << std::endl;

    return httpCode == 200;
}

int main(int argc, char* argv[]) {
    // Configuration
    std::string serverUrl = "http://localhost:8080";
    std::string authToken = "test-token-12345";
    
    if (argc < 2) {
        std::cout << "Usage: " << argv[0] << " <file_path>" << std::endl;
        std::cout << "       " << argv[0] << " ping" << std::endl;
        return 1;
    }

    std::string command = argv[1];

    // Initialize curl globally
    curl_global_init(CURL_GLOBAL_ALL);

    if (command == "ping") {
        // Test server connectivity
        if (testPing(serverUrl)) {
            std::cout << "Server is reachable!" << std::endl;
        } else {
            std::cout << "Server is not reachable!" << std::endl;
        }
    } else {
        // Upload file
        std::string filePath = command;
        std::cout << "Uploading file: " << filePath << std::endl;
        
        if (uploadFile(serverUrl, authToken, filePath)) {
            std::cout << "File uploaded successfully!" << std::endl;
        } else {
            std::cout << "File upload failed!" << std::endl;
        }
    }

    // Cleanup curl
    curl_global_cleanup();

    return 0;
}
