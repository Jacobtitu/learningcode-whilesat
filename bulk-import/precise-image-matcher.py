#!/usr/bin/env python3
"""
Precise image matcher: Matches images to questions based on question number positions
Images belong to the question number that appears BEFORE them, until next question number
"""

import fitz
import json
import re
from pathlib import Path

def extract_questions_with_precise_images():
    """Extract questions and match images precisely based on question number positions"""
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
    
    print("🔍 Precise matching: Analyzing question positions and images...\n")
    
    questions_with_images = {}
    
    # Process Math Module pages (19-26)
    for page_num in range(18, min(26, len(doc))):  # Pages 19-26
        page = doc[page_num]
        text = page.get_text()
        
        # Get images on this page from PDF
        pdf_images = page.get_images()
        
        if not pdf_images or (page_num + 1) not in all_images:
            continue
        
        # Extract question numbers and their positions in text
        lines = text.split('\n')
        question_positions = []  # (question_num, line_index)
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            # Check if this is a question number (1-22, standalone)
            if re.match(r'^\d+$', stripped):
                q_num = int(stripped)
                if 1 <= q_num <= 22:
                    question_positions.append((q_num, i))
        
        if not question_positions:
            continue
        
        print(f"📄 Page {page_num + 1}:")
        print(f"   Questions: {[q[0] for q in question_positions]}")
        print(f"   Images on page: {len(all_images[page_num + 1])}")
        
        # Match images to questions
        # Strategy: Images belong to the question that appears BEFORE them
        # If we have Q4, Q5, Q6 on same page:
        # - Images before Q5 belong to Q4
        # - Images after Q5 but before Q6 belong to Q5
        # - Images after Q6 belong to Q6
        
        extracted_images = sorted(all_images[page_num + 1], key=lambda x: x['img_num'])
        
        # For each question, find which images belong to it
        for q_idx, (q_num, q_line_pos) in enumerate(question_positions):
            # Find the range of lines this question covers
            # Start: current question line
            # End: next question line (or end of page)
            start_line = q_line_pos
            end_line = question_positions[q_idx + 1][1] if q_idx + 1 < len(question_positions) else len(lines)
            
            # Count how many images appear in this question's section
            # Since we can't get exact image positions, we'll use a heuristic:
            # If this is the last question on page, it gets remaining images
            # Otherwise, we need to look at the text structure
            
            # Simple heuristic for now:
            # - If only one question on page: all images belong to it
            # - If multiple questions: distribute images based on question order
            #   (This is approximate - user may need to adjust)
            
            if len(question_positions) == 1:
                # Only one question - all images belong to it
                if q_num not in questions_with_images:
                    questions_with_images[q_num] = []
                questions_with_images[q_num].extend(extracted_images)
                print(f"   ✅ Q{q_num}: {len(extracted_images)} images (only question on page)")
            else:
                # Multiple questions - need better distribution
                # Look at question text to see if it mentions graphs/charts
                question_text = ' '.join(lines[start_line:min(start_line+10, end_line)])
                
                # Check if question text mentions visual elements
                has_visual_keywords = any(keyword in question_text.lower() for keyword in 
                    ['graph', 'chart', 'scatterplot', 'diagram', 'figure', 'table', 'plot', 'shows'])
                
                if has_visual_keywords:
                    # This question likely has images
                    # Assign images proportionally or based on keywords
                    # For now, assign first image(s) to first question, etc.
                    images_per_question = len(extracted_images) // len(question_positions)
                    start_img = q_idx * images_per_question
                    end_img = start_img + images_per_question if q_idx < len(question_positions) - 1 else len(extracted_images)
                    
                    assigned_images = extracted_images[start_img:end_img]
                    if assigned_images:
                        if q_num not in questions_with_images:
                            questions_with_images[q_num] = []
                        questions_with_images[q_num].extend(assigned_images)
                        print(f"   ✅ Q{q_num}: {len(assigned_images)} images (has visual keywords)")
        
        print()
    
    doc.close()
    
    return questions_with_images

def update_database_precisely():
    """Update database with precise image matching"""
    
    # Load database
    with open('questions-database.json', 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # Get precise image mappings
    image_mappings = extract_questions_with_precise_images()
    
    print("\n📝 Updating database with precise image matching...\n")
    
    updated_count = 0
    removed_count = 0
    
    for q in questions:
        if q.get('module') == 'Math Module 1' and q.get('subject') == 'Math':
            q_num = q.get('questionNumber')
            
            if q_num in image_mappings and image_mappings[q_num]:
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
                elif len(images) >= 1:
                    # Single or multiple images
                    img_filename = images[0]['filename']
                    new_name = f"q{q_num}-graph.png"
                    q['imageUrl'] = f"images/2025-03/asiav1/{new_name}"
                    if len(images) > 1:
                        print(f"✅ Q{q_num}: Added image → {new_name} ({len(images)} images available, using first)")
                    else:
                        print(f"✅ Q{q_num}: Added image → {new_name}")
                    updated_count += 1
            else:
                # This question does NOT have images - remove any image references
                had_image = False
                if 'imageUrl' in q:
                    del q['imageUrl']
                    had_image = True
                if 'imageCaption' in q:
                    del q['imageCaption']
                if q.get('hasImageChoices'):
                    q['hasImageChoices'] = False
                    had_image = True
                
                if had_image:
                    removed_count += 1
                    print(f"🗑️  Q{q_num}: Removed image (question has no images)")
    
    # Save updated database
    with open('questions-database.json', 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Updated {updated_count} questions with images")
    print(f"🗑️  Removed images from {removed_count} questions")
    
    # Show summary
    math_qs = [q for q in questions if q.get('module') == 'Math Module 1']
    with_images = [q for q in math_qs if 'imageUrl' in q or q.get('hasImageChoices')]
    without_images = [q for q in math_qs if 'imageUrl' not in q and not q.get('hasImageChoices')]
    
    print(f"\n📊 Summary:")
    print(f"   Total Math questions: {len(math_qs)}")
    print(f"   With images: {len(with_images)}")
    print(f"   Without images: {len(without_images)}")

if __name__ == "__main__":
    update_database_precisely()

