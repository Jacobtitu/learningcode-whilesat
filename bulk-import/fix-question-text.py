#!/usr/bin/env python3
"""
Quick fix for questions with incomplete text extraction
"""

import json

# Load database
with open('questions-database.json', 'r') as f:
    db = json.load(f)

# Fix Q14 text
for q in db:
    if q.get('module') == 'Math Module 1' and q['questionNumber'] == 14:
        q['questionText'] = 'f(x)= -10 (2)^(x/3). Which table gives four values of x and their corresponding values of f(x) for the given exponential function?'
        print(f"✅ Fixed Q14 text")

# Add more fixes here as needed
# Example:
# for q in db:
#     if q.get('module') == 'Math Module 1' and q['questionNumber'] == 17:
#         q['questionText'] = 'Your correct question text here'

# Save
with open('questions-database.json', 'w') as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print("\n✅ Question texts updated!")

