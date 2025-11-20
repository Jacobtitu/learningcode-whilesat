#!/usr/bin/env python3
"""
Extract Math questions from PDF and match with images
"""

import fitz  # PyMuPDF
import json
import re
from pathlib import Path

def extract_math_questions_from_pdf(pdf_path):
    """Extract all math questions from PDF"""
    doc = fitz.open(pdf_path)
    
    questions = []
    current_question = None
    
    print("📄 Extracting questions from PDF...")
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        
        # Look for question patterns
        # Questions usually start with a number followed by text
        question_pattern = r'(\d+)\s+(.+?)(?=\d+\s+|$)'
        
        # Check if this page has math content
        if 'Math Module 1' in text or any(char.isdigit() for char in text[:200]):
            # Try to extract questions
            matches = re.finditer(r'^(\d+)\s+(.+?)(?=^\d+\s+|$)', text, re.MULTILINE | re.DOTALL)
            
            for match in matches:
                q_num = int(match.group(1))
                q_text = match.group(2).strip()
                
                # Extract choices (A, B, C, D)
                choices = []
                choice_pattern = r'([A-D])\)\s*(.+?)(?=[A-D]\)|$)'
                choice_matches = re.finditer(choice_pattern, q_text, re.DOTALL)
                
                for choice_match in choice_matches:
                    choices.append(choice_match.group(2).strip())
                
                # Find images on this page
                images_on_page = page.get_images()
                
                questions.append({
                    'question_number': q_num,
                    'page': page_num + 1,
                    'text': q_text[:500],  # First 500 chars
                    'full_text': q_text,
                    'choices': choices,
                    'images_count': len(images_on_page)
                })
    
    doc.close()
    return questions

def match_images_to_questions(pdf_path, questions):
    """Match extracted images to questions based on page numbers"""
    images_folder = Path('bulk-import/images')
    images = list(images_folder.glob('*.png'))
    
    # Group images by page
    images_by_page = {}
    for img in images:
        # Extract page number from filename
        match = re.search(r'page(\d+)_img(\d+)', img.name)
        if match:
            page_num = int(match.group(1))
            img_num = int(match.group(2))
            if page_num not in images_by_page:
                images_by_page[page_num] = []
            images_by_page[page_num].append({
                'filename': img.name,
                'path': str(img),
                'img_num': img_num
            })
    
    # Match questions with images
    matched = []
    for q in questions:
        page = q['page']
        if page in images_by_page:
            q['images'] = images_by_page[page]
        else:
            q['images'] = []
        matched.append(q)
    
    return matched

def create_csv_rows(questions_with_images):
    """Create CSV rows for import"""
    rows = []
    
    for q in questions_with_images:
        q_num = q['question_number']
        
        # Extract question text (before choices)
        text = q['full_text']
        # Remove choice markers
        text = re.sub(r'[A-D]\)\s*', '', text)
        text = text.strip()
        
        # Get choices
        choices = q['choices']
        if len(choices) < 4:
            choices = ['', '', '', '']  # Fill empty if not found
        
        # Determine image filename
        image_name = ''
        if q['images']:
            # Use first image, rename suggestion
            if len(q['images']) == 4:
                # Math question with 4 graph choices
                image_name = ''  # Will use image choices instead
            elif len(q['images']) == 1:
                image_name = f"q{q_num}-graph.png"
            else:
                image_name = f"q{q_num}-img.png"
        
        # Check if this is a math question with image choices
        has_image_choices = len(q['images']) == 4 and q_num == 1
        
        row = {
            'question_number': q_num,
            'question_text': text[:200],  # Truncate for CSV
            'prompt': '',
            'choice_a': choices[0] if len(choices) > 0 else '',
            'choice_b': choices[1] if len(choices) > 1 else '',
            'choice_c': choices[2] if len(choices) > 2 else '',
            'choice_d': choices[3] if len(choices) > 3 else '',
            'correct_answer': '',  # Need to fill manually
            'explanation': '',  # Need to fill manually
            'image_name': image_name,
            'image_caption': '',
            'difficulty': 'medium',
            'topic': 'math',
            'module': 'Math Module 1',
            'date': '2025-03',
            'region': 'Asia',
            'test_number': 1,
            'test_name': '2025-03 Asia Test 1',
            'subject': 'Math'
        }
        
        rows.append(row)
    
    return rows

def main():
    pdf_path = 'bulk-import/202503asiav1 (1).pdf'
    
    if not Path(pdf_path).exists():
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    # Extract questions
    questions = extract_math_questions_from_pdf(pdf_path)
    
    if not questions:
        print("⚠️  Could not extract questions automatically")
        print("   Let me try a different approach...")
        
        # Try simpler extraction - just get text from math pages
        doc = fitz.open(pdf_path)
        print("\n📄 Pages with Math content:")
        for page_num in range(19, min(26, len(doc))):  # Pages 20-25 likely have math
            page = doc[page_num]
            text = page.get_text()
            if text.strip():
                print(f"\n{'='*60}")
                print(f"Page {page_num + 1}:")
                print(text[:800])
        doc.close()
        return
    
    # Match with images
    questions_with_images = match_images_to_questions(pdf_path, questions)
    
    # Create CSV rows
    csv_rows = create_csv_rows(questions_with_images)
    
    # Save to JSON for review
    output_file = 'bulk-import/extracted-questions.json'
    with open(output_file, 'w') as f:
        json.dump({
            'questions': questions_with_images,
            'csv_rows': csv_rows
        }, f, indent=2)
    
    print(f"\n✅ Extracted {len(questions)} questions")
    print(f"📝 Saved to: {output_file}")
    print("\nNext: Review extracted-questions.json and add to CSV")

if __name__ == "__main__":
    main()

