#!/usr/bin/env python3
"""
Complete fix for US v1 questions - extract from PDF and update database properly
"""

import fitz  # PyMuPDF
import json
import re
from pathlib import Path
from collections import defaultdict

def load_database():
    """Load database"""
    db_path = Path("questions-database.json")
    with open(db_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_usv1_questions(database):
    """Find all US v1 questions, grouped by module and question number"""
    usv1_qs = [q for q in database if q.get('testId') == 'usv1']
    
    # Group by module + question number
    grouped = defaultdict(list)
    for q in usv1_qs:
        key = (q.get('module'), q.get('questionNumber'))
        grouped[key].append(q)
    
    return grouped, usv1_qs

def extract_text_from_pdf(pdf_path):
    """Extract full text from PDF"""
    doc = fitz.open(pdf_path)
    full_text = {}
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        full_text[page_num + 1] = text
    
    doc.close()
    return full_text

def update_question_from_pdf_text(db_question, pdf_text_by_page):
    """Update a database question with complete text from PDF"""
    updated = False
    
    # Get the question's page if available, or search all pages
    # For now, we'll search all text for this question's number
    q_num = db_question.get('questionNumber')
    module = db_question.get('module', '')
    
    if not q_num:
        return db_question, False
    
    # Search PDF text for this question
    for page_num, text in pdf_text_by_page.items():
        # Look for question number in text
        pattern = rf'^{q_num}\s+(.+?)(?=^{q_num + 1}\s+|$)'
        match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
        
        if match:
            pdf_text = match.group(1).strip()
            db_text = db_question.get('questionText', '').strip()
            
            # If PDF text is more complete, update
            if len(pdf_text) > len(db_text) * 0.8:
                db_question['questionText'] = pdf_text
                updated = True
            
            # Extract choices
            choices = []
            choice_pattern = r'([A-D])\)\s*(.+?)(?=[A-D]\)|$)'
            for cm in re.finditer(choice_pattern, pdf_text, re.DOTALL):
                choice_text = cm.group(2).strip()
                # Clean up choice text
                choice_text = re.sub(r'\s+', ' ', choice_text)
                choices.append(choice_text)
            
            if choices and (not db_question.get('choices') or any(c == '' or c == '-' for c in db_question.get('choices', []))):
                db_question['choices'] = choices
                updated = True
            
            break
    
    return db_question, updated

def main():
    print("="*80)
    print("🔧 COMPLETE US V1 QUESTION FIXER")
    print("="*80)
    
    pdf_path = Path("bulk-import/202503usv1.pdf")
    if not pdf_path.exists():
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    # Load database
    database = load_database()
    grouped, all_usv1 = find_usv1_questions(database)
    
    print(f"📊 Found {len(all_usv1)} US v1 questions in database")
    print(f"   Across {len(grouped)} unique module/question combinations")
    
    # Extract PDF text
    print("\n📄 Extracting text from PDF...")
    pdf_text = extract_text_from_pdf(str(pdf_path))
    print(f"   ✓ Extracted text from {len(pdf_text)} pages")
    
    # Update each question
    print("\n🔄 Updating questions with complete text...")
    updated_count = 0
    
    for (module, q_num), questions in grouped.items():
        # Use the question with the lowest ID (original)
        questions.sort(key=lambda x: x.get('id', 0))
        q = questions[0]
        
        updated_q, was_updated = update_question_from_pdf_text(q, pdf_text)
        
        if was_updated:
            # Update in database
            for i, db_q in enumerate(database):
                if db_q.get('id') == updated_q.get('id'):
                    database[i] = updated_q
                    updated_count += 1
                    print(f"   ✓ Updated Q{q_num} ({module})")
                    break
    
    # Remove duplicates (keep only the first question for each module/q_num)
    print(f"\n🗑️  Removing duplicates...")
    ids_to_remove = []
    for (module, q_num), questions in grouped.items():
        if len(questions) > 1:
            # Keep first, remove others
            questions.sort(key=lambda x: x.get('id', 0))
            for q in questions[1:]:
                ids_to_remove.append(q.get('id'))
    
    database = [q for q in database if q.get('id') not in ids_to_remove]
    print(f"   ✓ Removed {len(ids_to_remove)} duplicate questions")
    
    # Save database
    db_path = Path("questions-database.json")
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Complete!")
    print(f"   • Updated: {updated_count} questions")
    print(f"   • Removed: {len(ids_to_remove)} duplicates")
    print(f"   • Total US v1 questions: {len([q for q in database if q.get('testId') == 'usv1'])}")

if __name__ == "__main__":
    main()

