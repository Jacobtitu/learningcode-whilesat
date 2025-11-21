#!/bin/bash

# Simple script to start a local web server

echo "🚀 Starting local server..."
echo ""
echo "📝 Your app will be available at:"
echo "   http://localhost:8000"
echo ""
echo "💡 Press Ctrl+C to stop the server"
echo ""

# Try using the custom server.py first
if [ -f "server.py" ] && command -v python3 &> /dev/null; then
    python3 server.py
# Fallback to Python 3 http.server
elif command -v python3 &> /dev/null; then
    python3 -m http.server 8000
# Fallback to Python 2
elif command -v python &> /dev/null; then
    python -m SimpleHTTPServer 8000
else
    echo "❌ Python not found. Please install Python to run a local server."
    exit 1
fi

