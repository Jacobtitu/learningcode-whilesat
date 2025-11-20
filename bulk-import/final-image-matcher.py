#!/usr/bin/env python3
"""
Final image matcher: Uses question text to determine which questions have images
Only adds images to questions that mention graphs, charts, scatterplots, etc.
"""

import fitz
import json
import re
from pathlib import Path

def analyze_questions_for_images():
    """Analyze question text to determine which need images"""
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
    
    print("🔍 Analyzing questions to determine which need images...\n")
    
    questions_with_images = {}
    question_texts = {}
    
    # First pass: Extract all question texts
    for page_num in range(18, min(26, len(doc))):
        page = doc[page_num]
        text = page.get_text()
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if re.match(r'^\d+$', stripped) and 1 <= int(stripped) <= 22:
                q_num = int(stripped)
                # Get text after question number (until next question or end)
                question_text = []
                for j in range(i+1, len(lines)):
                    next_line = lines[j].strip()
                    if re.match(r'^\d+$', next_line) and 1 <= int(next_line) <= 22:
                        break
                    if next_line and not next_line.startswith('Math Module'):
                        question_text.append(next_line)
                
                question_texts[q_num] = ' '.join(question_text[:20])  # First 20 lines
    
    # Second pass: Match images based on question text and page structure
    for page_num in range(18, min(26, len(doc))):
        page = doc[page_num]
        text = page.get_text()
        lines = text.split('\n')
        
        # Find question numbers on this page
        question_nums_on_page = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if re.match(r'^\d+$', stripped) and 1 <= int(stripped) <= 22:
                question_nums_on_page.append(int(stripped))
        
        if not question_nums_on_page or (page_num + 1) not in all_images:
            continue
        
        extracted_images = sorted(all_images[page_num + 1], key=lambda x: x['img_num'])
        
        print(f"📄 Page {page_num + 1}: Questions {question_nums_on_page}, {len(extracted_images)} images")
        
        # Check each question for visual keywords
        visual_keywords = ['graph', 'chart', 'scatterplot', 'diagram', 'figure', 'table', 'plot', 'shows', 'shown']
        
        questions_needing_images = []
        for q_num in question_nums_on_page:
            if q_num in question_texts:
                text_lower = question_texts[q_num].lower()
                has_visual = any(keyword in text_lower for keyword in visual_keywords)
                
                # Also check if question has A) B) C) D) right after number (graph choices)
                # This indicates it's a graph question
                has_choices_immediately = False
                for i, line in enumerate(lines):
                    if line.strip() == str(q_num):
                        # Check next few lines
                        for j in range(i+1, min(i+5, len(lines))):
                            if re.match(r'^[A-D]\)', lines[j].strip()):
                                has_choices_immediately = True
                                break
                        break
                
                if has_visual or has_choices_immediately:
                    questions_needing_images.append(q_num)
                    print(f"   ✅ Q{q_num} needs images (visual keywords or graph choices)")
        
        # Distribute images to questions that need them
        if questions_needing_images and extracted_images:
            if len(questions_needing_images) == 1:
                # Only one question needs images - all images belong to it
                q_num = questions_needing_images[0]
                if q_num not in questions_with_images:
                    questions_with_images[q_num] = []
                questions_with_images[q_num].extend(extracted_images)
                print(f"   → All {len(extracted_images)} images → Q{q_num}")
            else:
                # Multiple questions need images - distribute
                # If we have 4 images and question has A) B) C) D), it's probably 4 graph choices
                for q_num in questions_needing_images:
                    if q_num not in questions_with_images:
                        questions_with_images[q_num] = []
                    
                    # Check if this question has 4 choices immediately (graph question)
                    text_lower = question_texts.get(q_num, '').lower()
                    if 'graph' in text_lower or 'which of the following' in text_lower:
                        # Probably needs 4 graph choices
                        if len(extracted_images) >= 4:
                            questions_with_images[q_num].extend(extracted_images[:4])
                            print(f"   → 4 images → Q{q_num} (graph choices)")
                            extracted_images = extracted_images[4:]  # Remove used images
                        else:
                            questions_with_images[q_num].extend(extracted_images[:1])
                            print(f"   → 1 image → Q{q_num}")
                            extracted_images = extracted_images[1:]
                    else:
                        # Single image question
                        if extracted_images:
                            questions_with_images[q_num].append(extracted_images[0])
                            print(f"   → 1 image → Q{q_num}")
                            extracted_images = extracted_images[1:]
        
        print()
    
    doc.close()
    
    return questions_with_images

def update_database_final():
    """Final update with correct image matching"""
    
    # Load database
    with open('questions-database.json', 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # Get image mappings
    image_mappings = analyze_questions_for_images()
    
    print("\n📝 Updating database...\n")
    
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
                    image_paths = [f"images/2025-03/asiav1/{img['filename']}" for img in sorted(images, key=lambda x: x['img_num'])]
                    q['choices'] = image_paths
                    print(f"✅ Q{q_num}: 4 image choices")
                    updated_count += 1
                elif len(images) >= 1:
                    # Single image
                    img_filename = images[0]['filename']
                    new_name = f"q{q_num}-graph.png"
                    q['imageUrl'] = f"images/2025-03/asiav1/{new_name}"
                    print(f"✅ Q{q_num}: Image → {new_name}")
                    updated_count += 1
            else:
                # This question does NOT have images
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
                    print(f"🗑️  Q{q_num}: No image")
    
    # Save
    with open('questions-database.json', 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Updated {updated_count} questions with images")
    print(f"🗑️  Removed images from {removed_count} questions")
    
    # Summary
    math_qs = [q for q in questions if q.get('module') == 'Math Module 1']
    with_images = [q for q in math_qs if 'imageUrl' in q or q.get('hasImageChoices')]
    
    print(f"\n📊 Final Summary:")
    print(f"   Math questions with images: {len(with_images)}")
    print(f"   Math questions without images: {len(math_qs) - len(with_images)}")

if __name__ == "__main__":
    update_database_final()

