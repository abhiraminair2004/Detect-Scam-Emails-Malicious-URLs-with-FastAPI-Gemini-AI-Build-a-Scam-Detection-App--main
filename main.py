from flask import Flask, render_template, request, jsonify, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import google.generativeai as genai
import os
import PyPDF2
import redis
from celery import Celery
import uuid
import time
from datetime import datetime
from functools import wraps
import hashlib
import secrets
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# Enable CORS for API endpoints
CORS(app, origins=["*"])

# Initialize Redis for rate limiting and task queue
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["1000 per hour", "100 per minute"]
)

# Initialize Celery for async tasks
celery = Celery('threatguard', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

# Set up the Google API Key
os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY", "your_api_key_here")
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")

# In-memory storage for task results (in production, use Redis or database)
task_results = {}

# API Key management (in production, use proper database)
api_keys = {
    "demo-key-123": {"name": "Demo User", "rate_limit": "100/hour"},
    "admin-key-456": {"name": "Admin User", "rate_limit": "1000/hour"}
}

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        if not api_key or api_key not in api_keys:
            return jsonify({'error': 'Valid API key required'}), 401
        g.current_api_key = api_key
        return f(*args, **kwargs)
    return decorated_function

def generate_api_key():
    """Generate a new API key"""
    return secrets.token_urlsafe(32)

# Celery task for async URL scanning
@celery.task
def scan_url_async(url, task_id):
    """Asynchronous URL scanning task"""
    try:
        # Simulate processing time for demonstration
        time.sleep(2)
        
        # Perform actual URL analysis
        classification = url_detection(url)
        
        # Store result
        task_results[task_id] = {
            'status': 'completed',
            'result': classification,
            'url': url,
            'completed_at': datetime.now().isoformat()
        }
        
        return classification
    except Exception as e:
        task_results[task_id] = {
            'status': 'failed',
            'error': str(e),
            'url': url,
            'failed_at': datetime.now().isoformat()
        }
        return None

# functions
def predict_fake_or_real_email_content(text):
    prompt = f"""
    You are an expert in identifying scam messages in text, email etc. Analyze the given text and classify it as:

    - **Real/Legitimate** (Authentic, safe message)
    - **Scam/Fake** (Phishing, fraud, or suspicious message)

    **for the following Text:**
    {text}

    **Return a clear message indicating whether this content is real or a scam. 
    If it is a scam, mention why it seems fraudulent. If it is real, state that it is legitimate.**

    **Only return the classification message and nothing else.**
    Note: Don't return empty or null, you only need to return message for the input text
    """

    response = model.generate_content(prompt)
    return response.text.strip() if response else "Classification failed."


def url_detection(url):
    prompt = f"""
    You are an advanced AI model specializing in URL security classification. Analyze the given URL and classify it as one of the following categories:

    1. Benign**: Safe, trusted, and non-malicious websites such as google.com, wikipedia.org, amazon.com.
    2. Phishing**: Fraudulent websites designed to steal personal information. Indicators include misspelled domains (e.g., paypa1.com instead of paypal.com), unusual subdomains, and misleading content.
    3. Malware**: URLs that distribute viruses, ransomware, or malicious software. Often includes automatic downloads or redirects to infected pages.
    4. Defacement**: Hacked or defaced websites that display unauthorized content, usually altered by attackers.

    **Example URLs and Classifications:**
    - **Benign**: "https://www.microsoft.com/"
    - **Phishing**: "http://secure-login.paypa1.com/"
    - **Malware**: "http://free-download-software.xyz/"
    - **Defacement**: "http://hacked-website.com/"

    **Input URL:** {url}

    **Output Format:**  
    - Return only a string class name
    - Example output for a phishing site:  

    Analyze the URL and return the correct classification (Only name in lowercase such as benign etc.
    Note: Don't return empty or null, at any cost return the corrected class
    """

    response = model.generate_content(prompt)
    return response.text if response else "Detection failed."


# Routes

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/api/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/generate-key', methods=['POST'])
def generate_new_api_key():
    """Generate a new API key (for demo purposes)"""
    new_key = generate_api_key()
    api_keys[new_key] = {"name": "Generated User", "rate_limit": "100/hour"}
    return jsonify({
        'api_key': new_key,
        'message': 'API key generated successfully'
    })

@app.route('/scam/', methods=['POST'])
@limiter.limit("10 per minute")
def detect_scam():
    if 'file' not in request.files:
        return render_template("index.html", message="No file uploaded.")

    file = request.files['file']
    extracted_text = ""

    if file.filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(file)
        extracted_text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    elif file.filename.endswith('.txt'):
        extracted_text = file.read().decode("utf-8")
    else:
        return render_template("index.html", message="Invalid file type. Please upload a PDF or TXT file.")

    if not extracted_text.strip():
        return render_template("index.html", message="File is empty or text could not be extracted.")

    message = predict_fake_or_real_email_content(extracted_text)
    return render_template("index.html", message=message)

@app.route('/predict', methods=['POST'])
@limiter.limit("20 per minute")
def predict_url():
    url = request.form.get('url', '').strip()

    if not url.startswith(("http://", "https://")):
        return render_template("index.html", message="Invalid URL format.", input_url=url)

    classification = url_detection(url)
    return render_template("index.html", input_url=url, predicted_class=classification)

# API Endpoints with Authentication and Rate Limiting

@app.route('/api/v1/scan-url', methods=['POST'])
@require_api_key
@limiter.limit("50 per minute")
def api_scan_url():
    """API endpoint for URL scanning with authentication"""
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    url = data['url'].strip()
    if not url.startswith(("http://", "https://")):
        return jsonify({'error': 'Invalid URL format'}), 400
    
    # Generate task ID for async processing
    task_id = str(uuid.uuid4())
    
    # Start async task
    scan_url_async.delay(url, task_id)
    
    return jsonify({
        'task_id': task_id,
        'status': 'processing',
        'message': 'URL scan started. Use task_id to check results.',
        'check_url': f'/api/v1/task/{task_id}'
    })

@app.route('/api/v1/task/<task_id>')
@require_api_key
def get_task_result(task_id):
    """Get the result of an async task"""
    if task_id not in task_results:
        return jsonify({'error': 'Task not found'}), 404
    
    result = task_results[task_id]
    return jsonify(result)

@app.route('/api/v1/scan-content', methods=['POST'])
@require_api_key
@limiter.limit("30 per minute")
def api_scan_content():
    """API endpoint for content scanning with authentication"""
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'Content is required'}), 400
    
    content = data['content']
    if len(content) > 10000:  # Limit content size
        return jsonify({'error': 'Content too long (max 10000 characters)'}), 400
    
    try:
        result = predict_fake_or_real_email_content(content)
        return jsonify({
            'status': 'completed',
            'result': result,
            'content_length': len(content),
            'scanned_at': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/v1/stats')
@require_api_key
def get_api_stats():
    """Get API usage statistics"""
    return jsonify({
        'total_tasks': len(task_results),
        'completed_tasks': len([r for r in task_results.values() if r['status'] == 'completed']),
        'failed_tasks': len([r for r in task_results.values() if r['status'] == 'failed']),
        'active_api_keys': len(api_keys),
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    app.run(debug=True)
