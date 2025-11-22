import json
import csv
import shutil
from pathlib import Path

print("🚀 Starting bulk import...")

# Load existing questions
try:
    with open('questions-database.json', 'r', encoding='utf-8') as f:
        all_questions = json.load(f)
    print(f"📚 Loaded {len(all_questions)} existing questions")
except FileNotFoundError:
    all_questions = []
    print("📚 Starting with empty database")

# Read CSV file
new_questions = []
csv_path = 'bulk-import/questions.csv'

try:
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):  # Start at 2 because row 1 is headers
            try:
                # Get next ID
                next_id = max([q['id'] for q in all_questions]) + 1 if all_questions else 1
                
                # ===== IMAGE HANDLING =====
                image_path = None
                image_caption = None
                
                image_name = row.get('image_name', '').strip()
                if image_name:  # If image exists
                    source_image = Path(f"bulk-import/images/{image_name}")
                    target_folder = Path("images/2025-03/asiav1")
                    target_folder.mkdir(parents=True, exist_ok=True)
                    target_image = target_folder / image_name
                    
                    # Copy image to correct location
                    if source_image.exists():
                        shutil.copy(source_image, target_image)
                        image_path = f"images/2025-03/asiav1/{image_name}"
                        print(f"  ✅ Copied image: {image_name}")
                    else:
                        print(f"  ⚠️  Image not found: {image_name} (row {row_num})")
                
                # Get image caption if provided
                if row.get('image_caption', '').strip():
                    image_caption = row['image_caption'].strip()
                # ===== END IMAGE HANDLING =====
                
                # Convert A/B/C/D to 0/1/2/3
                correct_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
                correct_answer_str = row.get('correct_answer', '').upper().strip()
                correct_answer = correct_map.get(correct_answer_str, 0)
                
                # Check if choices are images (for math questions)
                has_image_choices = False
                choices = [
                    row.get('choice_a', '').strip(),
                    row.get('choice_b', '').strip(),
                    row.get('choice_c', '').strip(),
                    row.get('choice_d', '').strip()
                ]
                
                # Check if any choice is an image path
                if any(choice.startswith('images/') or choice.endswith(('.png', '.jpg', '.svg')) for choice in choices):
                    has_image_choices = True
                
                # Also check the has_image_choices column
                if row.get('has_image_choices', '').lower() in ['yes', 'true', '1']:
                    has_image_choices = True
                
                # Create question object
                question = {
                    "id": next_id,
                    "module": row.get('module', 'Reading and Writing Module 1'),
                    "questionNumber": int(row.get('question_number', row_num - 1)),
                    "totalQuestions": int(row.get('total_questions', 27)),
                    "date": row.get('date', '2025-03'),
                    "region": row.get('region', 'Asia'),
                    "testNumber": int(row.get('test_number', 1)),
                    "testName": row.get('test_name', '2025-03 Asia Test 1'),
                    "questionText": row.get('question_text', '').strip(),
                    "prompt": row.get('prompt', 'Which choice completes the text?').strip(),
                    "choices": choices,
                    "correctAnswer": correct_answer,
                    "explanation": row.get('explanation', '').strip(),
                    "difficulty": row.get('difficulty', 'medium'),
                    "topic": row.get('topic', 'vocabulary'),
                    "subject": row.get('subject', 'English')
                }
                
                # Add image info if image exists
                if image_path:
                    question["imageUrl"] = image_path
                    if image_caption:
                        question["imageCaption"] = image_caption
                
                # Add image choices flag
                if has_image_choices:
                    question["hasImageChoices"] = True
                
                new_questions.append(question)
                print(f"  ✅ Added question {question['questionNumber']}")
                
            except Exception as e:
                print(f"  ❌ Error processing row {row_num}: {e}")
                continue

except FileNotFoundError:
    print(f"❌ Error: Could not find {csv_path}")
    print("   Make sure you have a 'bulk-import' folder with 'questions.csv' inside")
    exit(1)
except Exception as e:
    print(f"❌ Error reading CSV: {e}")
    exit(1)

# Add new questions to database
all_questions.extend(new_questions)

# Save everything
try:
    with open('questions-database.json', 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Successfully added {len(new_questions)} questions!")
    print(f"📊 Total questions in database: {len(all_questions)}")
except Exception as e:
    print(f"❌ Error saving database: {e}")
    exit(1)

