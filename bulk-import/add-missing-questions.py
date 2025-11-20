#!/usr/bin/env python3
"""
Quick script to add missing question texts
Edit the MISSING_QUESTIONS dictionary below with your question texts
"""

import json

# ============================================================================
# EDIT THESE - Add your question texts here:
# ============================================================================

MISSING_QUESTIONS = {
    10: "ADD Q10 QUESTION TEXT HERE",
    11: "ADD Q11 QUESTION TEXT HERE",
    # Add more as needed:
    # 17: "Your question text here",
}

# ============================================================================

# Load database
with open('questions-database.json', 'r') as f:
    db = json.load(f)

# Update questions
updated = []
for q in db:
    if q.get('module') == 'Math Module 1':
        q_num = q['questionNumber']
        if q_num in MISSING_QUESTIONS:
            new_text = MISSING_QUESTIONS[q_num]
            if 'ADD Q' not in new_text and 'HERE' not in new_text:
                q['questionText'] = new_text
                updated.append(q_num)
                print(f"✅ Q{q_num}: Updated")
            else:
                print(f"⚠️  Q{q_num}: Still needs text (edit this script first)")

# Save
if updated:
    with open('questions-database.json', 'w') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Updated {len(updated)} questions: {updated}")
else:
    print("\n⚠️  No questions updated. Edit the MISSING_QUESTIONS dictionary first!")

print("\n📝 To use this script:")
print("   1. Edit this file: bulk-import/add-missing-questions.py")
print("   2. Replace 'ADD Q10 QUESTION TEXT HERE' with actual question")
print("   3. Run: python3 bulk-import/add-missing-questions.py")

