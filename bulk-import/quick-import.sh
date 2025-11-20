#!/bin/bash
# 🚀 Quick SAT Test Import Script
# Drag your PDF here and answer a few questions!

echo "════════════════════════════════════════════════════════════════"
echo "🚀 QUICK SAT TEST IMPORTER"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Get PDF file
if [ -z "$1" ]; then
    echo "📁 Enter the path to your PDF file:"
    read PDF_FILE
else
    PDF_FILE="$1"
fi

# Check if file exists
if [ ! -f "$PDF_FILE" ]; then
    echo "❌ Error: File not found: $PDF_FILE"
    exit 1
fi

echo ""
echo "✅ PDF found: $PDF_FILE"
echo ""

# Get test information
echo "📝 Enter test name (e.g., '2025-03 Asia Test 1'):"
read TEST_NAME

echo ""
echo "📅 Enter date (e.g., 2025-03):"
read DATE

echo ""
echo "🌍 Enter region (e.g., Asia, USA, International):"
read REGION

echo ""
echo "🔢 Enter test number (e.g., 1, 2, 3):"
read TEST_NUM

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📊 IMPORTING TEST:"
echo "   Name: $TEST_NAME"
echo "   Date: $DATE"
echo "   Region: $REGION"
echo "   Test #: $TEST_NUM"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "⏳ Starting import... This will take ~5 minutes"
echo ""

# Run the fast importer
cd "$(dirname "$0")/.."
python3 bulk-import/fast-import.py "$PDF_FILE" "$TEST_NAME" "$DATE" "$REGION" "$TEST_NUM"

if [ $? -eq 0 ]; then
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "✅ IMPORT COMPLETE!"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo "🎉 Your test has been imported successfully!"
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Restart your local server (./start-server.sh)"
    echo "   2. Refresh your browser"
    echo "   3. Select your new test from the date picker"
    echo ""
else
    echo ""
    echo "❌ Import failed. Check the error messages above."
fi

