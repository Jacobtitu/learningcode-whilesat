#!/usr/bin/env python3
"""
Create question structure for Asia v6 from extracted images
Since PDF is image-based, creates placeholder structure based on standard SAT format
"""

import json
from pathlib import Path

def create_asiav6_structure():
    """Create question structure for Asia v6"""
    
    # Standard SAT structure: 4 modules
    modules = [
        {
            'name': 'Reading and Writing Module 1',
            'subject': 'Reading',
            'total_questions': 27,
            'start_page': 1,  # Approximate - adjust based on actual PDF
            'end_page': 25
        },
        {
            'name': 'Math Module 1',
            'subject': 'Math',
            'total_questions': 22,
            'start_page': 26,
            'end_page': 50
        },
        {
            'name': 'Reading and Writing Module 2',
            'subject': 'Reading',
            'total_questions': 27,
            'start_page': 51,
            'end_page': 75
        },
        {
            'name': 'Math Module 2',
            'subject': 'Math',
            'total_questions': 22,
            'start_page': 76,
            'end_page': 97
        }
    ]
    
    # Load image mapping if available
    image_mapping_file = Path("images/2025-03/asiav6/image-mapping.json")
    images_by_page = {}
    
    if image_mapping_file.exists():
        with open(image_mapping_file, 'r') as f:
            mapping_data = json.load(f)
            images_by_page = mapping_data.get('images_by_page', {})
    
    # Read existing database
    db_path = Path("questions-database.json")
    with open(db_path, 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    # Find next ID
    max_id = max((q.get('id', 0) for q in database), default=0)
    
    # Create questions for each module
    questions = []
    test_name = "2025-03 Asia Test 6"
    date = "2025-03"
    region = "Asia"
    test_number = 6
    test_id = "asiav6"
    
    for module in modules:
        module_name = module['name']
        subject = module['subject']
        total_q = module['total_questions']
        
        print(f"Creating {module_name} ({total_q} questions)...")
        
        for q_num in range(1, total_q + 1):
            # Estimate page number (rough approximation)
            pages_per_q = (module['end_page'] - module['start_page']) / total_q
            estimated_page = int(module['start_page'] + (q_num - 1) * pages_per_q)
            
            # Find images for this page
            page_images = images_by_page.get(str(estimated_page), [])
            
            # Determine if grid-in or multiple choice
            # Math questions 16-22 are usually grid-in
            is_grid_in = (subject == 'Math' and q_num >= 16)
            
            question = {
                "id": max_id + len(questions) + 1,
                "module": module_name,
                "questionNumber": q_num,
                "totalQuestions": total_q,
                "date": date,
                "region": region,
                "testNumber": test_number,
                "testName": test_name,
                "questionText": "",  # To be filled manually or with OCR
                "prompt": "",
                "difficulty": "medium",
                "topic": "general",
                "subject": subject,
                "explanation": "",
                "hasImageChoices": False,
                "imageUrl": "",
                "choices": [] if is_grid_in else ["", "", "", ""],
                "questionType": "grid-in" if is_grid_in else "multiple-choice",
                "correctAnswer": 0 if not is_grid_in else "",
                "testId": test_id
            }
            
            # Add image if found
            if page_images and len(page_images) > 0:
                if len(page_images) >= 4:
                    # Likely image choices
                    question['hasImageChoices'] = True
                    question['choices'] = [
                        f"images/{date}/{test_id}/{img['filename']}"
                        for img in page_images[:4]
                    ]
                elif len(page_images) == 1:
                    # Single image
                    question['imageUrl'] = f"images/{date}/{test_id}/{page_images[0]['filename']}"
            
            questions.append(question)
    
    # Add to database
    database.extend(questions)
    
    # Save database
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Created {len(questions)} placeholder questions")
    print(f"   Added to questions-database.json")
    print(f"\n📝 Next steps:")
    print(f"   1. Review questions in database (testId: {test_id})")
    print(f"   2. Fill in questionText for each question")
    print(f"   3. Add correct answers from answer key")
    print(f"   4. Verify image assignments")

if __name__ == "__main__":
    create_asiav6_structure()

