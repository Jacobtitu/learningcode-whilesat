#!/bin/bash

# Simple script to extract images from PDFs in bulk-import folder
# Usage: Just drag PDF files into bulk-import/ folder, then run this script

echo "🔍 Looking for PDF files in bulk-import folder..."

# Find all PDF files
pdf_files=$(find bulk-import -name "*.pdf" -type f)

if [ -z "$pdf_files" ]; then
    echo "❌ No PDF files found in bulk-import folder"
    echo ""
    echo "💡 To use this:"
    echo "   1. Drag your PDF files into the bulk-import/ folder"
    echo "   2. Run this script again"
    exit 1
fi

echo "📄 Found PDF files:"
echo "$pdf_files"
echo ""

# Check if PyMuPDF is installed
if ! python3 -c "import fitz" 2>/dev/null; then
    echo "⚠️  PyMuPDF not installed"
    echo ""
    echo "📦 Installing PyMuPDF..."
    pip3 install PyMuPDF
    echo ""
fi

# Extract images from each PDF
for pdf in $pdf_files; do
    echo "📄 Processing: $pdf"
    python3 bulk-import/extract-images-from-pdf.py "$pdf" bulk-import/images
done

echo ""
echo "✅ Done! Check bulk-import/images/ for extracted images"
echo "💡 Tip: Rename images to match your questions (e.g., q2-graph.png)"

