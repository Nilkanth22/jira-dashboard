# Collaborative Dashboard Deployment to PythonAnywhere

## Problem Solved
With Flask backend, when **anyone** uploads a new CSV file through the dashboard, it automatically:
- ✅ Updates the JSON files on the server
- ✅ Everyone sees the latest data immediately after refresh
- ✅ Comments and planned weeks are preserved
- ✅ No manual file copying needed

## Quick Setup Steps

### 1. Create PythonAnywhere Account
- Go to [pythonanywhere.com](https://www.pythonanywhere.com/registration/register/beginner/)
- Sign up for **free account**

### 2. Upload Your Files
Click **Files** tab, navigate to `/home/yourusername/`, upload:
- `app.py` ← **New Flask backend**
- `dashboard.html`
- `cases.json`
- `data.json`
- `data.csv`
- `requirements.txt`

### 3. Install Dependencies
Click **Consoles** → Start new **Bash console**:
```bash
cd ~/
pip install --user pandas flask werkzeug
```

### 4. Configure Web App
Click **Web** tab → **Add new web app**:
1. Choose **Flask**
2. Select **Python 3.10**
3. Set path to `/home/yourusername/app.py`
4. Click **Next**

### 5. Set WSGI File
In **Web** tab, click on **WSGI configuration file**, replace content with:
```python
import sys
path = '/home/yourusername'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

Replace `yourusername` with your actual username.

### 6. Reload & Test
- Click green **Reload** button
- Visit `https://yourusername.pythonanywhere.com`
- Test CSV upload!

## How It Works

### Collaborative Upload Flow
1. **User A** uploads new `data.csv` via dashboard
2. Flask backend (`app.py`) receives the file
3. Server processes CSV, preserves comments/weeks
4. Updates `cases.json` and `data.json` on server
5. **User B** refreshes their browser → sees latest data!

### API Endpoints
- `GET /` → Serves dashboard.html
- `GET /cases.json` → Returns case data
- `GET /data.json` → Returns summary
- `POST /upload` → Processes CSV upload
- `POST /update_comment` → Updates single comment
- `POST /update_week` → Updates planned week

### Smart Client Detection
The dashboard automatically detects if it's running:
- **On server** (http://...) → Uses backend API
- **Locally** (file://...) → Uses client-side processing

## Testing Collaboratively

### Scenario: Multiple Team Members
1. **Team Member 1** visits dashboard, adds comments
2. **Team Member 2** visits same URL, sees those comments
3. **Team Member 3** uploads new CSV with updated statuses
4. Everyone refreshes → sees new statuses + preserved comments!

### Real-Time Comments (Bonus Feature)
The dashboard now saves comments to the server:
- Type a comment → automatically saved to server
- Anyone else viewing sees it after refresh
- Survives CSV uploads

## Security & Access Control

### Option 1: Password Protection (Manual)
Add to `app.py` before route definitions:
```python
from functools import wraps
from flask import request, Response

def check_auth(username, password):
    return username == 'admin' and password == 'your_password'

def authenticate():
    return Response('Login required', 401, 
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Then add @requires_auth to routes:
@app.route('/')
@requires_auth
def index():
    return send_file('dashboard.html')
```

### Option 2: Share Account Access
- Give team members your PythonAnywhere login
- They can upload files directly via Files tab

### Option 3: IP Whitelist (Paid plans)
- Restrict access to company IP range

## Troubleshooting

### "No module named 'flask'"
```bash
pip install --user flask pandas werkzeug
```

### "Internal Server Error"
- Check **Error log** in Web tab
- Verify `app.py` path is correct in WSGI config
- Ensure all files uploaded

### CSV upload returns error
- Check file permissions: `chmod 644 data.csv`
- Verify pandas is installed
- Check Error log for details

### Changes not visible
- Hard refresh: `Ctrl + F5` or `Cmd + Shift + R`
- Check if JSON files updated in Files tab
- Clear browser cache

## Free Tier Limitations

⚠️ **CPU Seconds**: 100 seconds/day
- Each CSV upload uses ~2-5 seconds
- ~20-50 uploads per day max
- Viewing dashboard doesn't count

💡 **Workaround**: Upgrade to $5/month for unlimited CPU

## Alternative: Upgrade Features

With PythonAnywhere paid plan ($5/mo):
- Unlimited CPU seconds
- Always-on scheduled tasks
- Custom domain support
- Better performance

## Comparison

| Feature | Static (Free) | Flask Backend (Free) | Notes |
|---------|---------------|---------------------|-------|
| View dashboard | ✅ | ✅ | Both work |
| Upload CSV | Browser only | Server-side | Backend better |
| Collaborative | ❌ Manual sync | ✅ Automatic | Big difference! |
| Real-time updates | ❌ | ✅ | Refresh to see |
| Comments persist | ❌ localStorage | ✅ Server | Backend better |
| CPU usage | None | ~2-5s per upload | Free tier: 100s/day |

## Summary

**With Flask backend (recommended for teams):**
✅ Anyone can upload CSV → everyone sees updates  
✅ Comments saved to server, not just browser  
✅ Planned weeks persist across uploads  
✅ Real collaborative dashboard  

**Cost:** FREE on PythonAnywhere (within 100 CPU seconds/day)

**Setup time:** 10 minutes
