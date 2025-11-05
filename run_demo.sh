#!/bin/bash

# Demo script to show server capabilities
echo "==================================="
echo "Paimon Server Demo"
echo "==================================="

# Start server in background
echo "Starting server..."
python server.py > /tmp/server.log 2>&1 &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Run tests
echo -e "\n=== Testing Endpoints ==="

echo -e "\n1. Testing /ping endpoint:"
curl -s http://localhost:8080/ping | python -m json.tool

echo -e "\n2. Testing /status endpoint:"
curl -s http://localhost:8080/status | python -m json.tool

echo -e "\n3. Testing /upload without auth (should fail):"
echo "test" > /tmp/demo.txt
curl -s -X POST "http://localhost:8080/upload?service=mega" -F "file=@/tmp/demo.txt" | python -m json.tool

echo -e "\n4. Testing /upload with auth but invalid service:"
curl -s -X POST "http://localhost:8080/upload?service=dropbox" -H "X-Auth-Token: test-token-12345" -F "file=@/tmp/demo.txt" | python -m json.tool

echo -e "\n==================================="
echo "Demo completed!"
echo "==================================="

# Cleanup
kill $SERVER_PID 2>/dev/null
rm /tmp/demo.txt 2>/dev/null

exit 0
