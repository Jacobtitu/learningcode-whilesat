"""
Optional: Extract images from PDF automatically
Requires: pip install PyMuPDF (fitz)
"""

try:
    import fitz  # PyMuPDF
except ImportError:
    print("❌ PyMuPDF not installed. Install it with: pip install PyMuPDF")
    print("   Or just use screenshots instead (easier!)")
    exit(1)

import os
from pathlib import Path

def extract_images_from_pdf(pdf_path, output_folder):
    """
    Extract all images from a PDF file
    
    Usage:
        extract_images_from_pdf("path/to/file.pdf", "bulk-import/images")
    """
    # Create output folder if it doesn't exist
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    # Open PDF
    doc = fitz.open(pdf_path)
    
    pdf_name = Path(pdf_path).stem  # Get PDF name without extension
    
    print(f"📄 Processing PDF: {pdf_path}")
    print(f"📊 Total pages: {len(doc)}")
    
    image_count = 0
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images()
        
        if len(image_list) > 0:
            print(f"\n📄 Page {page_num + 1}: Found {len(image_list)} images")
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            
            # Only save RGB or Grayscale images (skip CMYK)
            if pix.n - pix.alpha < 4:
                # Generate filename with PDF name prefix
                filename = f"{pdf_name}_page{page_num + 1}_img{img_index + 1}.png"
                filepath = os.path.join(output_folder, filename)
                
                # Save image
                pix.save(filepath)
                image_count += 1
                print(f"  ✅ Saved: {filename}")
            else:
                print(f"  ⚠️  Skipped CMYK image")
            
            pix = None
    
    doc.close()
    print(f"\n✅ Extracted {image_count} images to {output_folder}")
    print(f"💡 Tip: Rename images to match your questions (e.g., q2-graph.png)")

if __name__ == "__main__":
    import sys
    
    # Check if PDF path provided as argument
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        output_folder = sys.argv[2] if len(sys.argv) > 2 else "bulk-import/images"
        
        if not os.path.exists(pdf_path):
            print(f"❌ PDF not found: {pdf_path}")
            exit(1)
        
        extract_images_from_pdf(pdf_path, output_folder)
    else:
        # Interactive mode
        pdf_path = input("Enter PDF path (or press Enter to skip): ").strip()
        
        if not pdf_path:
            print("\n📝 To use this script:")
            print("   1. Install PyMuPDF: pip install PyMuPDF")
            print("   2. Run: python bulk-import/extract-images-from-pdf.py <pdf-path>")
            print("   3. Or drag PDFs into bulk-import/ and run: bash bulk-import/extract-pdf.sh")
            print("\n💡 Or just use screenshots - it's easier!")
            exit(0)
        
        if not os.path.exists(pdf_path):
            print(f"❌ PDF not found: {pdf_path}")
            exit(1)
        
        output_folder = "bulk-import/images"
        extract_images_from_pdf(pdf_path, output_folder)

