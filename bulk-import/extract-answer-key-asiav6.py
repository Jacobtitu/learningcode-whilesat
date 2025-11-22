#!/usr/bin/env python3
"""
Extract answer key from Asia v6 PDF using OCR
"""

import fitz
import json
import re
from pathlib import Path
from PIL import Image
import pytesseract
import subprocess

# Set tesseract path
tesseract_path = subprocess.run(['which', 'tesseract'], capture_output=True, text=True).stdout.strip()
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

class AnswerKeyExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.answer_key = {}
        
        print("=" * 80)
        print("🔑 ANSWER KEY EXTRACTOR - ASIA V6")
        print("=" * 80)
    
    def find_answer_key_pages(self):
        """Find pages that likely contain answer key"""
        # Answer key is usually on last few pages
        key_pages = []
        
        for page_num in range(max(0, len(self.doc) - 5), len(self.doc)):
            page = self.doc[page_num]
            text = page.get_text()
            
            # Check if page has answer-like content
            if 'Answer' in text or 'ANSWERS' in text or re.search(r'\d+\.\s*[A-D]', text):
                key_pages.append(page_num)
        
        # Also check if pages are image-based
        for page_num in range(max(0, len(self.doc) - 10), len(self.doc)):
            page = self.doc[page_num]
            images = page.get_images()
            if len(images) > 0:
                key_pages.append(page_num)
        
        return sorted(set(key_pages))
    
    def extract_text_from_page(self, page_num):
        """Extract text from page using OCR if needed"""
        page = self.doc[page_num]
        text = page.get_text()
        
        # If no text, use OCR
        if not text.strip():
            images = page.get_images()
            if images:
                try:
                    xref = images[0][0]
                    pix = fitz.Pixmap(self.doc, xref)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    text = pytesseract.image_to_string(img, config='--psm 6')
                    pix = None
                except:
                    pass
        
        return text
    
    def parse_answer_key(self, text):
        """Parse answer key from text - improved for OCR"""
        answers = {}
        current_module = None
        
        lines = text.split('\n')
        
        # Also try to find answers in the middle of lines
        full_text = ' '.join(lines)
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect module (more flexible patterns)
            if re.search(r'Module\s*1', line, re.IGNORECASE):
                if re.search(r'Math', line, re.IGNORECASE):
                    current_module = 'Math Module 1'
                elif re.search(r'Reading|Writing', line, re.IGNORECASE):
                    current_module = 'Reading and Writing Module 1'
            elif re.search(r'Module\s*2', line, re.IGNORECASE):
                if re.search(r'Math', line, re.IGNORECASE):
                    current_module = 'Math Module 2'
                elif re.search(r'Reading|Writing', line, re.IGNORECASE):
                    current_module = 'Reading and Writing Module 2'
            
            # Parse answer lines: "1. A" or "1 A" or "1) A" or "1. 5780"
            # More flexible patterns for OCR
            patterns = [
                r'(\d+)[\.\)]\s*([A-D]|\d+\.?\d*)',  # "1. A" or "1) 5780"
                r'(\d+)\s+([A-D]|\d+\.?\d*)',  # "1 A" or "1 5780"
                r'(\d+)[\.\)]\s*([A-D]|\d+)',  # "1. A" or "1) 5780"
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    q_num = int(match.group(1))
                    answer = match.group(2).strip()
                    
                    # Validate question number range
                    if 1 <= q_num <= 27:  # Max for reading modules
                        # Try to determine module if not set
                        if not current_module:
                            # Estimate based on question number
                            if q_num <= 22:
                                # Could be Math Module 1 or Reading Module 1
                                # Check context - if we see "Math" nearby, it's Math
                                if re.search(r'Math', line, re.IGNORECASE):
                                    current_module = 'Math Module 1'
                                else:
                                    current_module = 'Reading and Writing Module 1'
                        
                        if current_module:
                            if current_module not in answers:
                                answers[current_module] = {}
                            answers[current_module][q_num] = answer
        
        # Also search full text for patterns
        if not answers:
            # Try to find all answer patterns in full text
            all_matches = re.finditer(r'(\d+)[\.\)]\s*([A-D]|\d+\.?\d*)', full_text)
            for match in all_matches:
                q_num = int(match.group(1))
                answer = match.group(2).strip()
                if 1 <= q_num <= 27:
                    # Try to assign to a module (rough estimate)
                    # This is a fallback - better to have module context
                    if q_num <= 22:
                        module = 'Math Module 1'  # Default guess
                        if module not in answers:
                            answers[module] = {}
                        if q_num not in answers[module]:
                            answers[module][q_num] = answer
        
        return answers
    
    def extract(self):
        """Extract answer key from PDF"""
        print("\n📄 Finding answer key pages...")
        
        key_pages = self.find_answer_key_pages()
        print(f"   ✓ Found {len(key_pages)} potential answer key pages")
        
        all_text = ""
        for page_num in key_pages:
            print(f"   Processing page {page_num + 1}...")
            text = self.extract_text_from_page(page_num)
            all_text += text + "\n"
        
        print("\n🔍 Parsing answer key...")
        answers = self.parse_answer_key(all_text)
        
        # Print summary
        for module, module_answers in answers.items():
            print(f"   ✓ {module}: {len(module_answers)} answers")
        
        self.answer_key = answers
        return answers
    
    def apply_to_database(self):
        """Apply answer key to database"""
        print("\n💾 Applying answers to database...")
        
        db_path = Path("questions-database.json")
        with open(db_path, 'r', encoding='utf-8') as f:
            database = json.load(f)
        
        updated_count = 0
        
        for q in database:
            if q.get('testId') != 'asiav6':
                continue
            
            module = q['module']
            q_num = q['questionNumber']
            
            if module in self.answer_key and q_num in self.answer_key[module]:
                answer_str = self.answer_key[module][q_num]
                
                # Convert A/B/C/D to 0/1/2/3
                if answer_str.upper() in ['A', 'B', 'C', 'D']:
                    q['correctAnswer'] = ord(answer_str.upper()) - ord('A')
                    updated_count += 1
                elif answer_str:  # Grid-in answer
                    q['correctAnswer'] = answer_str
                    updated_count += 1
        
        # Save database
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
        
        print(f"   ✓ Updated {updated_count} questions with correct answers")
    
    def save_to_file(self):
        """Save answer key to JSON file"""
        output_file = Path("bulk-import/asiav6-answer-key.json")
        with open(output_file, 'w') as f:
            json.dump(self.answer_key, f, indent=2)
        print(f"   ✓ Saved answer key to {output_file}")
    
    def run(self):
        """Run extraction"""
        try:
            self.extract()
            self.save_to_file()
            self.apply_to_database()
            
            print("\n" + "=" * 80)
            print("✅ ANSWER KEY EXTRACTION COMPLETE!")
            print("=" * 80)
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.doc.close()

if __name__ == "__main__":
    pdf_path = "bulk-import/202503asiav6-2.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ Error: PDF not found at {pdf_path}")
        exit(1)
    
    extractor = AnswerKeyExtractor(pdf_path)
    extractor.run()

