#!/usr/bin/env python3
"""
Review and correct OCR errors in Asia v6 questions
Shows questions with potential OCR errors and allows easy correction
"""

import json
import re
from pathlib import Path

class OCRReviewer:
    def __init__(self):
        self.db_path = Path("questions-database.json")
        with open(self.db_path, 'r', encoding='utf-8') as f:
            self.database = json.load(f)
        
        self.questions = [q for q in self.database if q.get('testId') == 'asiav6']
        
        # Common OCR error patterns
        self.ocr_fixes = {
            r'\bg\b': 'g',  # Fix isolated 'g'
            r'oudatea': 'outdated',
            r'variea': 'varied',
            r'forgoren': 'forgotten',
            r'Rea\'\\g': 'Reading',
            r'\\g and Writing': 'Reading and Writing',
            r'Highgnts': 'Highlights',
            r'31:5O': '',  # Remove timestamps
            r'31:4O': '',
            r'2O': '',
            r':\s*:\s*': '',  # Remove double colons
            r'^\s*&\s*$': '',  # Remove standalone &
            r'^\s*=\s*$': '',  # Remove standalone =
            r'sea\s+&': '',  # Remove UI elements
            r'Directions\s+&': '',
            r'More\s+ae': '',
            r'Ea\s+&': '',
            r'Section \d+,\s*Module \d+:\s*': '',  # Remove section headers
            r'^\s*[:\-=&]+\s*$': '',  # Remove lines of just symbols
        }
    
    def clean_text(self, text):
        """Apply common OCR fixes"""
        if not text:
            return text
        
        # Apply fixes
        for pattern, replacement in self.ocr_fixes.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing symbols
        text = re.sub(r'^[:\-=&\s]+', '', text)
        text = re.sub(r'[:\-=&\s]+$', '', text)
        
        return text.strip()
    
    def find_ocr_errors(self):
        """Find questions with potential OCR errors"""
        errors = []
        
        for q in self.questions:
            text = q.get('questionText', '')
            if not text:
                continue
            
            # Check for common OCR error patterns
            has_errors = False
            error_types = []
            
            # Check for weird characters
            if re.search(r'[®©○●]', text):
                has_errors = True
                error_types.append('special_chars')
            
            # Check for common OCR mistakes
            if re.search(r'oudatea|variea|forgoren|Rea\'|Highgnts', text, re.IGNORECASE):
                has_errors = True
                error_types.append('common_errors')
            
            # Check for UI elements
            if re.search(r'Section \d+|Module \d+:|Directions|Highlights|Notes|More|31:\d+', text):
                has_errors = True
                error_types.append('ui_elements')
            
            # Check for incomplete text (very short)
            if len(text) < 50:
                has_errors = True
                error_types.append('incomplete')
            
            if has_errors:
                errors.append({
                    'id': q['id'],
                    'question': q,
                    'error_types': error_types
                })
        
        return errors
    
    def auto_fix_questions(self):
        """Automatically fix common OCR errors"""
        print("🔧 Auto-fixing common OCR errors...\n")
        
        fixed_count = 0
        for q in self.questions:
            original_text = q.get('questionText', '')
            if not original_text:
                continue
            
            # Clean text
            cleaned_text = self.clean_text(original_text)
            
            if cleaned_text != original_text:
                q['questionText'] = cleaned_text
                fixed_count += 1
        
        # Also clean choices
        for q in self.questions:
            choices = q.get('choices', [])
            if choices:
                cleaned_choices = []
                for choice in choices:
                    if choice:
                        cleaned = self.clean_text(choice)
                        cleaned_choices.append(cleaned)
                    else:
                        cleaned_choices.append('')
                q['choices'] = cleaned_choices
        
        print(f"   ✓ Fixed {fixed_count} questions")
        return fixed_count
    
    def show_errors(self):
        """Show questions with errors"""
        errors = self.find_ocr_errors()
        
        print(f"\n⚠️  Found {len(errors)} questions with potential OCR errors:\n")
        
        for i, error in enumerate(errors[:20], 1):  # Show first 20
            q = error['question']
            print(f"{i}. Q{q['questionNumber']} ({q['module']})")
            print(f"   Errors: {', '.join(error['error_types'])}")
            text = q.get('questionText', '')[:200]
            print(f"   Text: {text}...")
            print()
        
        if len(errors) > 20:
            print(f"   ... and {len(errors) - 20} more")
        
        return errors
    
    def save_database(self):
        """Save updated database"""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.database, f, indent=2, ensure_ascii=False)
        print(f"   ✓ Saved database")

if __name__ == "__main__":
    reviewer = OCRReviewer()
    
    print("=" * 80)
    print("🔍 OCR ERROR REVIEWER")
    print("=" * 80)
    
    # Show errors
    errors = reviewer.show_errors()
    
    # Auto-fix
    fixed = reviewer.auto_fix_questions()
    
    # Save
    reviewer.save_database()
    
    print("\n" + "=" * 80)
    print("✅ REVIEW COMPLETE!")
    print(f"   Found {len(errors)} questions with errors")
    print(f"   Auto-fixed {fixed} questions")
    print("=" * 80)

