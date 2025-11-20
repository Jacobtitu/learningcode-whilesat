# 🎯 Quick Image Identification Guide

## Most Important Images (Based on Your PDF)

### ✅ Question 2 - Graph (Page 20)
**The graph showing two lines intersecting at (5,5)**

Look for these files:
- `202503asiav1 (1)_page20_img1.png` 
- `202503asiav1 (1)_page20_img2.png`

**Action:** Open both and see which one shows the graph. Rename it to:
- `q2-graph.png`

### ✅ Question 1 - Math Graphs (Page 24-25)
**Math question with 4 graph choices (A, B, C, D)**

You have 16 images total from pages 24-25. These are likely:
- 4 graphs for Question 1 (options A, B, C, D)
- Possibly more math questions

**Action:** Look for 4 similar graphs that show coordinate systems. Rename them:
- `math-q1-optionA.png`
- `math-q1-optionB.png`
- `math-q1-optionC.png`
- `math-q1-optionD.png`

### ✅ Question 11 - Table (Page 21)
**Data table question**

Look for:
- `202503asiav1 (1)_page21_img1.png` - Probably the table
- `202503asiav1 (1)_page21_img2.png` - Possibly continuation

**Action:** Rename to:
- `q11-table.png`

## 🔍 How to Identify Them

### Option 1: Open Images Manually
1. Go to `bulk-import/images/` folder
2. Open images starting with `page20`, `page21`, `page24`, `page25`
3. Match them to your PDF

### Option 2: Use Finder Preview
1. Open Finder
2. Navigate to `bulk-import/images/`
3. Select images and press Spacebar to preview
4. Compare with your PDF

## 📋 Quick Checklist

For Question 2:
- [ ] Open `page20_img1.png` and `page20_img2.png`
- [ ] Find the one with two lines intersecting at (5,5)
- [ ] Rename it to `q2-graph.png`

For Question 1:
- [ ] Look at images from page 24-25
- [ ] Find 4 graphs that look like coordinate systems
- [ ] Rename them to `math-q1-optionA.png`, `optionB.png`, etc.

## 🚀 After Identifying

Once you've identified and renamed the key images:

1. **Update CSV** with correct image filenames
2. **Run:** `python import.py`

