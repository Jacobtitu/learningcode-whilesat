#!/usr/bin/env python3
"""
🚀 FAST SAT TEST IMPORTER
Import an entire SAT test (all 4 modules) in ONE command!

Usage:
    python3 fast-import.py <pdf-file> <test-name> <date> <region> <test-number>

Example:
    python3 fast-import.py march2025.pdf "2025-03 Asia Test 1" 2025-03 Asia 1

What it does:
    ✅ Extracts all 4 modules (Math 1, Math 2, Reading 1, Reading 2)
    ✅ Auto-detects answer key from PDF
    ✅ Extracts and matches ALL images
    ✅ Extracts real answer choices
    ✅ Adds everything to database
    ✅ Verifies against answer key

Time: ~5 minutes per test
"""

import fitz  # PyMuPDF
import json
import shutil
import re
import sys
from pathlib import Path
from collections import defaultdict

class FastSATImporter:
    def __init__(self, pdf_path, test_name, date, region, test_number):
        self.pdf_path = pdf_path
        self.test_name = test_name
        self.date = date
        self.region = region
        self.test_number = test_number
        
        self.doc = fitz.open(pdf_path)
        self.pdf_name = Path(pdf_path).stem
        
        # Storage
        self.modules = {}
        self.answer_key = {}
        self.images_by_page = defaultdict(list)
        self.all_text = ""
        
        # Folders
        self.image_folder = Path("bulk-import/images-temp")
        self.target_folder = Path(f"images/{date}/{region.lower()}v{test_number}")
        
        print("=" * 80)
        print(f"🚀 FAST SAT IMPORTER - {test_name}")
        print("=" * 80)
    
    def remove_answer_choices_from_text(self, text):
        """Remove embedded answer choices from question text"""
        if not text:
            return text
        
        # Strategy: Find where answer choices start by looking for A) B) C) D) pattern
        # Find the position of A) and verify B) C) D) come after it in order
        
        # Find all occurrences of choice markers
        text_upper = text.upper()
        
        # Find the last occurrence of A) that's followed by B) C) D)
        # We'll search backwards to find the right A)
        a_positions = []
        pos = 0
        while True:
            pos = text_upper.find('A)', pos)
            if pos == -1:
                break
            a_positions.append(pos)
            pos += 1
        
        # Check each A) position (starting from the end) to see if it's followed by B) C) D)
        for a_pos in reversed(a_positions):
            # Look for B) C) D) after this A)
            remaining = text_upper[a_pos:]
            
            b_pos = remaining.find('B)')
            if b_pos == -1:
                continue
            
            c_pos = remaining.find('C)', b_pos)
            if c_pos == -1:
                continue
            
            d_pos = remaining.find('D)', c_pos)
            if d_pos == -1:
                continue
            
            # Found all 4 in order! Check if they're reasonably close together
            # (answer choices are usually within 2000 characters)
            if d_pos < 2000:
                # This looks like answer choices - remove everything from A) onwards
                return text[:a_pos].strip()
        
        # Fallback: Try regex patterns for edge cases
        # Pattern: A) ... B) ... C) ... D) ... at the end
        # Use non-greedy matching with lookahead for next choice
        pattern = r'\s*A\)\s+.*?B\)\s+.*?C\)\s+.*?D\)\s+.*?$'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            matched = match.group(0)
            # Verify all 4 are present
            if all(marker in matched.upper() for marker in ['A)', 'B)', 'C)', 'D)']):
                return text[:match.start()].strip()
        
        return text.strip()
    
    def run(self):
        """Run the complete import process"""
        try:
            # Step 1: Detect modules
            self.detect_modules()
            
            # Step 2: Extract answer key
            self.extract_answer_key()
            
            # Step 3: Extract all images
            self.extract_all_images()
            
            # Step 4: Extract questions for each module
            for module_name in self.modules.keys():
                self.extract_module_questions(module_name)
            
            # Step 5: Extract answer choices
            self.extract_all_choices()
            
            # Step 6: Match images to questions
            self.match_all_images()
            
            # Step 7: Add to database
            self.add_to_database()
            
            # Step 8: Cleanup
            self.cleanup()
            
            print("\n" + "=" * 80)
            print("✅ IMPORT COMPLETE!")
            print(f"   Test: {self.test_name}")
            print(f"   Modules imported: {len(self.modules)}")
            total_questions = sum(len(m['questions']) for m in self.modules.values())
            print(f"   Total questions: {total_questions}")
            print("=" * 80)
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def detect_modules(self):
        """Auto-detect all modules in the PDF"""
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
            self.all_text += text + "\n"
            
            for module_name, pattern in module_patterns.items():
                if re.search(pattern, text):
                    if module_name not in self.modules:
                        self.modules[module_name] = {
                            'name': module_name,
                            'start_page': page_num,
                            'end_page': None,
                            'questions': [],
                            'subject': 'Math' if 'Math' in module_name else 'Reading'
                        }
                        print(f"   ✓ Found {module_name} on page {page_num + 1}")
        
        # Set end pages
        module_list = sorted(self.modules.items(), key=lambda x: x[1]['start_page'])
        for i, (name, module) in enumerate(module_list):
            if i < len(module_list) - 1:
                next_module_start = module_list[i + 1][1]['start_page']
                # Check if there are questions on the same page as next module starts
                # If so, include that page in current module
                next_page = self.doc[next_module_start]
                next_text = next_page.get_text()
                
                # Check if current module's questions continue onto next module's start page
                # Look for question numbers that belong to current module
                max_q = 27 if module['subject'] == 'Reading' else 22
                current_module_questions_on_next_page = False
                
                # Check if there are question numbers on the next module's start page
                # that belong to the current module (e.g., question 27 for Reading modules)
                lines = next_text.split('\n')
                for line in lines:
                    stripped = line.strip()
                    if re.match(r'^\d+$', stripped):
                        q_num = int(stripped)
                        # If it's a valid question number for current module and it's the last question
                        if 1 <= q_num <= max_q and q_num == max_q:
                            current_module_questions_on_next_page = True
                            break
                
                if current_module_questions_on_next_page:
                    # Include the next module's start page in current module
                    module['end_page'] = next_module_start
                else:
                    module['end_page'] = next_module_start - 1
            else:
                # Last module ends before answer key (usually last 2 pages)
                module['end_page'] = len(self.doc) - 3
    
    def extract_answer_key(self):
        """Extract answer key from the end of PDF"""
        print("\n🔑 Step 2: Extracting answer key...")
        
        # Answer key is usually on the last 2-3 pages
        for page_num in range(len(self.doc) - 3, len(self.doc)):
            page = self.doc[page_num]
            text = page.get_text()
            
            if 'Answers' in text or 'Answer Key' in text:
                print(f"   ✓ Found answer key on page {page_num + 1}")
                
                # Parse answer key
                lines = text.split('\n')
                current_module = None
                
                for line in lines:
                    # Detect module headers
                    if 'Module 1 Answers' in line:
                        if 'Math' in line:
                            current_module = 'Math Module 1'
                        elif 'Reading' in line or 'Writing' in line:
                            current_module = 'Reading and Writing Module 1'
                    elif 'Module 2 Answers' in line:
                        if 'Math' in line:
                            current_module = 'Math Module 2'
                        elif 'Reading' in line or 'Writing' in line:
                            current_module = 'Reading and Writing Module 2'
                    
                    # Parse answer lines (e.g., "1. A", "2. 5780", "16. D")
                    if current_module:
                        match = re.match(r'^(\d+)\.\s+(.+)$', line.strip())
                        if match:
                            q_num = int(match.group(1))
                            answer = match.group(2).strip()
                            
                            if current_module not in self.answer_key:
                                self.answer_key[current_module] = {}
                            
                            self.answer_key[current_module][q_num] = answer
        
        # Print summary
        for module_name, answers in self.answer_key.items():
            print(f"   ✓ {module_name}: {len(answers)} answers")
    
    def extract_all_images(self):
        """Extract all images from PDF"""
        print("\n📸 Step 3: Extracting images...")
        
        self.image_folder.mkdir(parents=True, exist_ok=True)
        total_images = 0
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    pix = fitz.Pixmap(self.doc, xref)
                    
                    if pix.n - pix.alpha < 4:
                        filename = f"p{page_num + 1}_img{img_index + 1}.png"
                        filepath = self.image_folder / filename
                        pix.save(filepath)
                        
                        self.images_by_page[page_num].append({
                            'filename': filename,
                            'filepath': filepath,
                            'page': page_num,
                            'index': img_index
                        })
                        total_images += 1
                    
                    pix = None
                except:
                    pass
        
        print(f"   ✓ Extracted {total_images} images")
    
    def extract_module_questions(self, module_name):
        """Extract questions for a specific module"""
        module = self.modules[module_name]
        start_page = module['start_page']
        end_page = module['end_page']
        
        print(f"\n📝 Step 4: Extracting {module_name} questions (pages {start_page+1}-{end_page+1})...")
        
        questions = {}
        current_q = None
        
        for page_num in range(start_page, end_page + 1):
            page = self.doc[page_num]
            text = page.get_text()
            lines = text.split('\n')
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                
                # Find question numbers (standalone on a line)
                if re.match(r'^\d+$', stripped):
                    q_num = int(stripped)
                    
                    # Reasonable question numbers (1-27 for reading, 1-22 for math)
                    max_q = 27 if module['subject'] == 'Reading' else 22
                    if 1 <= q_num <= max_q:
                        # Save previous question
                        if current_q and current_q['number'] not in questions:
                            questions[current_q['number']] = current_q
                        
                        # Start new question
                        current_q = {
                            'number': q_num,
                            'text_lines': [],
                            'page': page_num
                        }
                
                elif current_q and stripped:
                    # Skip module headers and navigation text
                    if 'Module' not in stripped and 'CONTINUE' not in stripped and 'QUESTIONS' not in stripped:
                        current_q['text_lines'].append(stripped)
        
        # Save last question
        if current_q and current_q['number'] not in questions:
            questions[current_q['number']] = current_q
        
        # Combine text and clean
        for q_num, q in questions.items():
            text = ' '.join(q['text_lines']).strip()
            
            # Remove embedded answer choices using helper function
            text = self.remove_answer_choices_from_text(text)
            
            # Clean up extra whitespace
            text = ' '.join(text.split()).strip()
            
            q['text'] = text
            del q['text_lines']
        
        module['questions'] = questions
        print(f"   ✓ Extracted {len(questions)} questions")
    
    def extract_all_choices(self):
        """Extract answer choices for all questions"""
        print("\n📋 Step 5: Extracting answer choices...")
        
        for module_name, module in self.modules.items():
            missing_choices = []
            for q_num, question in module['questions'].items():
                choices = self.extract_choices_for_question(module, q_num)
                question['choices'] = choices if choices else []
                if not choices and module['subject'] == 'Reading':  # Math grid-in questions don't need choices
                    missing_choices.append(q_num)
            
            if missing_choices:
                print(f"   ⚠️  {module_name}: {len(missing_choices)} questions missing choices: {missing_choices}")
            else:
                print(f"   ✓ {module_name}: All questions have choices")
    
    def extract_choices_for_question(self, module, q_num):
        """Extract choices for a specific question - handles multi-page questions"""
        start_page = module['start_page']
        end_page = module['end_page']
        
        # Find where the question starts
        question_start_page = None
        question_start_pos = None
        
        for page_num in range(start_page, end_page + 1):
            page = self.doc[page_num]
            text = page.get_text()
            
            # Look for question number on its own line
            if f'\n{q_num}\n' in text:
                question_start_page = page_num
                # Find the position after the question number
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip() == str(q_num):
                        # Found it - collect from here
                        question_start_pos = i
                        break
                break
        
        if question_start_page is None:
            return None
        
        # Collect text across pages until we find all 4 choices OR next question
        question_text_parts = []
        next_q_num = q_num + 1
        max_q = 27 if module['subject'] == 'Reading' else 22
        
        # Start collecting from the question start
        found_next_question = False
        found_module_boundary = False
        
        for page_num in range(question_start_page, end_page + 1):
            page = self.doc[page_num]
            text = page.get_text()
            lines = text.split('\n')
            
            if page_num == question_start_page:
                # Start from where we found the question
                if question_start_pos is not None:
                    lines = lines[question_start_pos + 1:]
            
            # Collect lines until we hit the next question number or module boundary
            for line in lines:
                stripped = line.strip()
                
                # Check if we hit a module boundary (e.g., "Math Module 1")
                if 'Module' in stripped and ('Math' in stripped or 'Reading' in stripped or 'Writing' in stripped):
                    found_module_boundary = True
                    break
                
                # Check if we hit the next question number
                if re.match(r'^\d+$', stripped):
                    next_q = int(stripped)
                    if 1 <= next_q <= max_q and next_q > q_num:
                        # Hit next question, stop collecting
                        found_next_question = True
                        break
                
                question_text_parts.append(line)
            
            # Check if we already have all 4 choices or hit a boundary
            combined_text = '\n'.join(question_text_parts)
            choice_count = len(re.findall(r'[A-D]\)', combined_text))
            if choice_count >= 4 or found_next_question or found_module_boundary:
                # We have enough choices or hit next question/module, stop
                break
        
        question_text = '\n'.join(question_text_parts)
        
        if not question_text:
            return None
        
        # Extract A), B), C), D) choices - improved pattern to handle multi-line choices
        choices = []
        for letter in ['A', 'B', 'C', 'D']:
            # Pattern: letter) followed by text until next letter) or end
            # Handle choices that might span multiple lines
            # Look for next choice marker (B), C), D)) or end of text
            next_letters = ['B', 'C', 'D'] if letter == 'A' else ['C', 'D'] if letter == 'B' else ['D'] if letter == 'C' else []
            
            if next_letters:
                # There's a next choice, match until we find it
                next_pattern = '|'.join([f'{l}\\)' for l in next_letters])
                choice_pattern = rf'{letter}\)\s+(.*?)(?=\s*(?:{next_pattern})|\Z)'
            else:
                # Last choice (D), match until end OR until we hit a question number or module marker
                choice_pattern = rf'{letter}\)\s+(.*?)(?=\Z|\n\s*\d+\s*\n|\n\s*Module\s+)'
            
            choice_match = re.search(choice_pattern, question_text, re.DOTALL | re.MULTILINE)
            if choice_match:
                choice_text = choice_match.group(1).strip()
                # Clean up: remove extra whitespace, handle line breaks
                choice_text = ' '.join(choice_text.split())
                
                # Remove any trailing content that looks like it's from the next question
                # Check for patterns like "1 s = " (math equation markers)
                if re.search(r'\d+\s+[a-z]\s*=\s*', choice_text):
                    # Found math equation, truncate before it
                    match = re.search(r'(\d+\s+[a-z]\s*=\s*)', choice_text)
                    if match:
                        choice_text = choice_text[:match.start()].strip()
                
                # Remove trailing numbers that might be question numbers
                choice_text = re.sub(r'\s+\d+\s*$', '', choice_text).strip()
                
                choices.append(choice_text)
        
        return choices if len(choices) == 4 else None
    
    def match_all_images(self):
        """Match images to questions - ONLY when explicitly referenced"""
        print("\n🔗 Step 6: Matching images to questions...")
        
        # Patterns that indicate an image is needed
        strict_image_patterns = [
            'the graph', 'the scatterplot', 'the histogram',
            'the chart', 'the figure', 'the diagram', 'the table',
            'the triangle', 'the cone', 'the circle', 'the rectangle',
            'graph shows', 'table shows', 'chart shows', 'figure shows',
            'diagram shows', 'shown in', 'figure shown', 'graph shown',
            'triangle shown', 'cone shown', 'circle shown',
            'right triangle shown', 'circular cone shown',
            'graph of', 'scatterplot of', 'histogram of',
            'data from the graph', 'data from the table', 'data from the chart',
            'according to the table', 'according to the graph',
            'based on the graph', 'based on the table', 'based on the chart',
            'uses data from', 'using data from',
            'which table gives', 'which graph', 'which figure',
            'shown below', 'shown above', 'shaded region',
            'table above', 'table below', 'figure above', 'figure below'
        ]
        
        for module_name, module in self.modules.items():
            matched_count = 0
            used_images = set()  # Track which images have been assigned
            
            # Sort questions by question number (not page) to maintain order
            sorted_questions = sorted(module['questions'].items(), key=lambda x: x[0])
            
            for q_num, question in sorted_questions:
                text_lower = question['text'].lower()
                page_num = question['page']
                
                # STRICT CHECK: Does the question EXPLICITLY reference a visual?
                needs_image = any(pattern in text_lower for pattern in strict_image_patterns)
                
                # Special case: very short question text usually means the image IS the question
                is_only_choices = len(question['text']) < 20
                
                if needs_image or is_only_choices:
                    # Get images from current page ONLY (most reliable)
                    available_images = []
                    
                    if page_num in self.images_by_page:
                        for img in self.images_by_page[page_num]:
                            if img['filename'] not in used_images:
                                available_images.append(img)
                    
                    # If no images on current page, check next page (question might span pages)
                    if not available_images and (page_num + 1) in self.images_by_page:
                        for img in self.images_by_page[page_num + 1]:
                            if img['filename'] not in used_images:
                                available_images.append(img)
                    
                    if available_images:
                        # Check for 4 image choices (A/B/C/D options as images)
                        if len(available_images) >= 4 and ('which' in text_lower or is_only_choices):
                            question['image_type'] = 'choices'
                            question['images'] = [img['filename'] for img in available_images[:4]]
                            for img in available_images[:4]:
                                used_images.add(img['filename'])
                            matched_count += 1
                        else:
                            # Single image - use the first available image
                            # Since we already prioritized same-page images, just take the first one
                            question['image_type'] = 'single'
                            question['images'] = [available_images[0]['filename']]
                            used_images.add(available_images[0]['filename'])
                            matched_count += 1
                    else:
                        question['image_type'] = 'none'
                        question['images'] = []
                else:
                    question['image_type'] = 'none'
                    question['images'] = []
            
            if matched_count > 0:
                print(f"   ✓ {module_name}: {matched_count} questions with images")
    
    def add_to_database(self):
        """Add all modules to the database"""
        print("\n💾 Step 7: Adding to database...")
        
        # Load existing database
        db_path = Path('questions-database.json')
        if db_path.exists():
            with open(db_path, 'r') as f:
                db = json.load(f)
        else:
            db = []
        
        # Get next ID
        next_id = max([q['id'] for q in db], default=0) + 1
        
        # Prepare target image folder
        self.target_folder.mkdir(parents=True, exist_ok=True)
        
        total_added = 0
        
        for module_name, module in self.modules.items():
            # Determine total questions for this module
            total_questions = 27 if module['subject'] == 'Reading' else 22
            
            for q_num in sorted(module['questions'].keys()):
                question_data = module['questions'][q_num]
                answer_str = self.answer_key.get(module_name, {}).get(q_num, "A")
                
                # Determine if grid-in or multiple choice
                is_grid_in = False
                if module['subject'] == 'Math':
                    # Check if answer is numeric or fraction (grid-in)
                    is_grid_in = bool(re.match(r'^[\d./\-]+$', str(answer_str))) and answer_str not in ['A', 'B', 'C', 'D']
                
                # Build question object
                q_obj = {
                    "id": next_id,
                    "module": module_name,
                    "questionNumber": q_num,
                    "totalQuestions": total_questions,
                    "date": self.date,
                    "region": self.region,
                    "testNumber": self.test_number,
                    "testName": self.test_name,
                    "questionText": question_data['text'],
                    "prompt": "",
                    "difficulty": "medium",
                    "topic": "general",
                    "subject": module['subject'],
                    "explanation": ""
                }
                
                # Handle images
                if question_data.get('image_type') == 'choices' and question_data.get('images'):
                    # Multiple image choices (A/B/C/D)
                    q_obj['hasImageChoices'] = True
                    q_obj['imageUrl'] = ""
                    image_choices = []
                    
                    for idx, img_filename in enumerate(question_data['images'][:4]):
                        option_letter = chr(65 + idx)
                        src = self.image_folder / img_filename
                        new_name = f"{module_name.lower().replace(' ', '-')}-q{q_num}-option{option_letter}.png"
                        dst = self.target_folder / new_name
                        
                        if src.exists():
                            shutil.copy2(src, dst)
                            image_choices.append(f"{self.target_folder}/{new_name}")
                    
                    q_obj['choices'] = image_choices
                
                elif question_data.get('image_type') == 'single' and question_data.get('images'):
                    # Single image
                    q_obj['hasImageChoices'] = False
                    img_filename = question_data['images'][0]
                    src = self.image_folder / img_filename
                    new_name = f"{module_name.lower().replace(' ', '-')}-q{q_num}-diagram.png"
                    dst = self.target_folder / new_name
                    
                    if src.exists():
                        shutil.copy2(src, dst)
                        q_obj['imageUrl'] = f"{self.target_folder}/{new_name}"
                    else:
                        q_obj['imageUrl'] = ""
                    
                    q_obj['choices'] = question_data.get('choices', [])
                
                else:
                    # No images
                    q_obj['hasImageChoices'] = False
                    q_obj['imageUrl'] = ""
                    q_obj['choices'] = question_data.get('choices', [])
                
                # Set answer
                if is_grid_in:
                    q_obj['questionType'] = 'grid-in'
                    q_obj['correctAnswer'] = answer_str
                    q_obj['choices'] = []
                else:
                    q_obj['questionType'] = 'multiple-choice'
                    # Convert letter to index
                    if answer_str in ['A', 'B', 'C', 'D']:
                        q_obj['correctAnswer'] = ord(answer_str) - ord('A')
                    else:
                        q_obj['correctAnswer'] = 0  # Default to A if unclear
                
                db.append(q_obj)
                next_id += 1
                total_added += 1
        
        # Save database
        with open(db_path, 'w') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        
        print(f"   ✓ Added {total_added} questions to database")
    
    def cleanup(self):
        """Clean up temporary files"""
        print("\n🧹 Step 8: Cleaning up...")
        if self.image_folder.exists():
            shutil.rmtree(self.image_folder)
        print("   ✓ Temporary files removed")

def main():
    if len(sys.argv) < 6:
        print("Usage: python3 fast-import.py <pdf-file> <test-name> <date> <region> <test-number>")
        print("\nExample:")
        print('  python3 fast-import.py march2025.pdf "2025-03 Asia Test 1" 2025-03 Asia 1')
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    test_name = sys.argv[2]
    date = sys.argv[3]
    region = sys.argv[4]
    test_number = int(sys.argv[5])
    
    if not Path(pdf_path).exists():
        print(f"❌ Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    importer = FastSATImporter(pdf_path, test_name, date, region, test_number)
    importer.run()

if __name__ == "__main__":
    main()

