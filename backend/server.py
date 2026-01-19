import os
import mimetypes
from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
from flask_cors import CORS
from functools import wraps  # Import for security decorator

# --- FIX MIME TYPES ---
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

# --- Import Features ---
from features.sku_printing import process_order_file
from features.blog_wrapper import start_blog_automation
from features.keyword_gen.ai_keywords import get_hybrid_keywords
from features.blog_posting.core.generate_blog import search_trending_topics
from features.amazon_details import get_product_details

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# --- Config ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
IMAGE_FOLDER_ABSOLUTE = os.path.join(BASE_DIR, 'static', 'labels')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🔐 SECURITY SYSTEM START (Multi-User Safe Mode)
USERS = {
    "admin": {
        "password": os.getenv("PASS_ADMIN", "AdminTemp123"), # Fallback only for local testing
        "role": "super_admin", 
        "name": "Super Admin"
    },
    "victor": {
        "password": os.getenv("PASS_VICTOR", "VicTemp123"), 
        "role": "user",        
        "name": "Victor"
    },
    "stephy": {
        "password": os.getenv("PASS_STEPHY", "StephTemp123"), 
        "role": "user",        
        "name": "Stephy"
    },
    "kishore": {
        "password": os.getenv("PASS_KISHORE", "KishTemp123"), 
        "role": "user",        
        "name": "Kishore"
    },
    "sanjana": {
        "password": os.getenv("PASS_SANJANA", "SanTemp123"), 
        "role": "user",        
        "name": "Sanjana"
    }
}

# 2. Authentication Decorator
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Allow OPTIONS requests
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)
            
        # Get token from headers
        token = request.headers.get('X-Access-Token')
        
        # Check if token matches ANY active user password
        # (For this simple system, the password acts as the access token)
        is_valid = False
        for user_key, user_data in USERS.items():
            if user_data['password'] == token:
                is_valid = True
                break
                
        if not token or not is_valid:
            return jsonify({"error": "⛔ Unauthorized: Please Login Again"}), 401
            
        return f(*args, **kwargs)
    return decorated_function

# 3. Login Route (Now checks Username AND Password)
@app.route('/api/verify-login', methods=['POST'])
def verify_login():
    data = request.json
    username = data.get('username', '').lower().strip() # Normalize to lowercase
    password = data.get('password', '').strip()
    
    # Check if user exists and password matches
    if username in USERS and USERS[username]['password'] == password:
        user_info = USERS[username]
        return jsonify({
            "success": True, 
            "message": f"Welcome, {user_info['name']}!",
            "token": user_info['password'], # We use the password as the session token for now
            "role": user_info['role'],
            "name": user_info['name']
        })
        
    return jsonify({"success": False, "message": "Invalid Username or Password"}), 401

# ---------------------------------------------------------
# 🔐 SECURITY SYSTEM END
# ---------------------------------------------------------


# --- ROUTE 1: SKU PRINTING (Protected) ---
@app.route('/print-sku', methods=['POST']) 
@app.route('/upload', methods=['POST'])
@require_auth  # <--- LOCKED
def sku_route():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    
    import time
    unique_filename = f"{int(time.time())}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(filepath)
    
    result = process_order_file(filepath, IMAGE_FOLDER_ABSOLUTE)
    return jsonify(result)

# --- NEW ROUTE: FETCH AMAZON DETAILS (Protected) ---
@app.route('/api/amazon-details', methods=['POST'])
@require_auth  # <--- LOCKED
def get_amazon_details():
    data = request.json
    url = data.get('url')
    if not url: return jsonify({"error": "No URL provided"}), 400
    
    result = get_product_details(url)
    return jsonify(result)

# --- UPDATED ROUTE: BLOG AUTOMATION (Protected) ---
@app.route('/publish-blog', methods=['POST'])
@require_auth  # <--- LOCKED
def blog_route():
    data = request.json
    title = data.get('title')
    desc = data.get('desc')
    platforms = data.get('platforms', [])
    product_image = data.get('product_image') 
    product_link = data.get('product_link')
    brand = data.get('brand', 'SEVENXT')

    result = start_blog_automation(title, desc, platforms, product_image, product_link, brand)
    return jsonify(result)

@app.route('/api/trending/<category>', methods=['GET'])
@require_auth  # <--- LOCKED
def trending_route(category):
    try:
        topics = search_trending_topics(category)
        return jsonify({"success": True, "topics": topics})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# --- ROUTE 4: HYBRID KEYWORD GEN (Fixed for Cloud Downloads) ---
@app.route('/generate-seo-links', methods=['POST'])
@require_auth
def generate_seo_links_route():
    data = request.json
    product = data.get('product')
    asin = data.get('asin')
    specs = data.get('specs')
    
    if not product or not asin or not specs:
        return jsonify({"error": "Name, ASIN, and Specs are required"}), 400
    
    # 1. Run the Logic
    result_obj = get_hybrid_keywords(product, asin, specs)
    
    if not result_obj or "data" not in result_obj:
        return jsonify({"error": "Failed to generate strategies"}), 500

    # ---------------------------------------------------------
    # 🛠️ URL FIX: REWRITE LOCALHOST TO CLOUD URL
    # ---------------------------------------------------------
    from flask import url_for
    
    # 1. Extract just the filename (e.g., "report_123.xlsx")
    # This strips away "C:/Users/..." or "http://localhost..."
    raw_url = result_obj.get("file_url", "")
    filename = os.path.basename(raw_url)
    
    # 2. Generate the correct URL for WHOEVER is hosting this app (Render or Local)
    # 'download_file' is the name of the function handling /download/<filename>
    # _external=True creates a full absolute URL (http://...)
    final_url = url_for('download_file', filename=filename, _external=True)
    
    # 3. Force HTTPS if running on Render (Cloud uses Proxy, Flask sees HTTP by default)
    if request.headers.get('X-Forwarded-Proto') == 'https':
        final_url = final_url.replace('http://', 'https://')

    return jsonify({
        "success": True, 
        "data": result_obj["data"], 
        "download_url": final_url  # <--- Sending the corrected URL
    })

# --- DOWNLOAD ROUTE (Public - Needed for browser download) ---
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # This remains public so the browser can download the file after generation
    print(f"📥 [Download Request] Looking for: {filename}")
    try:
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    except Exception as e:
        print(f"❌ Download Error: {e}")
        return jsonify({"error": "File not found"}), 404

# --- ROUTE 5: SERVE REACT FRONTEND (Public) ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')

@app.route('/assets/<path:path>')
def proxy_assets(path):
    return send_from_directory('static/assets', path)

if __name__ == '__main__':
    print("Server running on Port 5000")
    app.run(debug=True, port=5000)