#!/usr/bin/env python3
"""
Final extraction: Get all Math questions with proper text and image matching
"""

import fitz
import json
import csv
import re
from pathlib import Path

def extract_all_math_questions():
    """Extract all 22 Math questions with full text"""
    pdf_path = 'bulk-import/202503asiav1 (1).pdf'
    doc = fitz.open(pdf_path)
    
    # Get text from Math pages (19-26)
    full_text = ""
    for page_num in range(18, min(26, len(doc))):
        page = doc[page_num]
        full_text += page.get_text() + "\n"
    
    doc.close()
    
    # Parse questions
    questions = []
    lines = [l.strip() for l in full_text.split('\n') if l.strip()]
    
    current_q = None
    
    for i, line in enumerate(lines):
        # Check if this is a question number
        if re.match(r'^\d+$', line) and 1 <= int(line) <= 22:
            q_num = int(line)
            if current_q:
                questions.append(current_q)
            
            current_q = {
                'number': q_num,
                'text_parts': [],
                'choices': []
            }
            continue
        
        if current_q:
            # Check if this is a choice
            choice_match = re.match(r'^([A-D])\)\s*(.+)$', line)
            if choice_match:
                current_q['choices'].append(choice_match.group(2).strip())
            elif line and not line.startswith('Math Module') and 'QUESTIONS' not in line:
                current_q['text_parts'].append(line)
    
    if current_q:
        questions.append(current_q)
    
    return questions

def match_images_to_questions(questions):
    """Match extracted images to questions"""
    images_folder = Path('bulk-import/images')
    images = list(images_folder.glob('*.png'))
    
    # Page to question mapping based on PDF structure
    # Page 20: Q1 (buttons), Q2 (graph with 4 choices)
    # Page 22: Q3 (scatterplot)
    # Page 23: Q4-Q7
    # Page 24: Q8-Q9 (with 4 graph choices for Q1)
    # Page 25: Q10 (more graphs)
    # Page 26: Q11-Q22
    
    # Group images by page
    images_by_page = {}
    for img in images:
        match = re.search(r'page(\d+)_img(\d+)', img.name)
        if match:
            page = int(match.group(1))
            img_num = int(match.group(2))
            if page not in images_by_page:
                images_by_page[page] = []
            images_by_page[page].append({
                'filename': img.name,
                'path': str(img),
                'img_num': img_num
            })
    
    # Match based on known structure
    # Q1: Has 4 graph choices on pages 24-25
    # Q2: Has graph on page 20
    # Q3: Has scatterplot on page 22
    
    for q in questions:
        q['images'] = []
        
        if q['number'] == 1:
            # Q1: 4 graph choices from pages 24-25
            if 24 in images_by_page:
                q['images'] = sorted(images_by_page[24][:4], key=lambda x: x['img_num'])
            elif 25 in images_by_page:
                q['images'] = sorted(images_by_page[25][:4], key=lambda x: x['img_num'])
        elif q['number'] == 2:
            # Q2: Graph on page 20
            if 20 in images_by_page:
                q['images'] = images_by_page[20][:1]
        elif q['number'] == 3:
            # Q3: Scatterplot on page 22
            if 22 in images_by_page:
                q['images'] = images_by_page[22][:1]
        else:
            # Other questions - match by page
            # Rough mapping
            if q['number'] <= 7 and 23 in images_by_page:
                q['images'] = images_by_page[23][:1]
            elif q['number'] >= 11 and 26 in images_by_page:
                q['images'] = images_by_page[26][:1]
    
    return questions

def create_csv_for_import(questions):
    """Create CSV rows ready for import"""
    rows = []
    
    for q in questions:
        # Combine text parts
        text = ' '.join(q['text_parts']).strip()
        if not text:
            text = f"Math question {q['number']}"
        
        # Clean up text (remove extra spaces)
        text = re.sub(r'\s+', ' ', text)
        
        # Get choices
        choices = q['choices']
        while len(choices) < 4:
            choices.append('')
        
        # Handle images
        image_name = ''
        has_image_choices = False
        
        if q['images']:
            if len(q['images']) == 4:
                # Math question with 4 graph choices (like Q1)
                has_image_choices = True
                # Use image paths as choices
                choices = [img['filename'] for img in sorted(q['images'], key=lambda x: x['img_num'])]
            elif len(q['images']) == 1:
                # Single image
                image_name = f"q{q['number']}-graph.png"
        
        row = {
            'question_number': q['number'],
            'question_text': text[:500],
            'prompt': '',
            'choice_a': choices[0] if len(choices) > 0 else '',
            'choice_b': choices[1] if len(choices) > 1 else '',
            'choice_c': choices[2] if len(choices) > 2 else '',
            'choice_d': choices[3] if len(choices) > 3 else '',
            'correct_answer': '',  # Fill manually
            'explanation': '',  # Fill manually
            'image_name': image_name,
            'image_caption': '',
            'difficulty': 'medium',
            'topic': 'math',
            'module': 'Math Module 1',
            'date': '2025-03',
            'region': 'Asia',
            'test_number': 1,
            'test_name': '2025-03 Asia Test 1',
            'subject': 'Math',
            'has_image_choices': 'yes' if has_image_choices else 'no'
        }
        
        rows.append(row)
    
    return rows

def main():
    print("🔍 Extracting Math Module 1 questions...\n")
    
    # Extract questions
    questions = extract_all_math_questions()
    print(f"✅ Found {len(questions)} questions")
    
    # Match with images
    questions = match_images_to_questions(questions)
    
    # Show first few
    print("\nFirst 3 questions:")
    for q in questions[:3]:
        print(f"\nQuestion {q['number']}:")
        print(f"  Text: {q['text_parts'][0] if q['text_parts'] else 'No text'}")
        print(f"  Choices: {len(q['choices'])}")
        print(f"  Images: {len(q['images'])}")
    
    # Create CSV
    csv_rows = create_csv_for_import(questions)
    
    # Save CSV
    csv_file = 'bulk-import/math-module1-questions.csv'
    if csv_rows:
        fieldnames = list(csv_rows[0].keys())
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)
        
        print(f"\n✅ Created: {csv_file}")
        print(f"   Contains {len(csv_rows)} questions ready to import")
        print(f"\n📝 Next steps:")
        print(f"   1. Review {csv_file}")
        print(f"   2. Add correct answers and explanations")
        print(f"   3. Copy rows to bulk-import/questions.csv")
        print(f"   4. Run: python import.py")

if __name__ == "__main__":
    main()

