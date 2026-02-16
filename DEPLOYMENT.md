# Deploying to PythonAnywhere (Free Tier)

## Prerequisites
- A free PythonAnywhere account: [https://www.pythonanywhere.com/](https://www.pythonanywhere.com/)
- Your dashboard files ready to upload

## Deployment Steps

### 1. Create PythonAnywhere Account
1. Go to [https://www.pythonanywhere.com/registration/register/beginner/](https://www.pythonanywhere.com/registration/register/beginner/)
2. Sign up for a **free Beginner account**
3. Verify your email and log in

### 2. Upload Your Files
You have two options:

#### Option A: Upload via Web Interface (Easier)
1. Click on **"Files"** tab in the dashboard
2. Navigate to `/home/yourusername/` (or create a folder like `/home/yourusername/jira-dashboard`)
3. Click **"Upload a file"** button
4. Upload these files:
   - `dashboard.html`
   - `cases.json`
   - `data.json`
   - `data.csv` (optional, for updates)

#### Option B: Upload via Git (Recommended for updates)
1. Click on **"Consoles"** tab
2. Start a new **Bash console**
3. Run these commands:
```bash
cd ~
git clone https://github.com/yourusername/jira-dashboard.git
# OR upload your files using wget/curl
```

### 3. Set Up Web App
1. Click on the **"Web"** tab
2. Click **"Add a new web app"**
3. Choose **"Manual configuration"** (not a framework)
4. Select **Python 3.10** (or latest available)
5. Click through the setup

### 4. Configure Static Files
1. In the **Web** tab, scroll to the **"Static files"** section
2. Add a new static file mapping:
   - **URL**: `/`
   - **Directory**: `/home/yourusername/jira-dashboard/`

3. Add another mapping for explicit files (optional):
   - **URL**: `/static/`
   - **Directory**: `/home/yourusername/jira-dashboard/`

### 5. Set Index File
Since your main file is `dashboard.html`, you need to make it the default page:

**Option 1: Rename dashboard.html to index.html**
```bash
# In Bash console:
cd ~/jira-dashboard
mv dashboard.html index.html
```

**Option 2: Configure WSGI to serve dashboard.html**
1. Click **"Web"** tab → Click on your WSGI configuration file
2. Replace the content with:

```python
import os
from pathlib import Path

def application(environ, start_response):
    # Serve dashboard.html as the default page
    path = Path('/home/yourusername/jira-dashboard/dashboard.html')
    
    if path.exists():
        with open(path, 'rb') as f:
            content = f.read()
        
        status = '200 OK'
        headers = [('Content-Type', 'text/html; charset=utf-8')]
        start_response(status, headers)
        return [content]
    else:
        status = '404 NOT FOUND'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        return [b'File not found']
```

Replace `yourusername` with your actual PythonAnywhere username.

### 6. Reload Web App
1. Go to the **Web** tab
2. Click the green **"Reload"** button
3. Your site will be available at: `https://yourusername.pythonanywhere.com`

## Updating Your Dashboard

### Method 1: Manual File Upload
1. Go to **Files** tab
2. Navigate to your dashboard folder
3. Click on `data.csv` → **Delete** → Upload new version
4. Run `update_data.py` in a Bash console:
```bash
cd ~/jira-dashboard
python update_data.py
```

### Method 2: Use the Upload Feature
1. Visit your live dashboard
2. Hover over the title to reveal **📤 Upload CSV**
3. Upload your new `data.csv`
4. Download the generated `cases.json` and `data.json`
5. Upload these to PythonAnywhere via **Files** tab

### Method 3: Automated Script (Advanced)
Create a bash script `refresh_dashboard.sh`:

```bash
#!/bin/bash
cd ~/jira-dashboard
python update_data.py
echo "Dashboard updated at $(date)"
```

Make it executable and run:
```bash
chmod +x refresh_dashboard.sh
./refresh_dashboard.sh
```

## Important Notes for Free Tier

### Limitations
- **CPU seconds**: Limited to 100 seconds/day
- **Disk space**: 512 MB
- **Always-on tasks**: Not available (site may sleep)
- **Custom domain**: Not available (use `yourusername.pythonanywhere.com`)

### Workarounds
- Since your dashboard is **100% client-side**, you won't hit CPU limits
- The CSV upload feature works entirely in the browser
- No server processing needed for viewing the dashboard

## Security Considerations

### Making Dashboard Private
If you want to restrict access:

1. Add password protection to your WSGI file:

```python
def application(environ, start_response):
    # Simple password protection
    auth = environ.get('HTTP_AUTHORIZATION', '')
    
    if auth != 'Basic dXNlcjpwYXNzd29yZA==':  # user:password in base64
        status = '401 Unauthorized'
        headers = [
            ('Content-Type', 'text/html'),
            ('WWW-Authenticate', 'Basic realm="Login Required"')
        ]
        start_response(status, headers)
        return [b'Authentication required']
    
    # Serve dashboard.html
    # ... rest of code
```

2. Or use PythonAnywhere's **password protection** feature (Paid plans only)

## Alternative: GitHub Pages (100% Free, No Limits)

If you don't need server-side processing, consider GitHub Pages:

1. Create a GitHub repository
2. Upload your files (rename `dashboard.html` to `index.html`)
3. Go to Settings → Pages
4. Select main branch → Save
5. Your site: `https://yourusername.github.io/jira-dashboard/`

**Pros**: Unlimited bandwidth, no sleeping, faster
**Cons**: Public repository (unless you have GitHub Pro)

## Troubleshooting

### Dashboard doesn't load
- Check the WSGI file path matches your username
- Ensure all JSON files are uploaded
- Check error logs in **Web** tab → **Error log**

### JSON files not loading
- Verify files are in the correct directory
- Check file permissions: `chmod 644 *.json`
- Add CORS headers if needed (usually not required)

### Upload CSV feature not working
- This feature works client-side, so server doesn't matter
- Ensure JavaScript is enabled in browser
- Check browser console for errors (F12)

## Support
- PythonAnywhere Forums: [https://www.pythonanywhere.com/forums/](https://www.pythonanywhere.com/forums/)
- Help docs: [https://help.pythonanywhere.com/](https://help.pythonanywhere.com/)
