from flask import Flask, request, jsonify, send_from_directory, send_file
import pandas as pd
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='.')

# Security: Secret key for session management
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32).hex())

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

@app.route('/')
def index():
    return send_file(get_path('index.html'))

@app.route('/dashboard.html')
def dashboard():
    return send_file(get_path('index.html'))

@app.route('/cases.json')
def cases():
    return send_file(get_path('cases.json'))

@app.route('/data.json')
def data():
    return send_file(get_path('data.json'))

@app.route('/upload', methods=['POST'])
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
