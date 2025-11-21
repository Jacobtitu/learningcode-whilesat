#!/usr/bin/env python3
"""
Match extracted images to asiav2 Math Module 2 questions
"""

import json
import re
from pathlib import Path
import shutil

def match_images_to_questions():
    # Load questions
    with open('questions-database.json', 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # Filter for asiav2 Math Module 2 questions
    math_module2_questions = [
        q for q in questions 
        if q.get('testId') == 'asiav2' 
        and q.get('module') == 'Math Module 2'
    ]
    math_module2_questions.sort(key=lambda x: x['questionNumber'])
    
    # Get all extracted images
    images_folder = Path('images/2025-03/asiav2')
    extracted_images = sorted(images_folder.glob('202503asiav2_page*_img*.png'))
    
    print(f"📚 Found {len(math_module2_questions)} Math Module 2 questions")
    print(f"🖼️  Found {len(extracted_images)} extracted images\n")
    
    # Questions that need images (based on keywords)
    visual_keywords = ['graph', 'figure', 'shown', 'diagram', 'chart', 'plot', 'scatterplot', 'table']
    
    questions_needing_images = []
    for q in math_module2_questions:
        text = q.get('questionText', '').lower()
        has_visual = any(keyword in text for keyword in visual_keywords)
        current_image = q.get('imageUrl', '')
        
        if has_visual or current_image:
            questions_needing_images.append({
                'q_num': q['questionNumber'],
                'text': q['questionText'][:100],  # First 100 chars
                'has_image': bool(current_image),
                'current_image': current_image
            })
    
    print(f"📊 Questions needing images: {len(questions_needing_images)}\n")
    
    # Match images to questions
    # Typical SAT layout: 2-3 questions per page in Math Module 2
    # Images are usually in order with questions
    
    matches = []
    img_idx = 0
    
    # For questions 1 and 4, we already know what they need
    for q in math_module2_questions:
        q_num = q['questionNumber']
        text = q.get('questionText', '').lower()
        
        # Determine image type based on question text
        if 'graph' in text or 'height' in text or 'ball' in text:
            img_type = 'graph'
        elif 'triangle' in text or 'figure' in text or 'diagram' in text:
            img_type = 'diagram'
        elif 'table' in text:
            img_type = 'table'
        else:
            img_type = 'diagram'  # default
        
        # Check if question needs image
        needs_image = any(kw in text for kw in visual_keywords) or q.get('imageUrl', '')
        
        if needs_image and img_idx < len(extracted_images):
            old_path = extracted_images[img_idx]
            new_name = f"math-module-2-q{q_num}-{img_type}.png"
            new_path = images_folder / new_name
            
            # Copy/rename the image
            shutil.copy2(old_path, new_path)
            matches.append({
                'question': q_num,
                'old_file': old_path.name,
                'new_file': new_name,
                'type': img_type
            })
            print(f"✅ Q{q_num}: {old_path.name} → {new_name}")
            img_idx += 1
    
    print(f"\n📝 Matched {len(matches)} images")
    print(f"\n💡 Update the database with these image paths:")
    for match in matches:
        print(f"   Q{match['question']}: images/2025-03/asiav2/{match['new_file']}")
    
    return matches

if __name__ == "__main__":
    try:
        match_images_to_questions()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

