from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>ScanWitch - Advanced Threat Detection Platform</h1><p>🚀 Application is running successfully!</p><p>Visit <a href='/api/health'>/api/health</a> for health check</p>"

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'ScanWitch API is running',
        'features': ['API Security', 'Rate Limiting', 'AI Detection', 'File Analysis'],
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("🚀 Starting ScanWitch - Advanced Threat Detection Platform")
    print("🌐 Web Interface: http://localhost:5000")
    print("🔍 Health Check: http://localhost:5000/api/health")
    app.run(debug=True, host='0.0.0.0', port=5000)

