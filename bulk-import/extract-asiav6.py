#!/usr/bin/env python3
"""
Improved extraction script for Asia v6 PDF
More accurate question and answer choice extraction
"""

import fitz  # PyMuPDF
import json
import re
import sys
from pathlib import Path
from collections import defaultdict

class AsiaV6Extractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.test_name = "2025-03 Asia Test 6"
        self.date = "2025-03"
        self.region = "Asia"
        self.test_number = 6
        self.test_id = "asiav6"
        
        # Storage
        self.modules = {}
        self.answer_key = {}
        self.images_by_page = defaultdict(list)
        self.all_questions = []
        
        # Folders
        self.image_output_folder = Path(f"images/{self.date}/{self.test_id}")
        self.image_output_folder.mkdir(parents=True, exist_ok=True)
        
        print("=" * 80)
        print(f"📚 ASIA V6 EXTRACTOR - Improved Accuracy")
        print("=" * 80)
    
    def detect_modules(self):
        """Detect all 4 modules in the PDF"""
        print("\n📚 Step 1: Detecting modules...")
        
        module_patterns = {
            'Reading and Writing Module 1': r'Reading and Writing Module 1',
            'Reading and Writing Module 2': r'Reading and Writing Module 2',
            'Math Module 1': r'Math Module 1',
            'Math Module 2': r'Math Module 2'
        }
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text = page.get_text()
            
            for module_name, pattern in module_patterns.items():
                if re.search(pattern, text, re.IGNORECASE):
                    if module_name not in self.modules:
                        self.modules[module_name] = {
                            'name': module_name,
                            'start_page': page_num,
                            'end_page': None,
                            'subject': 'Math' if 'Math' in module_name else 'Reading'
                        }
                        print(f"   ✓ Found {module_name} on page {page_num + 1}")
        
        # Set end pages
        module_list = sorted(self.modules.items(), key=lambda x: x[1]['start_page'])
        for i, (name, module) in enumerate(module_list):
            if i < len(module_list) - 1:
                next_module_start = module_list[i + 1][1]['start_page']
                module['end_page'] = next_module_start - 1
            else:
                # Last module ends before answer key
                module['end_page'] = len(self.doc) - 3
        
        print(f"   ✓ Detected {len(self.modules)} modules")
    
    def extract_answer_key(self):
        """Extract answer key from PDF"""
        print("\n🔑 Step 2: Extracting answer key...")
        
        for page_num in range(len(self.doc) - 3, len(self.doc)):
            page = self.doc[page_num]
            text = page.get_text()
            
            if 'Answer' in text or 'ANSWERS' in text:
                print(f"   ✓ Found answer key on page {page_num + 1}")
                
                lines = text.split('\n')
                current_module = None
                
                for line in lines:
                    # Detect module headers
                    if 'Module 1' in line:
                        if 'Math' in line:
                            current_module = 'Math Module 1'
                        elif 'Reading' in line or 'Writing' in line:
                            current_module = 'Reading and Writing Module 1'
                    elif 'Module 2' in line:
                        if 'Math' in line:
                            current_module = 'Math Module 2'
                        elif 'Reading' in line or 'Writing' in line:
                            current_module = 'Reading and Writing Module 2'
                    
                    # Parse answers: "1. A" or "1 A" or "1) A"
                    if current_module:
                        match = re.match(r'^(\d+)[\.\)]\s*([A-D]|\d+\.?\d*)$', line.strip())
                        if match:
                            q_num = int(match.group(1))
                            answer = match.group(2).strip()
                            
                            if current_module not in self.answer_key:
                                self.answer_key[current_module] = {}
                            
                            self.answer_key[current_module][q_num] = answer
        
        for module_name, answers in self.answer_key.items():
            print(f"   ✓ {module_name}: {len(answers)} answers")
    
    def extract_images(self):
        """Extract all images from PDF"""
        print("\n📸 Step 3: Extracting images...")
        
        total_images = 0
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    pix = fitz.Pixmap(self.doc, xref)
                    
                    if pix.n - pix.alpha < 4:
                        filename = f"202503asiav6_page{page_num + 1}_img{img_index + 1}.png"
                        filepath = self.image_output_folder / filename
                        pix.save(str(filepath))
                        
                        self.images_by_page[page_num].append({
                            'filename': filename,
                            'filepath': str(filepath),
                            'page': page_num,
                            'index': img_index
                        })
                        total_images += 1
                    
                    pix = None
                except Exception as e:
                    pass
        
        print(f"   ✓ Extracted {total_images} images")
    
    def clean_text(self, text):
        """Clean extracted text"""
        if not text:
            return ""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that break JSON
        text = text.replace('\x00', '')
        return text.strip()
    
    def extract_choices(self, text):
        """Extract answer choices from text"""
        choices = []
        
        # Pattern: A) ... B) ... C) ... D) ...
        pattern = r'([A-D])\)\s*([^A-D]+?)(?=[A-D]\)|$)'
        matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            choice_text = match.group(2).strip()
            # Clean up choice text
            choice_text = self.clean_text(choice_text)
            if choice_text:
                choices.append(choice_text)
        
        # If we found exactly 4 choices, return them
        if len(choices) == 4:
            return choices
        
        # Try alternative pattern: A. ... B. ... C. ... D. ...
        pattern2 = r'([A-D])\.\s*([^A-D]+?)(?=[A-D]\.|$)'
        matches2 = re.finditer(pattern2, text, re.DOTALL | re.IGNORECASE)
        choices2 = []
        for match in matches2:
            choice_text = match.group(2).strip()
            choice_text = self.clean_text(choice_text)
            if choice_text:
                choices2.append(choice_text)
        
        if len(choices2) == 4:
            return choices2
        
        return choices[:4] if len(choices) > 0 else []
    
    def remove_choices_from_text(self, text):
        """Remove answer choices from question text"""
        # Find where choices start
        # Look for A) followed by B) C) D)
        text_upper = text.upper()
        
        # Find A) position
        a_pos = text_upper.find('A)')
        if a_pos == -1:
            a_pos = text_upper.find('A.')
        
        if a_pos != -1:
            # Check if B) C) D) follow
            remaining = text_upper[a_pos:]
            if 'B)' in remaining or 'B.' in remaining:
                if 'C)' in remaining or 'C.' in remaining:
                    if 'D)' in remaining or 'D.' in remaining:
                        # Found all choices, remove from A) onwards
                        return text[:a_pos].strip()
        
        return text.strip()
    
    def extract_module_questions(self, module_name):
        """Extract questions for a module with improved accuracy"""
        module = self.modules[module_name]
        start_page = module['start_page']
        end_page = module['end_page']
        subject = module['subject']
        max_questions = 27 if subject == 'Reading' else 22
        
        print(f"\n📝 Step 4: Extracting {module_name} (pages {start_page+1}-{end_page+1})...")
        
        questions = {}
        current_q = None
        current_text_lines = []
        
        for page_num in range(start_page, end_page + 1):
            page = self.doc[page_num]
            text = page.get_text()
            lines = text.split('\n')
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                
                # Skip empty lines and headers
                if not stripped:
                    continue
                
                # Skip module headers
                if 'Module' in stripped and ('1' in stripped or '2' in stripped):
                    continue
                if 'QUESTIONS' in stripped or 'CONTINUE' in stripped:
                    continue
                
                # Check if this is a question number (standalone digit)
                if re.match(r'^\d+$', stripped):
                    q_num = int(stripped)
                    
                    if 1 <= q_num <= max_questions:
                        # Save previous question
                        if current_q:
                            # Combine text lines
                            full_text = ' '.join(current_text_lines).strip()
                            full_text = self.clean_text(full_text)
                            
                            # Extract choices
                            choices = self.extract_choices(full_text)
                            
                            # Remove choices from question text
                            question_text = self.remove_choices_from_text(full_text)
                            
                            current_q['questionText'] = question_text
                            current_q['choices'] = choices
                            
                            questions[current_q['number']] = current_q
                        
                        # Start new question
                        current_q = {
                            'number': q_num,
                            'module': module_name,
                            'page': page_num
                        }
                        current_text_lines = []
                        continue
                
                # Add to current question text
                if current_q and stripped:
                    current_text_lines.append(stripped)
        
        # Save last question
        if current_q:
            full_text = ' '.join(current_text_lines).strip()
            full_text = self.clean_text(full_text)
            choices = self.extract_choices(full_text)
            question_text = self.remove_choices_from_text(full_text)
            
            current_q['questionText'] = question_text
            current_q['choices'] = choices
            questions[current_q['number']] = current_q
        
        print(f"   ✓ Extracted {len(questions)} questions")
        return questions
    
    def match_images_to_questions(self, questions):
        """Match images to questions based on page numbers"""
        print("\n🖼️  Step 5: Matching images to questions...")
        
        for q_num, q in questions.items():
            page = q['page']
            
            # Check if there are images on this page or nearby pages
            images_for_q = []
            
            # Check current page
            if page in self.images_by_page:
                images_for_q.extend(self.images_by_page[page])
            
            # Check next page (questions often span pages)
            if page + 1 in self.images_by_page:
                images_for_q.extend(self.images_by_page[page + 1])
            
            # Determine if this is image choices or single image
            if len(images_for_q) >= 4:
                # Likely image choices
                q['hasImageChoices'] = True
                q['imageChoices'] = [img['filename'] for img in images_for_q[:4]]
                q['imageUrl'] = ""
            elif len(images_for_q) == 1:
                # Single image
                q['hasImageChoices'] = False
                q['imageUrl'] = f"images/{self.date}/{self.test_id}/{images_for_q[0]['filename']}"
                q['imageChoices'] = []
            else:
                q['hasImageChoices'] = False
                q['imageUrl'] = ""
                q['imageChoices'] = []
        
        print(f"   ✓ Matched images to questions")
    
    def convert_to_database_format(self, questions):
        """Convert questions to database format"""
        print("\n💾 Step 6: Converting to database format...")
        
        db_questions = []
        
        for q_num in sorted(questions.keys()):
            q = questions[q_num]
            module = q['module']
            subject = 'Math' if 'Math' in module else 'Reading'
            total_questions = 27 if subject == 'Reading' else 22
            
            # Get correct answer from answer key
            correct_answer = None
            if module in self.answer_key and q_num in self.answer_key[module]:
                answer_str = self.answer_key[module][q_num]
                # Convert A/B/C/D to 0/1/2/3
                if answer_str.upper() in ['A', 'B', 'C', 'D']:
                    correct_answer = ord(answer_str.upper()) - ord('A')
                else:
                    # Grid-in answer
                    correct_answer = answer_str
            
            # Determine question type
            question_type = "grid-in" if not q.get('choices') or len(q.get('choices', [])) == 0 else "multiple-choice"
            
            # Handle image choices
            choices = q.get('choices', [])
            if q.get('hasImageChoices', False):
                choices = [f"images/{self.date}/{self.test_id}/{img}" for img in q.get('imageChoices', [])]
            
            db_q = {
                "id": 0,  # Will be set when adding to database
                "module": module,
                "questionNumber": q_num,
                "totalQuestions": total_questions,
                "date": self.date,
                "region": self.region,
                "testNumber": self.test_number,
                "testName": self.test_name,
                "questionText": q.get('questionText', ''),
                "prompt": "",
                "difficulty": "medium",
                "topic": "general",
                "subject": subject,
                "explanation": "",
                "hasImageChoices": q.get('hasImageChoices', False),
                "imageUrl": q.get('imageUrl', ''),
                "choices": choices,
                "questionType": question_type,
                "correctAnswer": correct_answer if correct_answer is not None else 0,
                "testId": self.test_id
            }
            
            db_questions.append(db_q)
        
        print(f"   ✓ Converted {len(db_questions)} questions")
        return db_questions
    
    def add_to_database(self, db_questions):
        """Add questions to questions-database.json"""
        print("\n📚 Step 7: Adding to database...")
        
        db_path = Path("questions-database.json")
        
        # Read existing database
        with open(db_path, 'r', encoding='utf-8') as f:
            database = json.load(f)
        
        # Find next ID
        max_id = max((q.get('id', 0) for q in database), default=0)
        
        # Assign IDs and add questions
        for q in db_questions:
            max_id += 1
            q['id'] = max_id
            database.append(q)
        
        # Save database
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
        
        print(f"   ✓ Added {len(db_questions)} questions to database")
        print(f"   ✓ Total questions in database: {len(database)}")
    
    def run(self):
        """Run the complete extraction process"""
        try:
            self.detect_modules()
            self.extract_answer_key()
            self.extract_images()
            
            # Extract questions for each module
            all_questions = {}
            for module_name in self.modules.keys():
                module_questions = self.extract_module_questions(module_name)
                all_questions.update(module_questions)
            
            # Match images
            self.match_images_to_questions(all_questions)
            
            # Convert to database format
            db_questions = self.convert_to_database_format(all_questions)
            
            # Add to database
            self.add_to_database(db_questions)
            
            print("\n" + "=" * 80)
            print("✅ EXTRACTION COMPLETE!")
            print(f"   Test: {self.test_name}")
            print(f"   Modules: {len(self.modules)}")
            print(f"   Total questions: {len(db_questions)}")
            print("=" * 80)
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            self.doc.close()

if __name__ == "__main__":
    pdf_path = "bulk-import/202503asiav6-2.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ Error: PDF not found at {pdf_path}")
        sys.exit(1)
    
    extractor = AsiaV6Extractor(pdf_path)
    extractor.run()

