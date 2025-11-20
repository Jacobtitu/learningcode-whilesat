#!/bin/bash

# ONE-COMMAND PDF IMPORT
# Usage: ./import.sh your-pdf.pdf

echo "🚀 SAT Question Importer"
echo ""

# Check if PDF provided
if [ -z "$1" ]; then
    echo "❌ Please provide a PDF file"
    echo ""
    echo "Usage: ./import.sh your-pdf.pdf"
    echo ""
    echo "Example:"
    echo "  ./import.sh 202503asiav1.pdf"
    exit 1
fi

# Check if PyMuPDF is installed
if ! python3 -c "import fitz" 2>/dev/null; then
    echo "📦 Installing PyMuPDF (required for PDF processing)..."
    pip3 install PyMuPDF
fi

# Run the importer
cd "$(dirname "$0")/.."
python3 bulk-import/auto-import-pdf.py "$1"

echo ""
echo "✅ Done! Your questions are ready."
echo ""
echo "Next steps:"
echo "  1. Open http://localhost:8000/dynamic-questions.html"
echo "  2. Select 'Math Module 1' to see your questions"
echo "  3. Review and add correct answers + explanations"

