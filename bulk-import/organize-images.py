#!/usr/bin/env python3
"""
Organize and rename images to match questions
"""

import shutil
from pathlib import Path
import re

def organize_images():
    """Copy and rename images from bulk-import to proper location"""
    
    source_folder = Path('bulk-import/images')
    target_folder = Path('images/2025-03/asiav1')
    target_folder.mkdir(parents=True, exist_ok=True)
    
    # Mapping based on what we know:
    # Page 20: Q2 graph
    # Page 22: Q3 scatterplot  
    # Page 24: Q1 graph choices (4 images)
    # etc.
    
    mappings = [
        # Question 2 - Graph (page 20, img 1 or 2)
        {'source': '202503asiav1 (1)_page20_img1.png', 'target': 'q2-graph.png', 'question': 2},
        {'source': '202503asiav1 (1)_page20_img2.png', 'target': 'q2-graph-alt.png', 'question': 2},
        
        # Question 3 - Scatterplot (page 22)
        {'source': '202503asiav1 (1)_page22_img1.png', 'target': 'q3-scatterplot.png', 'question': 3},
        
        # Question 1 - Math graphs (4 choices from page 24)
        {'source': '202503asiav1 (1)_page24_img1.png', 'target': 'math-q1-optionA.png', 'question': 1},
        {'source': '202503asiav1 (1)_page24_img2.png', 'target': 'math-q1-optionB.png', 'question': 1},
        {'source': '202503asiav1 (1)_page24_img3.png', 'target': 'math-q1-optionC.png', 'question': 1},
        {'source': '202503asiav1 (1)_page24_img7.png', 'target': 'math-q1-optionD.png', 'question': 1},
        
        # Question 4 - Graph (page 23)
        {'source': '202503asiav1 (1)_page23_img1.png', 'target': 'q4-graph.png', 'question': 4},
    ]
    
    copied = 0
    skipped = 0
    
    print("📸 Organizing images...\n")
    
    for mapping in mappings:
        source = source_folder / mapping['source']
        target = target_folder / mapping['target']
        
        if source.exists():
            shutil.copy(source, target)
            print(f"✅ Q{mapping['question']}: {mapping['source']} → {mapping['target']}")
            copied += 1
        else:
            print(f"⚠️  Not found: {mapping['source']}")
            skipped += 1
    
    print(f"\n✅ Copied {copied} images")
    if skipped > 0:
        print(f"⚠️  Skipped {skipped} (not found)")
    
    print(f"\n📁 Images are now in: {target_folder}")
    print(f"\n💡 You may need to:")
    print(f"   1. Check which image is correct for Q2 (try both)")
    print(f"   2. Verify Q1 graph choices are in correct order")
    print(f"   3. Add more mappings for other questions")

if __name__ == "__main__":
    organize_images()

