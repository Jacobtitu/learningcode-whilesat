# 🚀 How to Run Your App Locally

## Quick Start

### Option 1: Using the Script (Easiest)

```bash
./start-server.sh
```

Then open: **http://localhost:8000**

### Option 2: Manual Python Server

```bash
python3 -m http.server 8000
```

Then open: **http://localhost:8000**

### Option 3: Using Python 2 (if Python 3 not available)

```bash
python -m SimpleHTTPServer 8000
```

Then open: **http://localhost:8000**

## 📋 Step-by-Step

1. **Open Terminal**
   - On Mac: Press `Cmd + Space`, type "Terminal", press Enter

2. **Navigate to your project folder**
   ```bash
   cd /Users/jacobtituana/learningcode-whilesat
   ```

3. **Start the server**
   ```bash
   python3 -m http.server 8000
   ```

4. **Open in browser**
   - Open your web browser
   - Go to: **http://localhost:8000**
   - Or: **http://127.0.0.1:8000**

5. **Stop the server**
   - Press `Ctrl + C` in the terminal

## 🌐 Your Pages

Once the server is running, you can access:

- **Home:** http://localhost:8000/index.html
- **Practice Questions:** http://localhost:8000/practice.html
- **Dynamic Questions:** http://localhost:8000/dynamic-questions.html
- **Select Date:** http://localhost:8000/select-date.html

## ⚠️ Important Notes

- **Keep the terminal open** - The server runs as long as the terminal is open
- **Don't close the terminal** - Closing it stops the server
- **Use Ctrl+C to stop** - Press Ctrl+C when you're done

## 🔧 Troubleshooting

**Port 8000 already in use?**
```bash
python3 -m http.server 8001
```
Then use: http://localhost:8001

**Python not found?**
- Install Python from: https://www.python.org/downloads/
- Or use: `python` instead of `python3`

## 💡 Pro Tip

You can bookmark **http://localhost:8000** in your browser for quick access!

