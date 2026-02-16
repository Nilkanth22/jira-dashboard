from flask import Flask, request, jsonify, send_from_directory, send_file, session, redirect, url_for, render_template_string
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='.')

# Security: Secret key for session management
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'jira-dashboard-secret-key-change-me')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)

# ─── User Authentication ────────────────────────────────────────────
USERS = {
    "nilkanth": generate_password_hash("centiro2024"),
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            if request.is_json or request.path.endswith('.json'):
                return jsonify({'error': 'Unauthorized'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Login - CENTIRO Jira Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: "Segoe UI", Arial, sans-serif;
            background: linear-gradient(135deg, #1f2d3d 0%, #2c3e50 50%, #1a252f 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 50px 40px;
            width: 400px;
            max-width: 90%;
        }
        .login-header {
            text-align: center;
            margin-bottom: 35px;
        }
        .login-header .icon {
            width: 60px;
            height: 60px;
            background: #1f2d3d;
            border-radius: 14px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 15px;
            font-size: 28px;
        }
        .login-header h1 {
            font-size: 22px;
            color: #1f2d3d;
            font-weight: 700;
        }
        .login-header p {
            font-size: 13px;
            color: #6b7280;
            margin-top: 5px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            font-size: 13px;
            font-weight: 600;
            color: #374151;
            margin-bottom: 6px;
        }
        .form-group input {
            width: 100%;
            padding: 12px 14px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.2s;
            outline: none;
        }
        .form-group input:focus {
            border-color: #4f46e5;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        }
        .login-btn {
            width: 100%;
            padding: 13px;
            background: #1f2d3d;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
            margin-top: 10px;
        }
        .login-btn:hover {
            background: #2c3e50;
        }
        .error-msg {
            background: #fef2f2;
            color: #dc2626;
            padding: 10px 14px;
            border-radius: 8px;
            font-size: 13px;
            margin-bottom: 20px;
            border: 1px solid #fecaca;
            display: {{ 'block' if error else 'none' }};
        }
        .footer {
            text-align: center;
            margin-top: 25px;
            font-size: 11px;
            color: #9ca3af;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <div class="icon">&#x1f4ca;</div>
            <h1>Jira Dashboard</h1>
            <p>Sign in to access the dashboard</p>
        </div>
        <div class="error-msg">{{ error or '' }}</div>
        <form method="POST" action="/login">
            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" placeholder="Enter your username" required autofocus>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" placeholder="Enter your password" required>
            </div>
            <button type="submit" class="login-btn">Sign In</button>
        </form>
        <div class="footer">CENTIRO &middot; Weekly Jira Status Overview</div>
    </div>
</body>
</html>
"""

# Configuration
# Use absolute paths for robust deployment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = BASE_DIR
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# ─── Security Headers ───────────────────────────────────────────────
@app.after_request
def add_security_headers(response):
    # Content Security Policy - controls what resources the browser can load
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'"
    )
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # Clickjacking protection
    response.headers['X-Frame-Options'] = 'DENY'
    # XSS protection (legacy browsers)
    response.headers['X-XSS-Protection'] = '1; mode=block'
    # Strict Transport Security - force HTTPS for 1 year
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    # Referrer Policy - don't leak URLs to other sites
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    # Permissions Policy - disable unnecessary browser features
    response.headers['Permissions-Policy'] = (
        'camera=(), microphone=(), geolocation=(), '
        'payment=(), usb=(), magnetometer=(), gyroscope=(), accelerometer=()'
    )
    # Prevent caching of sensitive data
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response

def get_path(filename):
    """Get absolute path for a file"""
    return os.path.join(BASE_DIR, filename)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def safe(value):
    if pd.isna(value):
        return ""
    return str(value).strip()

def calculate_week_number(date_str):
    """Calculate ISO week number from date string"""
    if not date_str or date_str.strip() == "":
        return ""
    
    try:
        for date_format in ["%d/%b/%y", "%d/%m/%y", "%d-%m-%Y", "%Y-%m-%d"]:
            try:
                date_obj = datetime.strptime(date_str.strip(), date_format)
                week_num = date_obj.isocalendar()[1]
                year = date_obj.year
                return f"W{week_num:02d}-{year}"
            except ValueError:
                continue
        return ""
    except Exception:
        return ""

def load_existing_comments():
    """Load existing comments from cases.json"""
    comments_map = {}
    planned_week_map = {}
    
    try:
        if os.path.exists(get_path("cases.json")):
            with open(get_path("cases.json"), "r", encoding="utf-8") as f:
                existing_cases = json.load(f)
                for case in existing_cases:
                    issue_key = case.get("issue_key", "")
                    if issue_key:
                        if "comments" in case:
                            comments_map[issue_key] = case["comments"]
                        if "planned_for_week" in case:
                            planned_week_map[issue_key] = case["planned_for_week"]
    except Exception as e:
        print(f"Warning: Could not load existing comments: {e}")
    
    return comments_map, planned_week_map

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('index'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')

        if username in USERS and check_password_hash(USERS[username], password):
            session['logged_in'] = True
            session['username'] = username
            session.permanent = True
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password. Please try again.'

    return render_template_string(LOGIN_PAGE, error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return send_file(get_path('index.html'))

@app.route('/dashboard.html')
@login_required
def dashboard():
    return send_file(get_path('index.html'))

@app.route('/cases.json')
@login_required
def cases():
    return send_file(get_path('cases.json'))

@app.route('/data.json')
@login_required
def data():
    return send_file(get_path('data.json'))

@app.route('/upload', methods=['POST'])
@login_required
def upload_csv():
    """Handle CSV upload and process it"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only CSV allowed'}), 400
        
        # Save uploaded CSV
        filename = secure_filename(file.filename)
        filepath = get_path('data.csv')
        file.save(filepath)
        
        # Process the CSV
        comments_map, planned_week_map = load_existing_comments()
        
        df = pd.read_csv(filepath, low_memory=False)
        cases = []
        
        for _, row in df.iterrows():
            issue_key = safe(row["Issue key"])
            target_start = safe(row["Target start date"])
            
            case = {
                "hierarchy": safe(row["Hierarchy"]),
                "issue_key": issue_key,
                "title": safe(row["Title"]),
                "assignee": safe(row["Assignee"]),
                "target_start": target_start,
                "target_end": safe(row["Target end date"]),
                "components": safe(row["Components"]),
                "status": safe(row["Issue status"]).title(),
                "deliverable_type": safe(row["Deliverable Type"])
            }
            
            # Preserve existing comments
            case["comments"] = comments_map.get(issue_key, "")
            
            # Preserve or calculate planned_for_week
            if issue_key in planned_week_map:
                case["planned_for_week"] = planned_week_map[issue_key]
            else:
                case["planned_for_week"] = calculate_week_number(target_start)
            
            cases.append(case)
        
        # Save cases.json
        with open(get_path("cases.json"), "w", encoding="utf-8") as f:
            json.dump(cases, f, indent=4, ensure_ascii=False)
        
        # Save data.json
        status_counts = df["Issue status"].value_counts().to_dict()
        summary = {
            "total_cases": len(cases),
            "status_distribution": {k.title() if isinstance(k, str) else str(k): v for k, v in status_counts.items()}
        }
        
        with open(get_path("data.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=4)
        
        return jsonify({
            'success': True,
            'message': 'CSV processed successfully',
            'total_cases': len(cases),
            'comments_preserved': len(comments_map),
            'weeks_preserved': len(planned_week_map)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update_comment', methods=['POST'])
@login_required
def update_comment():
    """Update a comment for a specific issue"""
    try:
        data = request.json
        issue_key = data.get('issue_key')
        comment = data.get('comment', '')
        
        # Load cases.json
        with open(get_path("cases.json"), "r", encoding="utf-8") as f:
            cases = json.load(f)
        
        # Update the comment
        for case in cases:
            if case.get('issue_key') == issue_key:
                case['comments'] = comment
                break
        
        # Save updated cases.json
        with open(get_path("cases.json"), "w", encoding="utf-8") as f:
            json.dump(cases, f, indent=4, ensure_ascii=False)
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save_all', methods=['POST'])
@login_required
def save_all():
    """Save all cases data at once"""
    try:
        cases = request.json
        if not isinstance(cases, list):
            return jsonify({'error': 'Invalid data format'}), 400

        with open(get_path("cases.json"), "w", encoding="utf-8") as f:
            json.dump(cases, f, indent=4, ensure_ascii=False)

        # Also update data.json summary
        status_counts = {}
        for case in cases:
            status = case.get('status', '')
            if status:
                status_counts[status] = status_counts.get(status, 0) + 1

        summary = {
            "total_cases": len(cases),
            "status_distribution": status_counts
        }

        with open(get_path("data.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=4)

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update_week', methods=['POST'])
@login_required
def update_week():
    """Update planned week for a specific issue"""
    try:
        data = request.json
        issue_key = data.get('issue_key')
        week = data.get('week', '')
        
        # Load cases.json
        with open(get_path("cases.json"), "r", encoding="utf-8") as f:
            cases = json.load(f)
        
        # Update the week
        for case in cases:
            if case.get('issue_key') == issue_key:
                case['planned_for_week'] = week
                break
        
        # Save updated cases.json
        with open(get_path("cases.json"), "w", encoding="utf-8") as f:
            json.dump(cases, f, indent=4, ensure_ascii=False)
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Debug mode only when running locally, not in production
    debug_mode = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    app.run(debug=debug_mode)
