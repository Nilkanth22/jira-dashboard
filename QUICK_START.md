# Quick Start: Running with Auto-Update

## The Problem
When opening `dashboard.html` directly (file:// protocol), the browser **cannot write files** to your computer for security reasons. So uploaded CSVs download new JSON files that you must manually replace.

## The Solution: Use Flask Backend

### One-Time Setup (2 minutes)
```bash
# Install Flask (if not already installed)
pip install flask pandas werkzeug
```

### Start the Server
**Double-click:** `start_server.bat`

OR run manually:
```bash
python app.py
```

You'll see:
```
* Running on http://127.0.0.1:5000
```

### Access Your Dashboard
Open browser and go to: **http://localhost:5000**

## How It Works Now

### ✅ With Flask Backend (Recommended)
1. Upload CSV via dashboard
2. **Files update automatically** in your folder
3. Refresh page → see changes immediately
4. **Everyone** on your network can access (optional)

**No manual file copying needed!**

### ❌ Without Flask (Opening dashboard.html directly)
1. Upload CSV
2. Downloads new JSON files
3. **You must manually replace** old files
4. Then refresh

## Features with Flask Backend

### Auto-Update
- Upload CSV → `data.csv`, `cases.json`, `data.json` update automatically
- Comments & planned weeks preserved
- No downloads or file copying

### Collaborative (Bonus!)
When running Flask server:
- Share URL with team: `http://your-ip:5000`
- Anyone uploads CSV → everyone sees updates
- Real-time collaboration!

### Comments Persist
- Type comment → saves to server immediately
- Survives CSV uploads
- Visible to all users

## Network Access (Optional)

To allow team members to access from other computers:

1. Find your IP address:
```bash
ipconfig
# Look for IPv4 Address (e.g., 192.168.1.100)
```

2. Share this URL with team:
```
http://192.168.1.100:5000
```

3. They can upload CSVs and everyone sees updates!

## Comparison

| Feature | File:// (Static) | Flask Backend |
|---------|------------------|---------------|
| View dashboard | ✅ | ✅ |
| Upload CSV | Downloads files | **Updates in-place** |
| Manual file copy | ❌ Required | ✅ Automatic |
| Comments persist | Browser only | ✅ Server |
| Team collaboration | ❌ | ✅ Yes |
| Setup time | 0 min | 2 min |

## Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"
```bash
pip install flask pandas werkzeug
```

### Port 5000 already in use
Change port in `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=8080)  # Use 8080 instead
```

### Files not updating
- Check if server is running (should see console output)
- Verify you're accessing via `http://localhost:5000` NOT opening file directly
- Check file permissions

## Summary

**For auto-updating files:**
1. Run `start_server.bat` 
2. Open `http://localhost:5000`
3. Upload CSV → files update automatically! ✨

No more downloads or manual copying!
