#!/usr/bin/env python3
"""
Smart image matcher: Matches images to questions based on question numbers in PDF
Only adds images to questions that actually have them
"""

import fitz
import json
import re
from pathlib import Path

def extract_questions_with_images():
    """Extract questions and match images based on question numbers"""
    pdf_path = 'bulk-import/202503asiav1 (1).pdf'
    doc = fitz.open(pdf_path)
    
    # Get all images from bulk-import folder
    images_folder = Path('bulk-import/images')
    all_images = {}
    for img in images_folder.glob('*.png'):
        match = re.search(r'page(\d+)_img(\d+)', img.name)
        if match:
            page = int(match.group(1))
            img_num = int(match.group(2))
            if page not in all_images:
                all_images[page] = []
            all_images[page].append({
                'filename': img.name,
                'path': str(img),
                'img_num': img_num
            })
    
    print("🔍 Analyzing PDF pages to match images to questions...\n")
    
    # Process Math Module pages (19-26)
    questions_with_images = {}
    
    for page_num in range(18, min(26, len(doc))):  # Pages 19-26 (0-indexed: 18-25)
        page = doc[page_num]
        text = page.get_text()
        
        # Find all question numbers on this page
        lines = text.split('\n')
        question_numbers_on_page = []
        
        for line in lines:
            stripped = line.strip()
            # Check if this is a question number (1-22, standalone)
            if re.match(r'^\d+$', stripped):
                q_num = int(stripped)
                if 1 <= q_num <= 22:
                    question_numbers_on_page.append(q_num)
        
        # Get images on this page
        images_on_page = page.get_images()
        
        if question_numbers_on_page and images_on_page:
            print(f"📄 Page {page_num + 1}:")
            print(f"   Questions found: {question_numbers_on_page}")
            print(f"   Images on page: {len(images_on_page)}")
            
            # Match images to questions
            # Images belong to the question number that appears BEFORE them
            # If multiple questions on same page, images belong to the first one
            # until we see the next question number
            
            if page_num + 1 in all_images:
                extracted_images = sorted(all_images[page_num + 1], key=lambda x: x['img_num'])
                
                # If only one question on page, all images belong to it
                if len(question_numbers_on_page) == 1:
                    q_num = question_numbers_on_page[0]
                    if q_num not in questions_with_images:
                        questions_with_images[q_num] = []
                    questions_with_images[q_num].extend(extracted_images)
                    print(f"   ✅ All {len(extracted_images)} images → Question {q_num}")
                else:
                    # Multiple questions on page - need to figure out which images belong to which
                    # For now, assign to first question (user can adjust)
                    q_num = question_numbers_on_page[0]
                    if q_num not in questions_with_images:
                        questions_with_images[q_num] = []
                    questions_with_images[q_num].extend(extracted_images)
                    print(f"   ⚠️  Multiple questions - assigning {len(extracted_images)} images to Question {q_num} (first)")
            print()
    
    doc.close()
    
    return questions_with_images

def update_database_with_images():
    """Update database to only add images to questions that have them"""
    
    # Load database
    with open('questions-database.json', 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # Get image mappings
    image_mappings = extract_questions_with_images()
    
    print("\n📝 Updating database...\n")
    
    updated_count = 0
    removed_count = 0
    
    for q in questions:
        if q.get('module') == 'Math Module 1' and q.get('subject') == 'Math':
            q_num = q.get('questionNumber')
            
            if q_num in image_mappings:
                # This question HAS images
                images = image_mappings[q_num]
                
                if len(images) == 4:
                    # Math question with 4 graph choices
                    q['hasImageChoices'] = True
                    # Update choices to use image paths
                    image_paths = [f"images/2025-03/asiav1/{img['filename']}" for img in sorted(images, key=lambda x: x['img_num'])]
                    q['choices'] = image_paths
                    print(f"✅ Q{q_num}: Added 4 image choices")
                    updated_count += 1
                elif len(images) == 1:
                    # Single image
                    img_filename = images[0]['filename']
                    # Rename suggestion
                    new_name = f"q{q_num}-graph.png"
                    q['imageUrl'] = f"images/2025-03/asiav1/{new_name}"
                    print(f"✅ Q{q_num}: Added image → {new_name}")
                    updated_count += 1
                elif len(images) > 1:
                    # Multiple images (not 4) - probably multiple graphs
                    img_filename = images[0]['filename']
                    new_name = f"q{q_num}-graph.png"
                    q['imageUrl'] = f"images/2025-03/asiav1/{new_name}"
                    print(f"✅ Q{q_num}: Added image → {new_name} (using first of {len(images)} images)")
                    updated_count += 1
            else:
                # This question does NOT have images - remove any image references
                if 'imageUrl' in q:
                    del q['imageUrl']
                    removed_count += 1
                    print(f"🗑️  Q{q_num}: Removed image (question has no images)")
                if 'imageCaption' in q:
                    del q['imageCaption']
                if q.get('hasImageChoices'):
                    # Remove image choices, restore text choices if needed
                    if not q.get('choices') or q['choices'][0].startswith('images/'):
                        # Need to restore text choices - but we don't have them
                        # Keep as is for now
                        pass
    
    # Save updated database
    with open('questions-database.json', 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Updated {updated_count} questions with images")
    print(f"🗑️  Removed images from {removed_count} questions")
    print(f"📊 Total Math questions: {len([q for q in questions if q.get('module') == 'Math Module 1'])}")

if __name__ == "__main__":
    update_database_with_images()

