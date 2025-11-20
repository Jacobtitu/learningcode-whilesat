#!/usr/bin/env python3
"""
Helper script to identify which extracted images belong to which questions
Opens images so you can see them and identify them
"""

import os
from pathlib import Path
import subprocess
import sys

def open_image(image_path):
    """Open image in default viewer"""
    if sys.platform == 'darwin':  # macOS
        subprocess.run(['open', image_path])
    elif sys.platform == 'linux':
        subprocess.run(['xdg-open', image_path])
    elif sys.platform == 'win32':
        os.startfile(image_path)

def main():
    images_folder = Path('bulk-import/images')
    
    if not images_folder.exists():
        print("❌ bulk-import/images folder not found")
        return
    
    # Get all PNG images
    images = sorted(images_folder.glob('*.png'))
    
    if not images:
        print("❌ No images found in bulk-import/images")
        return
    
    print("=" * 60)
    print("IMAGE IDENTIFICATION HELPER")
    print("=" * 60)
    print(f"\nFound {len(images)} images to identify\n")
    
    # Group by page
    pages = {}
    for img in images:
        # Extract page number from filename like "202503asiav1 (1)_page20_img1.png"
        parts = img.stem.split('_')
        page_num = None
        for part in parts:
            if part.startswith('page'):
                page_num = int(part.replace('page', ''))
                break
        
        if page_num:
            if page_num not in pages:
                pages[page_num] = []
            pages[page_num].append(img)
    
    print("Images organized by PDF page:\n")
    
    # Show mapping guide
    mapping_guide = {
        20: "Question 2 - Graph with two lines intersecting at (5,5)",
        21: "Question 11 - Data table",
        24: "Question 1 - Math graphs (4 options: A, B, C, D)",
        25: "Question 1 continued - More math graphs",
        22: "Possible chart/graph question",
        23: "Possible chart/graph question",
        13: "Possible Reading/Writing question image",
        14: "Possible Reading/Writing question image",
    }
    
    for page_num in sorted(pages.keys()):
        imgs = pages[page_num]
        guide = mapping_guide.get(page_num, "Unknown question")
        print(f"📄 Page {page_num}: {len(imgs)} image(s) - {guide}")
        for img in imgs:
            print(f"   - {img.name}")
    
    print("\n" + "=" * 60)
    print("IDENTIFICATION PROCESS")
    print("=" * 60)
    print("\nI'll open images for you to identify. Here's what to do:")
    print("\n1. Look at each image that opens")
    print("2. Identify which question it belongs to")
    print("3. Note the question number")
    print("\nPress Enter after viewing each image to continue...")
    
    input("\nPress Enter to start identifying images...")
    
    # Open images one by one
    identified = {}
    
    for page_num in sorted(pages.keys()):
        imgs = pages[page_num]
        print(f"\n📄 Page {page_num} - {len(imgs)} image(s)")
        
        for img in imgs:
            print(f"\nOpening: {img.name}")
            open_image(str(img))
            
            question_num = input("Which question does this belong to? (Enter question number, or 'skip'): ").strip()
            
            if question_num.lower() == 'skip':
                continue
            
            if question_num:
                if question_num not in identified:
                    identified[question_num] = []
                identified[question_num].append({
                    'filename': img.name,
                    'path': str(img)
                })
                print(f"✅ Identified as Question {question_num}")
    
    # Generate renaming suggestions
    print("\n" + "=" * 60)
    print("RENAMING SUGGESTIONS")
    print("=" * 60)
    
    if identified:
        print("\nHere are suggested renames:\n")
        for q_num, imgs in sorted(identified.items(), key=lambda x: int(x[0])):
            if len(imgs) == 1:
                # Single image - probably a question image
                old_name = imgs[0]['filename']
                new_name = f"q{q_num}-graph.png"
                print(f"Question {q_num}:")
                print(f"  mv '{old_name}' '{new_name}'")
            elif len(imgs) == 4:
                # 4 images - probably math question with 4 choices
                print(f"Question {q_num} (Math with 4 graph choices):")
                for i, img in enumerate(imgs):
                    letter = chr(65 + i)  # A, B, C, D
                    old_name = img['filename']
                    new_name = f"math-q{q_num}-option{letter}.png"
                    print(f"  mv '{old_name}' '{new_name}'")
            else:
                print(f"Question {q_num} ({len(imgs)} images):")
                for i, img in enumerate(imgs):
                    old_name = img['filename']
                    new_name = f"q{q_num}-img{i+1}.png"
                    print(f"  mv '{old_name}' '{new_name}'")
    else:
        print("\nNo images were identified. You can manually rename them.")
    
    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Rename images using the suggestions above")
    print("2. Add questions to bulk-import/questions.csv")
    print("3. Run: python import.py")

if __name__ == "__main__":
    main()

