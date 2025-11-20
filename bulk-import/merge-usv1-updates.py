#!/usr/bin/env python3
"""
Merge newly imported US v1 questions with existing ones
Update existing questions with complete text and images
"""

import json
from pathlib import Path
from collections import defaultdict

def load_database():
    """Load database"""
    db_path = Path("questions-database.json")
    with open(db_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_questions_by_test(database, test_id):
    """Find all questions for a test"""
    return [q for q in database if q.get('testId') == test_id]

def group_questions_by_module_and_number(questions):
    """Group questions by module and question number"""
    grouped = defaultdict(dict)
    for q in questions:
        module = q.get('module', '')
        q_num = q.get('questionNumber')
        if module and q_num:
            grouped[module][q_num] = q
    return grouped

def merge_question_data(old_q, new_q):
    """Merge new question data into old question, keeping old ID"""
    merged = old_q.copy()
    
    # Update text if new one is longer/more complete
    new_text = new_q.get('questionText', '').strip()
    old_text = old_q.get('questionText', '').strip()
    if len(new_text) > len(old_text) * 0.8:  # New text is substantial
        merged['questionText'] = new_text
    
    # Update choices if old ones are empty/invalid
    old_choices = old_q.get('choices', [])
    new_choices = new_q.get('choices', [])
    
    if new_choices and (not old_choices or any(c == '' or c == '-' for c in old_choices)):
        merged['choices'] = new_choices
    
    # Update image URL if missing
    if not merged.get('imageUrl') and new_q.get('imageUrl'):
        merged['imageUrl'] = new_q.get('imageUrl')
    
    # Update hasImageChoices
    if new_q.get('hasImageChoices'):
        merged['hasImageChoices'] = True
        if new_choices:
            merged['choices'] = new_choices
    
    # Update questionType if missing
    if not merged.get('questionType') and new_q.get('questionType'):
        merged['questionType'] = new_q.get('questionType')
    
    return merged

def main():
    print("="*80)
    print("🔄 MERGING US V1 QUESTION UPDATES")
    print("="*80)
    
    database = load_database()
    
    # Find all US v1 questions (old and new)
    all_usv1 = find_questions_by_test(database, 'usv1')
    print(f"📊 Found {len(all_usv1)} US v1 questions total")
    
    # Group by module and question number
    grouped = group_questions_by_module_and_number(all_usv1)
    
    # Find duplicates (same module + question number)
    duplicates = []
    for module, questions in grouped.items():
        if len(questions) > 1:
            duplicates.append((module, questions))
    
    if not duplicates:
        print("✅ No duplicates found - all questions are unique")
        return
    
    print(f"\n🔍 Found duplicates in {len(duplicates)} modules")
    
    # Merge duplicates
    questions_to_remove = []
    questions_to_update = []
    
    for module, questions_dict in duplicates:
        print(f"\n📝 Processing {module}:")
        
        # Sort by ID (oldest first)
        sorted_qs = sorted(questions_dict.values(), key=lambda x: x.get('id', 0))
        
        # Keep the first (oldest) question, merge others into it
        base_question = sorted_qs[0]
        print(f"  Keeping Q{base_question.get('questionNumber')} (ID: {base_question.get('id')})")
        
        for other_q in sorted_qs[1:]:
            print(f"  Merging Q{other_q.get('questionNumber')} (ID: {other_q.get('id')}) into base")
            
            # Merge data
            base_question = merge_question_data(base_question, other_q)
            questions_to_remove.append(other_q.get('id'))
        
        questions_to_update.append(base_question)
    
    # Update database
    print(f"\n💾 Updating database...")
    
    # Remove duplicates
    database = [q for q in database if q.get('id') not in questions_to_remove]
    print(f"  ✓ Removed {len(questions_to_remove)} duplicate questions")
    
    # Update merged questions
    id_to_question = {q.get('id'): q for q in database}
    updated_count = 0
    
    for updated_q in questions_to_update:
        q_id = updated_q.get('id')
        if q_id in id_to_question:
            # Find index in database
            for i, q in enumerate(database):
                if q.get('id') == q_id:
                    database[i] = updated_q
                    updated_count += 1
                    break
    
    print(f"  ✓ Updated {updated_count} questions with merged data")
    
    # Save database
    db_path = Path("questions-database.json")
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Database updated successfully!")
    print(f"   • Removed: {len(questions_to_remove)} duplicates")
    print(f"   • Updated: {updated_count} questions")
    print(f"   • Total US v1 questions: {len(find_questions_by_test(database, 'usv1'))}")

if __name__ == "__main__":
    main()

