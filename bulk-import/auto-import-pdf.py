#!/usr/bin/env python3
"""
ONE-COMMAND PDF IMPORT TOOL
Just run: python3 auto-import-pdf.py your-pdf.pdf

This will:
1. Extract all questions from the PDF
2. Extract all images from the PDF
3. Match images to questions based on page layout
4. Copy images to the correct folder
5. Add everything to questions-database.json

No manual work needed!
"""

import fitz  # PyMuPDF
import json
import shutil
import re
from pathlib import Path
from collections import defaultdict

class PDFImporter:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.pdf_name = Path(pdf_path).stem
        
        # Configuration - UPDATE THESE for your test
        self.module = "Math Module 1"
        self.date = "2025-03"
        self.region = "Asia"
        self.test_number = 1
        self.subject = "Math"
        
        # Storage
        self.questions = {}
        self.images_by_page = defaultdict(list)
        self.image_folder = Path("bulk-import/images")
        self.target_folder = Path(f"images/{self.date}/{self.region.lower()}v{self.test_number}")
        
    def extract_images(self):
        """Extract all images from PDF, organized by page"""
        print(f"📸 Extracting images from {self.pdf_name}...")
        
        self.image_folder.mkdir(parents=True, exist_ok=True)
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    pix = fitz.Pixmap(self.doc, xref)
                    
                    if pix.n - pix.alpha < 4:  # RGB or Grayscale
                        filename = f"p{page_num + 1}_img{img_index + 1}.png"
                        filepath = self.image_folder / filename
                        pix.save(filepath)
                        
                        # Get image position on page
                        img_rects = page.get_image_rects(xref)
                        y_position = img_rects[0].y0 if img_rects else 0
                        
                        self.images_by_page[page_num].append({
                            'filename': filename,
                            'filepath': filepath,
                            'y_position': y_position,
                            'index': img_index
                        })
                        print(f"  ✓ Page {page_num + 1}, Image {img_index + 1}")
                    
                    pix = None
                except Exception as e:
                    print(f"  ⚠️  Error extracting image on page {page_num + 1}: {e}")
        
        print(f"✅ Extracted {sum(len(imgs) for imgs in self.images_by_page.values())} images")
    
    def extract_questions(self):
        """Extract questions from PDF with smart image matching"""
        print(f"\n📝 Extracting questions from {self.pdf_name}...")
        
        current_question = None
        question_pages = {}  # Track which page each question is on
        current_module = None
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text = page.get_text()
            lines = text.split('\n')
            
            # Detect module changes
            for line in lines:
                if 'Math Module 1' in line:
                    current_module = 'Math Module 1'
                elif 'Math Module 2' in line:
                    current_module = 'Math Module 2'
                elif 'Reading and Writing Module' in line:
                    current_module = None  # Skip R&W modules
            
            # Only process Math Module 1
            if current_module != 'Math Module 1':
                continue
            
            # Get text blocks with positions for better matching
            blocks = page.get_text("dict")["blocks"]
            
            for line in lines:
                stripped = line.strip()
                
                # Check if this is a question number (standalone number)
                if re.match(r'^(\d+)$', stripped):
                    q_num = int(stripped)
                    
                    # Only process questions 1-22 for Math Module 1
                    if q_num > 22:
                        continue
                    
                    # Save previous question
                    if current_question and current_question['number']:
                        self.questions[current_question['number']] = current_question
                    
                    # Start new question
                    current_question = {
                        'number': q_num,
                        'text': '',
                        'page': page_num,
                        'has_text': [],
                        'module': current_module
                    }
                    question_pages[q_num] = page_num
                    print(f"  Found Q{q_num} on page {page_num + 1}")
                
                elif current_question and stripped:
                    # Skip headers/footers
                    if 'Module' not in stripped and 'QUESTIONS' not in stripped and 'CONTINUE' not in stripped:
                        current_question['has_text'].append(stripped)
        
        # Save last question
        if current_question and current_question['number']:
            self.questions[current_question['number']] = current_question
        
        # Combine text for each question
        for q_num, q in self.questions.items():
            q['text'] = ' '.join(q['has_text']).strip()
            del q['has_text']
        
        print(f"✅ Extracted {len(self.questions)} questions")
        
        # Now match images to questions
        self.match_images_to_questions()
    
    def match_images_to_questions(self):
        """Intelligently match images to questions based on keywords and position"""
        print(f"\n🔗 Matching images to questions...")
        
        # Keywords that indicate a question SHOWS an image (not just mentions it)
        image_keywords = [
            'scatterplot shows', 'chart shows', 'table shows', 'diagram shows',
            'figure shows', 'graph shows', 'plot shows',
            'shown in', 'shown below', 'displayed',
            'rectangle shown', 'triangle shown', 'circle shown',
            'the graph of', 'visual', 'illustration', 'depicts'
        ]
        
        # Track which images have been used
        used_images = set()
        
        # Sort questions by number to process in order
        sorted_questions = sorted(self.questions.items(), key=lambda x: x[0])
        
        for q_num, q in sorted_questions:
            q_text_lower = q['text'].lower()
            page_num = q['page']
            
            # Check if question is ONLY answer choices (A) B) C) D)) - means images ARE the question
            is_only_choices = re.match(r'^[\s\w]*a\)\s*b\)\s*c\)\s*d\)[\s\w]*$', q_text_lower.replace('\n', ' '))
            
            # Check if question text suggests it needs an image
            needs_image = any(re.search(keyword, q_text_lower) for keyword in image_keywords)
            
            # Special checks for specific question types
            has_which_choice = 'which of the following' in q_text_lower
            has_graph_choice = 'graph' in q_text_lower and ('could be' in q_text_lower or 'following' in q_text_lower)
            is_system_equation = 'system' in q_text_lower and 'equation' in q_text_lower
            
            # Check current page AND next page for images (questions can span pages)
            available_images = []
            for check_page in [page_num, page_num + 1]:
                if check_page in self.images_by_page:
                    page_images = [img for img in self.images_by_page[check_page] 
                                  if img['filename'] not in used_images]
                    available_images.extend(page_images)
                
            if available_images:
                # Check for image answer choices (4 options A/B/C/D)
                if is_only_choices or ((has_graph_choice or is_system_equation) and has_which_choice):
                    # Look for 4 consecutive images
                    if len(available_images) >= 4:
                        q['image_type'] = 'choices'
                        q['images'] = [img['filename'] for img in available_images[:4]]
                        # Mark these images as used
                        for img in available_images[:4]:
                            used_images.add(img['filename'])
                        if is_only_choices:
                            print(f"  Q{q_num}: 4 image choices (question IS images)")
                        else:
                            print(f"  Q{q_num}: 4 image choices (A/B/C/D)")
                    elif len(available_images) >= 2:
                        # Sometimes only 2 choices
                        q['image_type'] = 'choices'
                        q['images'] = [img['filename'] for img in available_images[:2]]
                        for img in available_images[:2]:
                            used_images.add(img['filename'])
                        print(f"  Q{q_num}: 2 image choices")
                    else:
                        q['image_type'] = 'single'
                        q['images'] = [available_images[0]['filename']]
                        used_images.add(available_images[0]['filename'])
                        print(f"  Q{q_num}: 1 image")
                    
                elif needs_image:
                    # Single image (diagram, table, chart, etc.)
                    q['image_type'] = 'single'
                    q['images'] = [available_images[0]['filename']]
                    used_images.add(available_images[0]['filename'])
                    print(f"  Q{q_num}: 1 image")
                else:
                    # No clear image indicators
                    q['image_type'] = 'none'
                    q['images'] = []
            else:
                # No images available
                q['image_type'] = 'none'
                q['images'] = []
        
        # Report unmatched images
        total_images = sum(len(imgs) for imgs in self.images_by_page.values())
        matched_images = len(used_images)
        if matched_images < total_images:
            print(f"  ⚠️  {total_images - matched_images} images were not matched to questions")
    
    def copy_images_to_target(self):
        """Copy images to the final destination folder"""
        print(f"\n📂 Copying images to {self.target_folder}...")
        self.target_folder.mkdir(parents=True, exist_ok=True)
        
        copied = 0
        for q_num, q in self.questions.items():
            if q['images']:
                for idx, img_filename in enumerate(q['images']):
                    source = self.image_folder / img_filename
                    
                    if source.exists():
                        # Generate clean filename
                        if q['image_type'] == 'choices':
                            option = ['A', 'B', 'C', 'D'][idx]
                            target_name = f"math-q{q_num}-option{option}.png"
                        else:
                            target_name = f"math-q{q_num}.png"
                        
                        target = self.target_folder / target_name
                        shutil.copy(source, target)
                        
                        # Update the image filename in question data
                        q['images'][idx] = str(self.target_folder / target_name)
                        copied += 1
        
        print(f"✅ Copied {copied} images")
    
    def add_to_database(self):
        """Add questions to questions-database.json"""
        print(f"\n💾 Adding questions to database...")
        
        db_path = Path("questions-database.json")
        
        # Load existing database
        with open(db_path, 'r') as f:
            database = json.load(f)
        
        # Get next ID
        next_id = max(q['id'] for q in database) + 1
        
        # Add questions
        added = 0
        for q_num in sorted(self.questions.keys()):
            q = self.questions[q_num]
            
            # Create question object
            question = {
                "id": next_id,
                "module": self.module,
                "questionNumber": q_num,
                "totalQuestions": len(self.questions),
                "date": self.date,
                "region": self.region,
                "testNumber": self.test_number,
                "testName": f"{self.date} {self.region} Test {self.test_number}",
                "questionText": q['text'],
                "prompt": "",
                "choices": ["A", "B", "C", "D"],  # Placeholder
                "correctAnswer": 0,  # TODO: Update this
                "explanation": "",  # TODO: Update this
                "difficulty": "medium",
                "topic": "general",
                "subject": self.subject
            }
            
            # Add images
            if q['image_type'] == 'choices':
                question['hasImageChoices'] = True
                question['choices'] = q['images']
            elif q['image_type'] == 'single':
                question['imageUrl'] = q['images'][0]
            
            database.append(question)
            next_id += 1
            added += 1
            
            print(f"  ✓ Added Q{q_num}")
        
        # Save database
        with open(db_path, 'w') as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Added {added} questions to database")
    
    def run(self):
        """Run the complete import process"""
        print("="*80)
        print("🚀 SAT QUESTION AUTO-IMPORT TOOL")
        print("="*80)
        
        self.extract_images()
        self.extract_questions()
        self.copy_images_to_target()
        self.add_to_database()
        
        print("\n" + "="*80)
        print("✅ IMPORT COMPLETE!")
        print("="*80)
        print(f"📊 Summary:")
        print(f"   • {len(self.questions)} questions imported")
        print(f"   • Images saved to: {self.target_folder}")
        print(f"   • Database updated: questions-database.json")
        print("\n⚠️  Remember to:")
        print("   • Add correct answers (currently all set to 'A')")
        print("   • Add explanations")
        print("   • Verify image matches")
        
        self.doc.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 auto-import-pdf.py <pdf-file>")
        print("\nExample:")
        print("  python3 auto-import-pdf.py bulk-import/202503asiav1.pdf")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    
    if not Path(pdf_file).exists():
        print(f"❌ Error: File not found: {pdf_file}")
        sys.exit(1)
    
    importer = PDFImporter(pdf_file)
    importer.run()

