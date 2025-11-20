#!/usr/bin/env python3
"""
Import Math Module 2 from PDF
"""

import fitz
import json
import shutil
import re
from pathlib import Path
from collections import defaultdict

# Answer key from PDF page 34 for Math Module 2
ANSWER_KEY = {
    1: "A",
    2: "5780",    # Grid-in
    3: "B",
    4: "D",
    5: "A",
    6: "C",
    7: "C",
    8: "B",
    9: "D",
    10: "6.4 or 32/5",  # Grid-in  
    11: "C",
    12: "D",
    13: "C",
    14: "A",
    15: "7.5 or 15/2",  # Grid-in
    16: "D",
    17: "2",     # Grid-in
    18: "C",
    19: "B",
    20: "B",
    21: "A",
    22: "C",
}

def extract_module2_questions():
    pdf = fitz.open('bulk-import/202503asiav1 (1).pdf')
    
    questions = {}
    current_q = None
    
    # Math Module 2 is on pages 27-33 (index 26-32)
    for page_num in range(26, 33):
        page = pdf[page_num]
        text = page.get_text()
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Find question numbers
            if re.match(r'^\d+$', stripped):
                q_num = int(stripped)
                
                if 1 <= q_num <= 22:
                    # Save previous
                    if current_q:
                        questions[current_q['number']] = current_q
                    
                    # Start new
                    current_q = {
                        'number': q_num,
                        'text_lines': [],
                        'page': page_num
                    }
            
            elif current_q and stripped:
                if 'Module' not in stripped and 'QUESTIONS' not in stripped:
                    current_q['text_lines'].append(stripped)
    
    # Save last
    if current_q:
        questions[current_q['number']] = current_q
    
    # Combine text
    for q_num, q in questions.items():
        q['text'] = ' '.join(q['text_lines']).strip()
        # Remove embedded answer choices
        q['text'] = re.sub(r'\s*A\)\s+.*?\s+D\)\s+.*?$', '', q['text'], flags=re.DOTALL).strip()
    
    pdf.close()
    return questions

def add_to_database():
    # Load database
    with open('questions-database.json', 'r') as f:
        db = json.load(f)
    
    # Get next ID
    next_id = max(q['id'] for q in db) + 1
    
    # Extract questions
    questions = extract_module2_questions()
    
    print("📝 IMPORTING MATH MODULE 2:")
    print("=" * 80)
    
    added = 0
    for q_num in sorted(questions.keys()):
        q = questions[q_num]
        answer_key = ANSWER_KEY.get(q_num, "A")
        
        # Determine if grid-in
        is_grid_in = isinstance(answer_key, str) and (answer_key.isdigit() or '/' in answer_key or '.' in answer_key) and answer_key not in ['A', 'B', 'C', 'D']
        
        question = {
            "id": next_id,
            "module": "Math Module 2",
            "questionNumber": q_num,
            "totalQuestions": 22,
            "date": "2025-03",
            "region": "Asia",
            "testNumber": 1,
            "testName": "2025-03 Asia Test 1",
            "questionText": q['text'],
            "prompt": "",
            "difficulty": "medium",
            "topic": "general",
            "subject": "Math"
        }
        
        if is_grid_in:
            question['questionType'] = 'grid-in'
            question['correctAnswer'] = answer_key
            question['choices'] = []
        else:
            question['questionType'] = 'multiple-choice'
            question['choices'] = ["A", "B", "C", "D"]
            question['correctAnswer'] = ord(answer_key) - ord('A')
        
        question['explanation'] = ""
        
        db.append(question)
        next_id += 1
        added += 1
        
        status = "GRID-IN" if is_grid_in else "MC"
        answer_display = answer_key if is_grid_in else answer_key
        print(f"✅ Q{q_num:2d} [{status}]: Answer = {answer_display}")
    
    # Save
    with open('questions-database.json', 'w') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Added {added} Math Module 2 questions!")

if __name__ == "__main__":
    add_to_database()

