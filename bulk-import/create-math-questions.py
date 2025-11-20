#!/usr/bin/env python3
"""
Create Math Module 1 questions from PDF and match with images
"""

import fitz
import re
import json
import csv
from pathlib import Path

def extract_math_questions():
    """Extract all Math Module 1 questions"""
    pdf_path = 'bulk-import/202503asiav1 (1).pdf'
    doc = fitz.open(pdf_path)
    
    # Math Module 1 is on pages 19-26
    all_text = ""
    for page_num in range(18, min(26, len(doc))):
        page = doc[page_num]
        all_text += page.get_text() + "\n"
    
    doc.close()
    
    # Parse questions - they're numbered 1-22
    questions = []
    
    # Split by question numbers
    # Questions start with just a number on its own line
    lines = all_text.split('\n')
    
    current_q = None
    q_text_lines = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Check if this line starts a new question (just a number 1-22)
        q_match = re.match(r'^(\d+)$', stripped)
        if q_match:
            q_num = int(q_match.group(1))
            if 1 <= q_num <= 22:
                # Save previous question
                if current_q is not None:
                    questions.append(current_q)
                
                # Start new question
                current_q = {
                    'number': q_num,
                    'text': '',
                    'choices': [],
                    'page': None  # Will determine from images
                }
                q_text_lines = []
                continue
        
        # If we're in a question, collect text
        if current_q is not None:
            # Check if this is a choice (A), B), C), D))
            choice_match = re.match(r'^([A-D])\)\s*(.+)$', stripped)
            if choice_match:
                current_q['choices'].append(choice_match.group(2).strip())
            elif stripped and not stripped.startswith('Math Module') and 'QUESTIONS' not in stripped:
                q_text_lines.append(stripped)
    
    # Add last question
    if current_q is not None:
        questions.append(current_q)
    
    # Match with images based on page numbers
    images_folder = Path('bulk-import/images')
    images = list(images_folder.glob('*.png'))
    
    # Page mapping: Based on what we saw
    # Page 20 = Questions 1-2
    # Page 22 = Question 3
    # Page 23 = Questions 4-7
    # Page 24 = Questions 8-9
    # Page 25 = Question 10
    # Page 26 = Questions 11-22
    
    page_to_q = {
        20: [1, 2],
        22: [3],
        23: [4, 5, 6, 7],
        24: [8, 9],
        25: [10],
        26: list(range(11, 23))
    }
    
    # Match images to questions
    for img in images:
        match = re.search(r'page(\d+)_img(\d+)', img.name)
        if match:
            page = int(match.group(1))
            img_num = int(match.group(2))
            
            if page in page_to_q:
                q_nums = page_to_q[page]
                # Assign to first question on that page for now
                # User can adjust
                for q in questions:
                    if q['number'] in q_nums:
                        if 'images' not in q:
                            q['images'] = []
                        q['images'].append({
                            'filename': img.name,
                            'path': str(img),
                            'img_num': img_num
                        })
                        break
    
    return questions

def create_csv_rows(questions):
    """Create CSV rows for import"""
    rows = []
    
    for q in questions:
        # Clean up question text
        text = q['text'].strip()
        if not text:
            # Try to reconstruct from choices context
            text = "Math question " + str(q['number'])
        
        # Get choices
        choices = q['choices']
        while len(choices) < 4:
            choices.append('')
        
        # Determine image handling
        image_name = ''
        image_choices = []
        
        if 'images' in q and q['images']:
            if len(q['images']) == 4:
                # Math question with 4 graph choices
                image_choices = [img['filename'] for img in sorted(q['images'], key=lambda x: x['img_num'])]
            elif len(q['images']) == 1:
                # Single image (graph/chart)
                image_name = f"q{q['number']}-graph.png"
        
        row = {
            'question_number': q['number'],
            'question_text': text[:500],  # Limit length
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
            'has_image_choices': 'yes' if image_choices else 'no',
            'image_choice_a': image_choices[0] if len(image_choices) > 0 else '',
            'image_choice_b': image_choices[1] if len(image_choices) > 1 else '',
            'image_choice_c': image_choices[2] if len(image_choices) > 2 else '',
            'image_choice_d': image_choices[3] if len(image_choices) > 3 else ''
        }
        
        rows.append(row)
    
    return rows

def main():
    print("🔍 Extracting Math Module 1 questions...")
    
    questions = extract_math_questions()
    
    print(f"\n✅ Found {len(questions)} questions")
    
    # Show summary
    for q in questions[:5]:
        print(f"\nQuestion {q['number']}:")
        print(f"  Text: {q['text'][:80]}...")
        print(f"  Choices: {len(q['choices'])}")
        if 'images' in q:
            print(f"  Images: {len(q['images'])}")
    
    # Create CSV rows
    csv_rows = create_csv_rows(questions)
    
    # Save to JSON for review
    with open('bulk-import/math-questions-final.json', 'w') as f:
        json.dump({
            'questions': questions,
            'csv_rows': csv_rows
        }, f, indent=2)
    
    # Also add to CSV file
    csv_file = 'bulk-import/math-questions.csv'
    if csv_rows:
        fieldnames = list(csv_rows[0].keys())
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)
        
        print(f"\n✅ Saved to:")
        print(f"   - {csv_file}")
        print(f"   - math-questions-final.json")
        print(f"\n📝 Next: Review and add correct answers/explanations")
        print(f"   Then merge into bulk-import/questions.csv")

if __name__ == "__main__":
    main()

