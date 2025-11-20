#!/usr/bin/env python3
"""
Extract all questions from US v1 PDF and compare with database
Fix missing text and images
"""

import fitz  # PyMuPDF
import json
import re
from pathlib import Path
from collections import defaultdict

def extract_full_text_from_pdf(pdf_path):
    """Extract all text from PDF preserving structure"""
    doc = fitz.open(pdf_path)
    full_text = {}
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        full_text[page_num + 1] = text
    
    doc.close()
    return full_text

def extract_questions_from_pdf(pdf_path):
    """Extract all questions with full text from PDF"""
    doc = fitz.open(pdf_path)
    questions = {}
    current_module = None
    
    print("📄 Extracting questions from PDF...")
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        
        # Detect module
        if 'Reading and Writing Module 1' in text:
            current_module = 'Reading and Writing Module 1'
        elif 'Reading and Writing Module 2' in text:
            current_module = 'Reading and Writing Module 2'
        elif 'Math Module 1' in text:
            current_module = 'Math Module 1'
        elif 'Math Module 2' in text:
            current_module = 'Math Module 2'
        
        # Extract images on this page
        images = page.get_images()
        image_rects = []
        for img_idx, img in enumerate(images):
            try:
                xref = img[0]
                rects = page.get_image_rects(xref)
                if rects:
                    image_rects.append({
                        'xref': xref,
                        'rect': rects[0],
                        'index': img_idx
                    })
            except:
                pass
        
        # Try to find questions on this page
        # Look for question numbers
        lines = text.split('\n')
        for i, line in enumerate(lines):
            # Match question number pattern
            q_match = re.match(r'^(\d+)\s+(.+)$', line.strip())
            if q_match:
                q_num = int(q_match.group(1))
                if 1 <= q_num <= 27:  # Valid question range
                    # Collect full question text
                    question_text = []
                    question_text.append(q_match.group(2))
                    
                    # Collect following lines until next question or end
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].strip()
                        # Stop if we hit another question number
                        if re.match(r'^\d+\s+', next_line):
                            break
                        if next_line:
                            question_text.append(next_line)
                        j += 1
                    
                    full_q_text = ' '.join(question_text)
                    
                    # Extract choices if multiple choice
                    choices = []
                    choice_pattern = r'([A-D])\)\s*(.+?)(?=[A-D]\)|$)'
                    choice_matches = re.finditer(choice_pattern, full_q_text, re.DOTALL)
                    for cm in choice_matches:
                        choices.append(cm.group(2).strip())
                    
                    # Check if grid-in (no choices or specific pattern)
                    is_grid_in = len(choices) == 0 or 'Enter your answer' in full_q_text.lower()
                    
                    questions[q_num] = {
                        'number': q_num,
                        'module': current_module,
                        'text': full_q_text,
                        'choices': choices,
                        'is_grid_in': is_grid_in,
                        'page': page_num + 1,
                        'images': []
                    }
    
    doc.close()
    return questions

def load_database():
    """Load current database"""
    db_path = Path("questions-database.json")
    if db_path.exists():
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def find_usv1_questions(database):
    """Find all US v1 questions in database"""
    usv1_questions = {}
    for q in database:
        if q.get('testId') == 'usv1':
            q_num = q.get('questionNumber')
            if q_num:
                usv1_questions[q_num] = q
    return usv1_questions

def compare_and_fix(pdf_questions, db_questions, database):
    """Compare PDF questions with database and fix missing text/images"""
    fixes = []
    
    for q_num, pdf_q in pdf_questions.items():
        db_q = db_questions.get(q_num)
        
        if not db_q:
            print(f"⚠️  Q{q_num}: Missing from database!")
            fixes.append({
                'number': q_num,
                'action': 'add',
                'data': pdf_q
            })
            continue
        
        # Check if text is missing or incomplete
        db_text = db_q.get('questionText', '').strip()
        pdf_text = pdf_q.get('text', '').strip()
        
        if len(pdf_text) > len(db_text) * 1.2:  # PDF text is significantly longer
            print(f"📝 Q{q_num}: Text appears incomplete")
            fixes.append({
                'number': q_num,
                'action': 'update_text',
                'old_text': db_text[:100] + '...',
                'new_text': pdf_text[:100] + '...',
                'id': db_q.get('id')
            })
        
        # Check if choices are missing
        db_choices = db_q.get('choices', [])
        pdf_choices = pdf_q.get('choices', [])
        
        if pdf_choices and not db_choices:
            print(f"📋 Q{q_num}: Missing choices")
            fixes.append({
                'number': q_num,
                'action': 'add_choices',
                'choices': pdf_choices,
                'id': db_q.get('id')
            })
        elif pdf_choices and db_choices:
            # Check if choices are empty strings
            if any(c == '' or c == '-' for c in db_choices):
                print(f"📋 Q{q_num}: Empty/invalid choices")
                fixes.append({
                    'number': q_num,
                    'action': 'update_choices',
                    'old_choices': db_choices,
                    'new_choices': pdf_choices,
                    'id': db_q.get('id')
                })
        
        # Check if images are missing
        db_image = db_q.get('imageUrl', '')
        if 'shown' in pdf_text.lower() or 'figure' in pdf_text.lower() or 'graph' in pdf_text.lower():
            if not db_image:
                print(f"🖼️  Q{q_num}: Missing image (text suggests image needed)")
                fixes.append({
                    'number': q_num,
                    'action': 'needs_image',
                    'id': db_q.get('id')
                })
    
    return fixes, database

def apply_fixes(fixes, database):
    """Apply fixes to database"""
    print(f"\n🔧 Applying {len(fixes)} fixes...")
    
    for fix in fixes:
        q_id = fix.get('id')
        q_num = fix.get('number')
        action = fix.get('action')
        
        # Find question in database
        q_index = None
        for i, q in enumerate(database):
            if q.get('id') == q_id:
                q_index = i
                break
        
        if q_index is None:
            print(f"  ⚠️  Q{q_num}: Could not find question ID {q_id}")
            continue
        
        q = database[q_index]
        
        if action == 'update_text':
            q['questionText'] = fix['new_text']
            print(f"  ✓ Q{q_num}: Updated text")
        
        elif action == 'add_choices':
            q['choices'] = fix['choices']
            print(f"  ✓ Q{q_num}: Added choices")
        
        elif action == 'update_choices':
            q['choices'] = fix['new_choices']
            print(f"  ✓ Q{q_num}: Updated choices")
    
    return database

def main():
    pdf_path = "bulk-import/202503usv1.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    print("="*80)
    print("🔍 US V1 QUESTION FIXER")
    print("="*80)
    
    # Extract from PDF
    pdf_questions = extract_questions_from_pdf(pdf_path)
    print(f"✅ Extracted {len(pdf_questions)} questions from PDF")
    
    # Load database
    database = load_database()
    db_questions = find_usv1_questions(database)
    print(f"✅ Found {len(db_questions)} US v1 questions in database")
    
    # Compare and find fixes
    fixes, database = compare_and_fix(pdf_questions, db_questions, database)
    
    print(f"\n📊 Found {len(fixes)} issues to fix")
    
    if fixes:
        # Apply fixes
        database = apply_fixes(fixes, database)
        
        # Save database
        db_path = Path("questions-database.json")
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Database updated!")
    else:
        print("\n✅ No fixes needed!")

if __name__ == "__main__":
    main()

