#!/usr/bin/env python3
"""
Extract images from Asia v6 PDF and organize them
Since PDF is image-based, we'll extract all images and organize by page
"""

import fitz
import json
from pathlib import Path
from collections import defaultdict

def extract_all_images(pdf_path):
    """Extract all images from PDF"""
    doc = fitz.open(pdf_path)
    
    output_folder = Path("images/2025-03/asiav6")
    output_folder.mkdir(parents=True, exist_ok=True)
    
    images_by_page = defaultdict(list)
    total_images = 0
    
    print(f"Extracting images from {pdf_path}...")
    print(f"Total pages: {len(doc)}\n")
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            try:
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                
                if pix.n - pix.alpha < 4:
                    filename = f"202503asiav6_page{page_num + 1}_img{img_index + 1}.png"
                    filepath = output_folder / filename
                    pix.save(str(filepath))
                    
                    images_by_page[page_num].append({
                        'filename': filename,
                        'filepath': str(filepath),
                        'page': page_num + 1,
                        'index': img_index + 1,
                        'width': pix.width,
                        'height': pix.height
                    })
                    total_images += 1
                
                pix = None
            except Exception as e:
                print(f"  ⚠️  Error extracting image {img_index + 1} from page {page_num + 1}: {e}")
    
    total_pages = len(doc)
    doc.close()
    
    print(f"✅ Extracted {total_images} images")
    print(f"   Saved to: {output_folder}\n")
    
    # Create a mapping file
    mapping = {
        'total_pages': total_pages,
        'total_images': total_images,
        'images_by_page': {}
    }
    
    for page_num, images in images_by_page.items():
        mapping['images_by_page'][page_num + 1] = [
            {
                'filename': img['filename'],
                'index': img['index'],
                'size': f"{img['width']}x{img['height']}"
            }
            for img in images
        ]
    
    mapping_file = output_folder / "image-mapping.json"
    with open(mapping_file, 'w') as f:
        json.dump(mapping, f, indent=2)
    
    print(f"✅ Created mapping file: {mapping_file}")
    
    # Print summary
    print("\n📊 Summary by page:")
    for page_num in sorted(images_by_page.keys())[:20]:  # First 20 pages
        images = images_by_page[page_num]
        print(f"  Page {page_num + 1}: {len(images)} image(s)")
        for img in images:
            print(f"    - {img['filename']} ({img['width']}x{img['height']})")
    
    if len(images_by_page) > 20:
        print(f"  ... and {len(images_by_page) - 20} more pages")
    
    return images_by_page

if __name__ == "__main__":
    pdf_path = "bulk-import/202503asiav6-2.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ Error: PDF not found at {pdf_path}")
        exit(1)
    
    extract_all_images(pdf_path)
    print("\n✅ Image extraction complete!")
    print("\n📝 Next steps:")
    print("   1. Review extracted images in images/2025-03/asiav6/")
    print("   2. Use OCR or manual entry to extract question text")
    print("   3. Match images to questions based on page numbers")

