# 📚 Bulk Import SAT Questions - EASY MODE

## 🎯 One-Command Import (Recommended)

Import an entire PDF of SAT questions with images in ONE command:

```bash
cd bulk-import
./import.sh your-pdf-file.pdf
```

**That's it!** The script will:
- ✅ Extract all questions from the PDF
- ✅ Extract all images from the PDF  
- ✅ Match images to questions automatically
- ✅ Copy images to the correct folders
- ✅ Add everything to `questions-database.json`

### Example:
```bash
cd bulk-import
./import.sh 202503asiav1.pdf
```

---

## 🎛️ Advanced: Manual CSV Import

If you prefer manual control, use the CSV method:

### Step 1: Extract Images
```bash
cd bulk-import
./extract-pdf.sh your-pdf.pdf
```

### Step 2: Fill in `questions.csv`
Edit `questions.csv` with your question data and image filenames.

### Step 3: Import
```bash
cd ..
python3 import.py
```

---

## 📝 After Import

1. **View your questions:**
   - Run: `./start-server.sh`
   - Open: http://localhost:8000/dynamic-questions.html
   - Select your module

2. **Update correct answers** in `questions-database.json`
   - Find your questions by ID
   - Change `"correctAnswer": 0` to the right answer (0=A, 1=B, 2=C, 3=D)

3. **Add explanations**
   - Edit the `"explanation"` field

---

## 🔧 Configuration

Edit settings at the top of `auto-import-pdf.py`:

```python
self.module = "Math Module 1"      # Change module name
self.date = "2025-03"              # Change date
self.region = "Asia"               # Change region
self.test_number = 1               # Change test number
self.subject = "Math"              # Math or English
```

---

## ❓ Troubleshooting

**Images not showing?**
- Hard refresh browser: `Cmd + Shift + R` (Mac) or `Ctrl + Shift + R` (Windows)
- Check that images are in `images/2025-03/asiav1/` folder

**Questions extracted wrong?**
- The script uses smart keywords to detect images
- For special cases, manually edit the JSON after import

**Need help?**
- Check the console output for errors
- Images are temporarily saved in `bulk-import/images/` for review
