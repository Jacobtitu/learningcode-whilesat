#!/usr/bin/env python3
"""
Extract and match images for asiav2 Math Module 2 questions
"""

import fitz  # PyMuPDF
import json
import re
from pathlib import Path
import shutil

def extract_math_module2_images():
    pdf_path = 'bulk-import/202503asiav2.pdf'
    output_folder = Path('images/2025-03/asiav2')
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Load questions database to find Math Module 2 questions
    with open('questions-database.json', 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # Filter for asiav2 Math Module 2 questions
    math_module2_questions = [
        q for q in questions 
        if q.get('testId') == 'asiav2' 
        and q.get('module') == 'Math Module 2'
    ]
    math_module2_questions.sort(key=lambda x: x['questionNumber'])
    
    print(f"📚 Found {len(math_module2_questions)} Math Module 2 questions for asiav2")
    
    # Open PDF
    doc = fitz.open(pdf_path)
    print(f"📄 PDF has {len(doc)} pages")
    
    # Math Module 2 typically starts around page 18-20 in SAT PDFs
    # Extract images from pages that likely contain Math Module 2
    # We'll extract from pages 18-40 to be safe
    start_page = 18
    end_page = min(40, len(doc))
    
    print(f"\n🔍 Extracting images from pages {start_page} to {end_page}...")
    
    image_count = 0
    extracted_images = []
    
    for page_num in range(start_page, end_page):
        page = doc[page_num]
        image_list = page.get_images()
        
        if len(image_list) > 0:
            print(f"\n📄 Page {page_num + 1}: Found {len(image_list)} images")
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                
                # Only save RGB or Grayscale images (skip CMYK)
                if pix.n - pix.alpha < 4:
                    # Save with temporary name first
                    temp_filename = f"202503asiav2_page{page_num + 1}_img{img_index + 1}.png"
                    temp_filepath = output_folder / temp_filename
                    pix.save(str(temp_filepath))
                    image_count += 1
                    extracted_images.append({
                        'page': page_num + 1,
                        'img_index': img_index + 1,
                        'temp_file': temp_filepath,
                        'filename': temp_filename
                    })
                    print(f"  ✅ Saved: {temp_filename}")
                
                pix = None
    
    doc.close()
    
    print(f"\n✅ Extracted {image_count} images")
    print(f"\n📝 Images saved to: {output_folder}")
    print(f"\n💡 Next steps:")
    print(f"   1. Review the extracted images")
    print(f"   2. Match them to questions manually or use an image matcher script")
    print(f"   3. Rename them to: math-module-2-q[number]-[type].png")
    
    return extracted_images

if __name__ == "__main__":
    try:
        extract_math_module2_images()
    except ImportError:
        print("❌ PyMuPDF not installed. Install it with: pip install PyMuPDF")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

