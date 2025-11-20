# ⚡ Quick Start: Add Your First Question

## In 3 Simple Steps

### Step 1: Extract One Image 📸

1. Open your PDF (`202503asiav1.pdf`)
2. Find Question 2 (the one with the graph)
3. Take a screenshot of the graph:
   - Mac: `Cmd + Shift + 4`
   - Drag to select just the graph
   - Save as: `q2-graph.png`
4. Put it here: `bulk-import/images/q2-graph.png`

### Step 2: Add to CSV 📝

Open `bulk-import/questions.csv` and add this row at the end:

```csv
2,"The solution to a system of linear equations is (5, 5). Which of the following could be the graph of the equations in the system?","","Graph A","Graph B","Graph C","Graph D","A","The two lines intersect at (5, 5), which is the solution to the system.","q2-graph.png","Graph showing two lines intersecting at (5,5)","medium","systems-of-equations","Math Module 1","2025-03","Asia",1,"2025-03 Asia Test 1","Math"
```

**Important:** Make sure the image filename `q2-graph.png` matches what you saved!

### Step 3: Run Script 🚀

```bash
python import.py
```

**Done!** Check `questions-database.json` - your question should be there!

---

## For Question 1 (No Image Needed)

Add this row to CSV:

```csv
1,"A jar has 310 buttons, and 20% of these buttons are green. How many buttons in the jar are green?","","62","310","20","155","A","20% of 310 = 0.20 × 310 = 62","","","easy","percentages","Math Module 1","2025-03","Asia",1,"2025-03 Asia Test 1","Math"
```

Notice: `image_name` is empty `""` because this question has no image.

---

## That's It! 🎉

Once you do this once, you'll understand the pattern. Then you can add all 22 questions the same way!

