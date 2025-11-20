# 🗺️ Image Mapping Guide

## Based on PDF Page Numbers

Here's a guide to help you identify which images belong to which questions:

### 📄 Page 20 (2 images)
**Likely Question 2** - Graph showing two lines intersecting at (5,5)
- `202503asiav1 (1)_page20_img1.png` → Probably the graph
- `202503asiav1 (1)_page20_img2.png` → Possibly another view or different graph

**Suggested rename:**
- `q2-graph.png` (for the main graph)

### 📄 Page 21 (2 images)
**Likely Question 11** - Data table
- `202503asiav1 (1)_page21_img1.png` → Probably the table
- `202503asiav1 (1)_page21_img2.png` → Possibly table continuation

**Suggested rename:**
- `q11-table.png`

### 📄 Page 24 (7 images)
**Likely Question 1** - Math question with graph choices
- Multiple images = probably the 4 graph options (A, B, C, D)
- Plus possibly the question itself

**Suggested rename:**
- `math-q1-optionA.png`
- `math-q1-optionB.png`
- `math-q1-optionC.png`
- `math-q1-optionD.png`

### 📄 Page 25 (9 images)
**Likely Question 1 continued** - More math graphs
- Probably more graph options or related images

### 📄 Page 22, 23, 26, 28, 30, 31, 32
**Other questions** - Need to check PDF to identify

## 🔍 How to Identify Images

### Method 1: Use the Helper Script
```bash
python bulk-import/identify-images.py
```
This will open each image for you to identify.

### Method 2: Manual Check
1. Open your PDF (`202503asiav1 (1).pdf`)
2. Go to each page number
3. See which question is on that page
4. Match the image to the question

### Method 3: Quick Visual Check
Open the images folder and preview images:
- Look for graphs → Math questions
- Look for tables → Data analysis questions
- Look for charts → Reading/Writing questions

## 📝 Quick Reference

| PDF Page | Question # | Image Type | Suggested Filename |
|----------|-----------|------------|-------------------|
| 20 | 2 | Graph | `q2-graph.png` |
| 21 | 11 | Table | `q11-table.png` |
| 24 | 1 | Math graphs (4) | `math-q1-optionA.png` etc. |
| 25 | 1 | Math graphs (more) | `math-q1-option*.png` |

## 🚀 Next Steps

1. **Identify images** using the script or manual check
2. **Rename images** to match questions (e.g., `q2-graph.png`)
3. **Add questions to CSV** with correct image filenames
4. **Run import**: `python import.py`

