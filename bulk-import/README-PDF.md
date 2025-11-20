# 📄 Using PDF Files

## ✅ Yes! You Can Drag PDFs Here

You can absolutely drag PDF files into the `bulk-import/` folder!

## 🚀 Two Ways to Use PDFs

### Method 1: Automatic Image Extraction (Recommended)

1. **Drag your PDF** into `bulk-import/` folder
   - Example: `bulk-import/202503asiav1.pdf`

2. **Extract images automatically:**
   ```bash
   bash bulk-import/extract-pdf.sh
   ```
   
   Or manually:
   ```bash
   python bulk-import/extract-images-from-pdf.py bulk-import/202503asiav1.pdf
   ```

3. **Images will be saved to:** `bulk-import/images/`
   - Named like: `202503asiav1_page20_img1.png`
   - You'll need to rename them to match your questions (e.g., `q2-graph.png`)

4. **Add questions to CSV** (still need to do this manually)
   - Open `bulk-import/questions.csv`
   - Add your questions
   - Reference the extracted images

### Method 2: Manual Screenshot (Easier for Few Questions)

1. Open PDF
2. Take screenshots of graphs/charts
3. Save to `bulk-import/images/`
4. Add to CSV

## 📋 What You Still Need to Do

Even with PDF extraction, you still need to:

1. ✅ Extract images (automatic or manual)
2. ✅ Add questions to CSV (manual - need to type question text)
3. ✅ Match image filenames in CSV
4. ✅ Run `python import.py`

## 💡 Pro Tip

**Best workflow:**
1. Drag PDF into `bulk-import/`
2. Run extraction script to get all images
3. Look at extracted images, rename them to match questions
4. Add questions to CSV with correct image names
5. Run `python import.py`

## ⚠️ Note

The PDF extraction gets ALL images from the PDF. You'll need to:
- Identify which images belong to which questions
- Rename them appropriately (e.g., `q2-graph.png`)
- Some images might be logos/headers - you can ignore those

## 🔧 Requirements

For automatic extraction, you need:
```bash
pip install PyMuPDF
```

The script will try to install it automatically if missing.

