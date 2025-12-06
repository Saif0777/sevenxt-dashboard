import os
import mimetypes
from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
from flask_cors import CORS

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

# --- ROUTE 1: SKU PRINTING ---
@app.route('/print-sku', methods=['POST']) 
@app.route('/upload', methods=['POST'])    
def sku_route():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    
    # Save with unique name to avoid "File Open" errors
    import time
    unique_filename = f"{int(time.time())}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(filepath)
    
    # Pass the image folder location to the logic
    result = process_order_file(filepath, IMAGE_FOLDER_ABSOLUTE)
    return jsonify(result)

# --- NEW ROUTE: FETCH AMAZON DETAILS ---
@app.route('/api/amazon-details', methods=['POST'])
def get_amazon_details():
    data = request.json
    url = data.get('url')
    if not url: return jsonify({"error": "No URL provided"}), 400
    
    result = get_product_details(url)
    return jsonify(result)

# --- UPDATED ROUTE: BLOG AUTOMATION ---
@app.route('/publish-blog', methods=['POST'])
def blog_route():
    data = request.json
    title = data.get('title')
    desc = data.get('desc')
    platforms = data.get('platforms', [])
    
    # NEW: Accept the Amazon Image URL from frontend
    product_image = data.get('product_image') 
    product_link = data.get('product_link')
    brand = data.get('brand', 'SEVENXT')

    # Pass these to the wrapper
    result = start_blog_automation(title, desc, platforms, product_image, product_link, brand)
    return jsonify(result)

@app.route('/api/trending/<category>', methods=['GET'])
def trending_route(category):
    try:
        topics = search_trending_topics(category)
        return jsonify({"success": True, "topics": topics})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# --- NEW HYBRID ROUTE ---
@app.route('/generate-seo-links', methods=['POST'])
def generate_seo_links_route():
    data = request.json
    product = data.get('product')
    asin = data.get('asin')
    
    if not product or not asin:
        return jsonify({"error": "Product Name and ASIN are required"}), 400
        
    print(f"🚀 [Hybrid Engine] Analyzing: {product} ({asin})")
    
    # Call the Hybrid Logic
    results = get_hybrid_keywords(product, asin)
    
    if not results:
        return jsonify({"error": "Failed to generate strategies"}), 500
        
    return jsonify({"success": True, "data": results})


# --- ROUTE 4: IMAGE AUTOMATION (PLACEHOLDER) ---
@app.route('/image-generator/create', methods=['POST'])
def image_route():
    # We return a dummy success so the frontend doesn't crash
    return jsonify({"status": "coming_soon", "message": "Module disabled for production"})

# --- ROUTE 5: SERVE REACT FRONTEND ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')

# --- ROUTE 6: FIX ASSET PATHS ---
@app.route('/assets/<path:path>')
def proxy_assets(path):
    return send_from_directory('static/assets', path)

if __name__ == '__main__':
    print("Server running on Port 5000")
    app.run(debug=True, port=5000)