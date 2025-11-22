#!/usr/bin/env python3
"""
OCR-based text extraction for Asia v6 PDF images
Extracts question text, answer choices, and matches them to database
"""

import json
import re
from pathlib import Path
from PIL import Image
import pytesseract

# Set tesseract path (common locations)
import subprocess
tesseract_path = subprocess.run(['which', 'tesseract'], capture_output=True, text=True).stdout.strip()
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    print(f"✓ Using Tesseract at: {tesseract_path}")
else:
    # Try common locations
    for path in ['/opt/homebrew/bin/tesseract', '/usr/local/bin/tesseract', '/usr/bin/tesseract']:
        if Path(path).exists():
            pytesseract.pytesseract.tesseract_cmd = path
            print(f"✓ Using Tesseract at: {path}")
            break

class AsiaV6OCR:
    def __init__(self):
        self.image_folder = Path("images/2025-03/asiav6")
        self.mapping_file = self.image_folder / "image-mapping.json"
        self.db_path = Path("questions-database.json")
        
        # Load image mapping
        with open(self.mapping_file, 'r') as f:
            self.mapping = json.load(f)
        
        # Load database
        with open(self.db_path, 'r', encoding='utf-8') as f:
            self.database = json.load(f)
        
        self.questions = {q['id']: q for q in self.database if q.get('testId') == 'asiav6'}
        
        print("=" * 80)
        print("🔍 OCR TEXT EXTRACTION FOR ASIA V6")
        print("=" * 80)
        print(f"   Found {len(self.questions)} questions")
        print(f"   Found {self.mapping['total_images']} images")
    
    def clean_ocr_text(self, text):
        """Clean OCR text"""
        if not text:
            return ""
        
        # Remove common UI elements and headers
        lines = text.split('\n')
        cleaned_lines = []
        skip_patterns = [
            r'Section \d+',
            r'Module \d+',
            r'Reading and Writing',
            r'Math Module',
            r'Directions',
            r'Highlights',
            r'Notes',
            r'More',
            r'^\d+:\d+',  # Time stamps like "31:50"
            r'^\s*:\s*$',  # Just colons
            r'^\s*=\s*$',  # Just equals
            r'^\s*&\s*$',  # Just ampersand
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip lines matching skip patterns
            skip = False
            for pattern in skip_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    skip = True
                    break
            
            if not skip:
                cleaned_lines.append(line)
        
        text = ' '.join(cleaned_lines)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that break JSON
        text = text.replace('\x00', '')
        # Fix common OCR errors (be careful with these)
        text = text.replace('|', 'I')
        # Don't replace 0 with O as it breaks numbers
        
        return text.strip()
    
    def extract_question_number(self, text):
        """Extract question number from text"""
        # Look for standalone numbers at start
        match = re.match(r'^(\d+)\s', text)
        if match:
            return int(match.group(1))
        
        # Look for numbers anywhere in first few lines (question numbers are usually early)
        lines = text.split('\n')[:5]
        for line in lines:
            # Look for standalone number
            match = re.search(r'^\s*(\d+)\s*$', line.strip())
            if match:
                num = int(match.group(1))
                if 1 <= num <= 27:  # Valid question number range
                    return num
        
        # Look for "Question 1" or "Q1" patterns
        match = re.search(r'(?:Question|Q)\s*(\d+)', text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        return None
    
    def extract_choices(self, text):
        """Extract answer choices from text - improved version"""
        choices = []
        
        # Strategy 1: Look for A) B) C) D) pattern
        pattern1 = r'([A-D])\)\s*([^A-D]+?)(?=[A-D]\)|$)'
        matches1 = list(re.finditer(pattern1, text, re.DOTALL | re.IGNORECASE))
        
        if len(matches1) >= 4:
            for match in matches1:
                choice_text = match.group(2).strip()
                choice_text = re.sub(r'\s+', ' ', choice_text)
                # Remove common OCR artifacts from choices
                choice_text = re.sub(r'^[®©○●\s]+', '', choice_text)
                choice_text = re.sub(r'[®©○●\s]+$', '', choice_text)
                if choice_text and len(choice_text) > 0:
                    choices.append(choice_text)
        
        # Strategy 2: Look for A. B. C. D. pattern
        if len(choices) != 4:
            pattern2 = r'([A-D])\.\s*([^A-D]+?)(?=[A-D]\.|$)'
            matches2 = list(re.finditer(pattern2, text, re.DOTALL | re.IGNORECASE))
            if len(matches2) >= 4:
                choices2 = []
                for match in matches2:
                    choice_text = match.group(2).strip()
                    choice_text = re.sub(r'\s+', ' ', choice_text)
                    choice_text = re.sub(r'^[®©○●\s]+', '', choice_text)
                    choice_text = re.sub(r'[®©○●\s]+$', '', choice_text)
                    if choice_text:
                        choices2.append(choice_text)
                if len(choices2) >= 4:
                    choices = choices2[:4]
        
        # Strategy 3: Look for bubble/circle markers (® © ○ ●) followed by text
        if len(choices) != 4:
            # More flexible pattern for bubbles
            pattern3 = r'[®©○●]\s*([A-Za-z0-9][^®©○●A-D]{1,100}?)(?=[®©○●]|$)'
            matches3 = list(re.finditer(pattern3, text, re.DOTALL))
            if len(matches3) >= 4:
                choices3 = []
                for match in matches3:
                    choice_text = match.group(1).strip()
                    choice_text = re.sub(r'\s+', ' ', choice_text)
                    # Clean up common OCR errors in choices
                    choice_text = re.sub(r'oudatea', 'outdated', choice_text, flags=re.IGNORECASE)
                    choice_text = re.sub(r'variea', 'varied', choice_text, flags=re.IGNORECASE)
                    choice_text = re.sub(r'forgoren', 'forgotten', choice_text, flags=re.IGNORECASE)
                    if choice_text and len(choice_text) > 1:
                        choices3.append(choice_text)
                if len(choices3) >= 4:
                    choices = choices3[:4]
        
        # Strategy 4: Look for lines that start with common choice patterns
        if len(choices) != 4:
            lines = text.split('\n')
            potential_choices = []
            for line in lines:
                line = line.strip()
                # Check if line looks like a choice (starts with A/B/C/D or bubble)
                if re.match(r'^([A-D][\)\.]|[®©○●])\s*[A-Za-z]', line):
                    # Extract the choice text
                    choice_text = re.sub(r'^[A-D][\)\.]\s*|[®©○●]\s*', '', line, flags=re.IGNORECASE)
                    choice_text = re.sub(r'\s+', ' ', choice_text).strip()
                    if choice_text and len(choice_text) > 1:
                        potential_choices.append(choice_text)
            
            # If we found 4 potential choices in sequence
            if len(potential_choices) >= 4:
                # Take first 4 that are reasonably spaced
                choices = potential_choices[:4]
        
        # Strategy 5: Look for numbered list pattern (1) 2) 3) 4) that might be choices
        if len(choices) != 4:
            pattern5 = r'([1-4])[\)\.]\s*([A-Za-z][^1-4]{2,100}?)(?=[1-4][\)\.]|$)'
            matches5 = list(re.finditer(pattern5, text, re.DOTALL))
            if len(matches5) >= 4:
                # Check if they're in order 1,2,3,4
                ordered = sorted(matches5, key=lambda m: int(m.group(1)))
                if len(ordered) >= 4 and all(int(ordered[i].group(1)) == i+1 for i in range(4)):
                    choices5 = []
                    for match in ordered[:4]:
                        choice_text = match.group(2).strip()
                        choice_text = re.sub(r'\s+', ' ', choice_text)
                        if choice_text:
                            choices5.append(choice_text)
                    if len(choices5) == 4:
                        choices = choices5
        
        # Final cleanup
        cleaned_choices = []
        for choice in choices[:4]:
            if choice:
                # Remove leading/trailing punctuation that's likely OCR error
                choice = re.sub(r'^[:\-=&\s]+', '', choice)
                choice = re.sub(r'[:\-=&\s]+$', '', choice)
                # Fix common OCR errors
                choice = re.sub(r'oudatea', 'outdated', choice, flags=re.IGNORECASE)
                choice = re.sub(r'variea', 'varied', choice, flags=re.IGNORECASE)
                choice = re.sub(r'forgoren', 'forgotten', choice, flags=re.IGNORECASE)
                choice = re.sub(r'\s+', ' ', choice).strip()
                cleaned_choices.append(choice)
            else:
                cleaned_choices.append('')
        
        # Pad to 4 if needed
        while len(cleaned_choices) < 4:
            cleaned_choices.append('')
        
        return cleaned_choices[:4]
    
    def remove_choices_from_text(self, text):
        """Remove answer choices from question text"""
        text_upper = text.upper()
        
        # Find A) position
        a_pos = text_upper.find('A)')
        if a_pos == -1:
            a_pos = text_upper.find('A.')
        
        if a_pos != -1:
            remaining = text_upper[a_pos:]
            if 'B)' in remaining or 'B.' in remaining:
                if 'C)' in remaining or 'C.' in remaining:
                    if 'D)' in remaining or 'D.' in remaining:
                        return text[:a_pos].strip()
        
        return text.strip()
    
    def process_image(self, image_path):
        """Process a single image with OCR"""
        try:
            img = Image.open(image_path)
            
            # Try multiple OCR modes and combine best results
            # PSM 6: Assume uniform block of text (best for full pages)
            text1 = pytesseract.image_to_string(img, config='--oem 3 --psm 6')
            
            # PSM 11: Sparse text (sometimes better for formatted pages)
            text2 = pytesseract.image_to_string(img, config='--oem 3 --psm 11')
            
            # Use the longer/more complete text
            text = text1 if len(text1) > len(text2) else text2
            
            return self.clean_ocr_text(text)
        except Exception as e:
            print(f"  ⚠️  Error processing {image_path.name}: {e}")
            return ""
    
    def match_image_to_question(self, page_num, img_filename):
        """Match an image to a question based on page number"""
        # Find questions that might be on this page
        # Questions are roughly distributed across pages
        for q_id, q in self.questions.items():
            # Check if this question's estimated page matches
            # We'll use a heuristic based on question number and module
            module = q['module']
            q_num = q['questionNumber']
            
            # Rough page estimation (will refine based on actual matches)
            if 'Reading and Writing Module 1' in module:
                estimated_page = q_num // 2 + 1
            elif 'Math Module 1' in module:
                estimated_page = q_num // 2 + 26
            elif 'Reading and Writing Module 2' in module:
                estimated_page = q_num // 2 + 51
            elif 'Math Module 2' in module:
                estimated_page = q_num // 2 + 76
            else:
                estimated_page = 1
            
            # Check if image filename matches question's current image
            if q.get('imageUrl', '').endswith(img_filename):
                return q_id
        
        return None
    
    def process_all_images(self):
        """Process all images and extract text"""
        print("\n📸 Processing images with OCR...")
        
        images_by_page = self.mapping.get('images_by_page', {})
        processed_count = 0
        updated_questions = set()
        
        for page_str, images in images_by_page.items():
            page_num = int(page_str)
            
            for img_info in images:
                img_filename = img_info['filename']
                img_path = self.image_folder / img_filename
                
                if not img_path.exists():
                    continue
                
                print(f"  Processing page {page_num}, image {img_info['index']}...")
                
                # Extract text with OCR
                ocr_text = self.process_image(img_path)
                
                if not ocr_text:
                    continue
                
                # Extract question number from OCR text
                q_num_from_text = self.extract_question_number(ocr_text)
                
                # Try to find matching question by number and page
                q_id = None
                if q_num_from_text:
                    # Find question by number and estimated module based on page
                    for q_id_candidate, q in self.questions.items():
                        if q['questionNumber'] == q_num_from_text:
                            # Check if page matches module
                            module = q['module']
                            if 'Reading and Writing Module 1' in module and 1 <= page_num <= 30:
                                q_id = q_id_candidate
                                break
                            elif 'Math Module 1' in module and 25 <= page_num <= 50:
                                q_id = q_id_candidate
                                break
                            elif 'Reading and Writing Module 2' in module and 50 <= page_num <= 75:
                                q_id = q_id_candidate
                                break
                            elif 'Math Module 2' in module and 75 <= page_num <= 100:
                                q_id = q_id_candidate
                                break
                
                # Fallback: try image filename match
                if not q_id:
                    q_id = self.match_image_to_question(page_num, img_filename)
                
                if q_id and q_id in self.questions:
                    q = self.questions[q_id]
                    
                    # Verify it matches (or use if no number found)
                    if q_num_from_text is None or q_num_from_text == q['questionNumber']:
                        # Extract choices
                        choices = self.extract_choices(ocr_text)
                        
                        # Remove choices from question text
                        question_text = self.remove_choices_from_text(ocr_text)
                        
                        # Update question
                        if question_text:
                            q['questionText'] = question_text
                        if choices and len(choices) == 4:
                            q['choices'] = choices
                            q['questionType'] = 'multiple-choice'
                        elif not choices and q.get('questionType') == 'grid-in':
                            # Keep as grid-in
                            pass
                        
                        updated_questions.add(q_id)
                        processed_count += 1
                        print(f"    ✓ Updated Q{q['questionNumber']} ({q['module']})")
                    else:
                        print(f"    ⚠️  Question number mismatch: expected {q['questionNumber']}, got {q_num_from_text}")
                else:
                    # Try to extract question number and find question
                    q_num = self.extract_question_number(ocr_text)
                    if q_num:
                        # Find question by number and module (estimate from page)
                        for q_id, q in self.questions.items():
                            if q['questionNumber'] == q_num:
                                # Check if page is reasonable for this module
                                module = q['module']
                                if 'Reading and Writing Module 1' in module and 1 <= page_num <= 25:
                                    q['questionText'] = self.remove_choices_from_text(ocr_text)
                                    choices = self.extract_choices(ocr_text)
                                    if choices:
                                        q['choices'] = choices
                                    updated_questions.add(q_id)
                                    processed_count += 1
                                    print(f"    ✓ Updated Q{q_num} ({module})")
                                    break
                                elif 'Math Module 1' in module and 26 <= page_num <= 50:
                                    q['questionText'] = self.remove_choices_from_text(ocr_text)
                                    choices = self.extract_choices(ocr_text)
                                    if choices:
                                        q['choices'] = choices
                                    updated_questions.add(q_id)
                                    processed_count += 1
                                    print(f"    ✓ Updated Q{q_num} ({module})")
                                    break
                                elif 'Reading and Writing Module 2' in module and 51 <= page_num <= 75:
                                    q['questionText'] = self.remove_choices_from_text(ocr_text)
                                    choices = self.extract_choices(ocr_text)
                                    if choices:
                                        q['choices'] = choices
                                    updated_questions.add(q_id)
                                    processed_count += 1
                                    print(f"    ✓ Updated Q{q_num} ({module})")
                                    break
                                elif 'Math Module 2' in module and 76 <= page_num <= 97:
                                    q['questionText'] = self.remove_choices_from_text(ocr_text)
                                    choices = self.extract_choices(ocr_text)
                                    if choices:
                                        q['choices'] = choices
                                    updated_questions.add(q_id)
                                    processed_count += 1
                                    print(f"    ✓ Updated Q{q_num} ({module})")
                                    break
        
        print(f"\n✅ Processed {processed_count} images")
        print(f"   Updated {len(updated_questions)} questions")
        
        return updated_questions
    
    def save_database(self):
        """Save updated database"""
        print("\n💾 Saving database...")
        
        # Update questions in database
        for i, q in enumerate(self.database):
            if q.get('id') in self.questions:
                q.update(self.questions[q['id']])
        
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.database, f, indent=2, ensure_ascii=False)
        
        print(f"   ✓ Saved {len(self.database)} questions to database")
    
    def run(self):
        """Run OCR extraction"""
        try:
            updated = self.process_all_images()
            self.save_database()
            
            print("\n" + "=" * 80)
            print("✅ OCR EXTRACTION COMPLETE!")
            print(f"   Updated questions: {len(updated)}")
            print("=" * 80)
            print("\n📝 Next steps:")
            print("   1. Review extracted text for accuracy")
            print("   2. Manually correct any OCR errors")
            print("   3. Add correct answers from answer key")
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # Check if tesseract is available
    try:
        pytesseract.get_tesseract_version()
        print("✓ Tesseract OCR found")
    except:
        print("❌ Tesseract OCR not found!")
        print("   Please install:")
        print("   - macOS: brew install tesseract")
        print("   - Linux: sudo apt-get install tesseract-ocr")
        print("   - Then: pip install pytesseract pillow")
        exit(1)
    
    extractor = AsiaV6OCR()
    extractor.run()

