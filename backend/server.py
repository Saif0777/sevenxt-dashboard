import os
from flask import Flask, request, jsonify, send_file # <--- FIXED: Added send_file here
from flask_cors import CORS

# --- Import Features ---
from features.sku_printing import process_order_file
from features.blog_wrapper import start_blog_automation
from features.keyword_wrapper import process_keyword_file
from features.blog_posting.core.generate_blog import search_trending_topics

app = Flask(__name__)
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
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    
    # Pass the image folder location to the logic
    result = process_order_file(filepath, IMAGE_FOLDER_ABSOLUTE)
    return jsonify(result)

# --- ROUTE 2: BLOG AUTOMATION ---
@app.route('/publish-blog', methods=['POST'])
def blog_route():
    data = request.json
    title = data.get('title')
    desc = data.get('desc')
    platforms = data.get('platforms', [])
    
    # Call the wrapper
    result = start_blog_automation(title, desc, platforms)
    return jsonify(result)

@app.route('/api/trending/<category>', methods=['GET'])
def trending_route(category):
    try:
        topics = search_trending_topics(category)
        return jsonify({"success": True, "topics": topics})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# --- ROUTE 3: KEYWORD GEN ---
@app.route('/generate-keywords', methods=['POST'])
def keyword_route():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    
    # Call the wrapper
    output_path = process_keyword_file(filepath)
    
    # This line failed before because send_file wasn't imported
    if output_path and os.path.exists(output_path):
        return send_file(output_path, as_attachment=True)
    else:
        return jsonify({"error": "Processing failed"}), 500

# --- ROUTE 4: IMAGE AUTOMATION (Placeholder) ---
@app.route('/image-automation', methods=['POST'])
def image_route():
    return jsonify({"status": "Image Automation Logic Coming Soon"})

if __name__ == '__main__':
    print("Server running on Port 5000")
    app.run(debug=True, port=5000)