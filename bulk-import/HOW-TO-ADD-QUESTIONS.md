# 📖 Step-by-Step Guide: Adding Questions from PDF

## 🎯 What You Need to Do

You have a PDF with questions. Here's how to add them:

---

## Step 1: Extract Images from PDF

### Option A: Screenshot Method (Easiest) ⭐ RECOMMENDED

1. **Open your PDF** (like `202503asiav1.pdf`)

2. **For each question with a graph/chart:**
   - Scroll to the question
   - Take a screenshot of JUST the graph/chart
   - On Mac: `Cmd + Shift + 4`, then drag to select the graph
   - Save it with a clear name like `q2-graph.png`

3. **Save screenshots to:**
   ```
   bulk-import/images/
   ```

### Option B: Export from PDF (Better Quality)

1. **Using Preview (Mac):**
   - Open PDF in Preview
   - Select the graph/chart area
   - Copy (`Cmd + C`)
   - Open Preview → New from Clipboard
   - Export as PNG: `File → Export → Format: PNG`
   - Save to `bulk-import/images/q2-graph.png`

2. **Using Adobe Acrobat:**
   - Tools → Export PDF → Image → PNG
   - Select pages with graphs
   - Export to `bulk-import/images/`

---

## Step 2: Name Your Images

**Naming Convention:**
- `q1-chart.png` - Chart for question 1
- `q2-graph.png` - Graph for question 2
- `q11-table.png` - Table for question 11
- `math-q1-optionA.svg` - Math question 1, choice A (if choices are images)

**Put all images in:** `bulk-import/images/`

---

## Step 3: Add Questions to CSV

Open `bulk-import/questions.csv` in Excel, Google Sheets, or a text editor.

### Example 1: Question WITHOUT Image (Question 1 from your PDF)

```csv
1,"A jar has 310 buttons, and 20% of these buttons are green. How many buttons in the jar are green?","","62","310","20","155","A","20% of 310 = 0.20 × 310 = 62","","","easy","percentages","Math Module 1","2025-03","Asia",1,"2025-03 Asia Test 1","Math"
```

**Key points:**
- `question_number`: 1
- `question_text`: The question text
- `image_name`: Leave empty `""` (no image)
- `correct_answer`: A

### Example 2: Question WITH Image (Question 2 from your PDF)

**First, extract the graph:**
1. Screenshot the graph from question 2
2. Save as `bulk-import/images/q2-graph.png`

**Then add to CSV:**

```csv
2,"The solution to a system of linear equations is (5, 5). Which of the following could be the graph of the equations in the system?","","images/2025-03/asiav1/math-q2-optionA.svg","images/2025-03/asiav1/math-q2-optionB.svg","images/2025-03/asiav1/math-q2-optionC.svg","images/2025-03/asiav1/math-q2-optionD.svg","A","The two lines intersect at (5, 5), which is the solution to the system.","","","medium","systems-of-equations","Math Module 1","2025-03","Asia",1,"2025-03 Asia Test 1","Math"
```

**OR if the graph is part of the question (not a choice):**

```csv
2,"The solution to a system of linear equations is (5, 5). Which of the following could be the graph of the equations in the system?","","Graph A description","Graph B description","Graph C description","Graph D description","A","The two lines intersect at (5, 5).","q2-graph.png","Graph showing two lines intersecting at (5,5)","medium","systems-of-equations","Math Module 1","2025-03","Asia",1,"2025-03 Asia Test 1","Math"
```

---

## Step 4: Fill Out CSV Columns

For each question, fill these columns:

| Column | What to Put | Example |
|--------|-------------|---------|
| `question_number` | Question number | `1`, `2`, `3` |
| `question_text` | Full question text | `"A jar has 310 buttons..."` |
| `prompt` | Question prompt | `"Which choice..."` or leave empty |
| `choice_a` | First choice | `"62"` or `"images/.../optionA.svg"` |
| `choice_b` | Second choice | `"310"` |
| `choice_c` | Third choice | `"20"` |
| `choice_d` | Fourth choice | `"155"` |
| `correct_answer` | A, B, C, or D | `"A"` |
| `explanation` | Why it's correct | `"20% of 310 = 62"` |
| `image_name` | Image filename | `"q2-graph.png"` or `""` if no image |
| `image_caption` | Image description | `"Graph showing lines"` |
| `difficulty` | easy, medium, or hard | `"easy"` |
| `topic` | Question topic | `"percentages"`, `"systems-of-equations"` |
| `module` | Module name | `"Math Module 1"` |
| `date` | Test date | `"2025-03"` |
| `region` | Region | `"Asia"` |
| `test_number` | Test number | `1` |
| `test_name` | Full test name | `"2025-03 Asia Test 1"` |
| `subject` | Subject | `"Math"` or `"English"` |

---

## Step 5: Run the Import Script

Once you've:
- ✅ Added images to `bulk-import/images/`
- ✅ Added questions to `bulk-import/questions.csv`

Run:

```bash
python import.py
```

The script will:
- Copy images to the right location
- Add questions to your database
- Show you progress messages

---

## 📋 Quick Checklist

Before running the script:

- [ ] Images extracted and saved to `bulk-import/images/`
- [ ] Images named clearly (e.g., `q2-graph.png`)
- [ ] Questions added to `bulk-import/questions.csv`
- [ ] Image filenames in CSV match actual image files
- [ ] All required columns filled in CSV

---

## 🎨 Visual Example

**Your folder should look like:**

```
bulk-import/
├── questions.csv
└── images/
    ├── q2-graph.png          ← Screenshot of question 2's graph
    ├── q11-table.png         ← Screenshot of question 11's table
    └── q13-chart.png         ← Screenshot of question 13's chart
```

**Your CSV should have:**

```csv
question_number,question_text,...,image_name,...
1,"Question text...","","","","","A","Explanation","","","easy","topic",...
2,"Question with graph...","","A","B","C","D","A","Explanation","q2-graph.png","Graph description","medium","topic",...
```

---

## 💡 Pro Tips

1. **Batch Screenshots:** Take all screenshots first, then add to CSV
2. **Name Consistently:** Use `q1-`, `q2-`, `q3-` prefix for easy matching
3. **Test One First:** Add 1-2 questions, run script, check if it works
4. **Keep PDF Open:** Have PDF open while filling CSV to copy text accurately
5. **Check Image Quality:** Make sure graphs are readable in screenshots

---

## 🆘 Need Help?

**Image not showing?**
- Check filename matches exactly (case-sensitive)
- Make sure image is in `bulk-import/images/` folder

**Script error?**
- Check CSV format (commas, quotes)
- Make sure all columns are present
- Check for typos in filenames

**Question not appearing?**
- Check `questions-database.json` was updated
- Look for error messages in script output

