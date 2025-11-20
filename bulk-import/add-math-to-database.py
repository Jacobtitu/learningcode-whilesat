#!/usr/bin/env python3
"""
Add Math questions directly to questions-database.json
"""

import json
import csv
from pathlib import Path

# Load existing database
with open('questions-database.json', 'r', encoding='utf-8') as f:
    all_questions = json.load(f)

# Load math questions CSV
math_csv = 'bulk-import/math-module1-questions.csv'

print(f"📚 Current database has {len(all_questions)} questions")
print(f"📄 Loading Math questions from {math_csv}...\n")

# Get next ID
next_id = max([q['id'] for q in all_questions]) + 1 if all_questions else 1

# Read math questions
math_questions = []
with open(math_csv, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        q_num = int(row['question_number'])
        
        # Convert A/B/C/D to 0/1/2/3
        correct_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
        correct_answer = correct_map.get(row.get('correct_answer', '').upper().strip(), 0)
        
        # Handle image choices
        choices = [
            row.get('choice_a', '').strip(),
            row.get('choice_b', '').strip(),
            row.get('choice_c', '').strip(),
            row.get('choice_d', '').strip()
        ]
        
        has_image_choices = row.get('has_image_choices', '').lower() == 'yes'
        
        # Create question object
        question = {
            "id": next_id,
            "module": "Math Module 1",
            "questionNumber": q_num,
            "totalQuestions": 22,
            "date": "2025-03",
            "region": "Asia",
            "testNumber": 1,
            "testName": "2025-03 Asia Test 1",
            "questionText": row.get('question_text', '').strip(),
            "prompt": row.get('prompt', '').strip() or "",
            "choices": choices,
            "correctAnswer": correct_answer,
            "explanation": row.get('explanation', '').strip() or "",
            "difficulty": row.get('difficulty', 'medium'),
            "topic": row.get('topic', 'math'),
            "subject": "Math"
        }
        
        # Add image if exists
        image_name = row.get('image_name', '').strip()
        if image_name:
            question["imageUrl"] = f"images/2025-03/asiav1/{image_name}"
            if row.get('image_caption'):
                question["imageCaption"] = row.get('image_caption')
        
        # Add image choices flag
        if has_image_choices:
            question["hasImageChoices"] = True
        
        math_questions.append(question)
        next_id += 1

print(f"✅ Prepared {len(math_questions)} Math questions\n")

# Show first few
print("First 3 questions:")
for q in math_questions[:3]:
    print(f"\n  Question {q['questionNumber']}: {q['questionText'][:60]}...")
    print(f"    Choices: {len(q['choices'])}")
    if 'imageUrl' in q:
        print(f"    Image: {q['imageUrl']}")
    if q.get('hasImageChoices'):
        print(f"    Has image choices: Yes")

# Add to database
all_questions.extend(math_questions)

# Save
with open('questions-database.json', 'w', encoding='utf-8') as f:
    json.dump(all_questions, f, indent=2, ensure_ascii=False)

print(f"\n✅ Added {len(math_questions)} Math questions to database!")
print(f"📊 Total questions now: {len(all_questions)}")
print(f"\n⚠️  Note: You still need to:")
print(f"   1. Add correct answers (currently all set to A)")
print(f"   2. Add explanations")
print(f"   3. Rename images to match (e.g., q2-graph.png)")
print(f"   4. Copy images to images/2025-03/asiav1/")

