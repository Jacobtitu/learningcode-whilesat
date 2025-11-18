# Image Support Instructions

## How to Add Images to Your SAT Questions

### 1. Extract Images from PDFs

#### Method A: Screenshot (Easiest)
1. Open your PDF (e.g., 202503asiav1.pdf)
2. Navigate to the question with a chart/graph
3. Take a screenshot of just the visual element
4. Save as PNG: `question-[number]-[description].png`

#### Method B: PDF Export
1. Use Adobe Acrobat or Preview
2. Export images from PDF
3. Crop to show just the relevant chart/graph
4. Save in appropriate folder

### 2. Organize Images

#### Folder Structure:
```
images/
├── 2025-03/
│   ├── asiav1/
│   │   ├── question-11-table.png
│   │   ├── question-12-chart.png
│   │   ├── question-15-diagram.png
│   │   └── ...
│   ├── asiav2/
│   ├── usv1/
│   └── ...
├── 2025-05/
└── ...
```

#### Naming Convention:
- `question-[number]-[type].png`
- Examples:
  - `question-11-table.png` (data table)
  - `question-15-graph.png` (line graph)
  - `question-20-diagram.png` (scientific diagram)

### 3. Add to JSON Database

```json
{
  "questionText": "The chart shows...",
  "imageUrl": "images/2025-03/asiav1/question-11-table.png",
  "imageCaption": "Population Growth Data Table" 
}
```

### 4. Image Best Practices

#### File Requirements:
- **Format**: PNG (best quality) or JPG
- **Size**: Under 500KB for web performance
- **Dimensions**: Max 800px wide for readability
- **Quality**: High enough to read all text/numbers

#### When to Use Images vs Text:
- **Use Images**: Complex graphs, scientific diagrams, geometric figures
- **Use Text**: Simple tables, basic data that can be described
- **Hybrid**: Describe the image AND include visual for clarity

### 5. Testing Your Images

1. Add image to correct folder
2. Update JSON with imageUrl
3. Test in browser - image should appear
4. Click image to zoom (modal view)
5. Check on mobile devices

### 6. Troubleshooting

#### Image Not Showing:
- Check file path is correct
- Verify image exists in folder
- Check image file name spelling
- Ensure server is running

#### Image Too Large:
- Resize to max 800px wide
- Compress using online tools
- Consider cropping unnecessary parts

#### Poor Quality:
- Use higher resolution screenshot
- Export at higher DPI from PDF
- Ensure text in image is readable