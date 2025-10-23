# ScanWitch - Advanced Threat Detection Platform

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue.svg)
![Redis](https://img.shields.io/badge/Redis-Caching-red.svg)
![Celery](https://img.shields.io/badge/Celery-Async%20Tasks-green.svg)

A comprehensive security platform for detecting malicious URLs and scam content using AI/ML, built with enterprise-grade features including API security, rate limiting, asynchronous processing, and containerization.

## 🚀 Key Features

### 🔐 API Security & Authentication
- **Token-based Authentication**: Secure API endpoints with API key validation
- **Rate Limiting**: Configurable rate limits using Flask-Limiter (1000/hour, 100/minute)
- **Input Validation**: Comprehensive validation for URLs and content
- **CORS Support**: Cross-origin resource sharing for web applications

### ⚡ Asynchronous Processing
- **Celery Task Queue**: High-performance async URL scanning with Redis backend
- **Non-blocking Operations**: Immediate response with task tracking
- **Scalable Architecture**: Handle high concurrency for enterprise workloads
- **Task Monitoring**: Real-time task status and result retrieval

### 🐳 DevOps & Deployment
- **Docker Containerization**: Multi-stage Dockerfile for optimized production builds
- **Docker Compose**: Complete stack deployment with Redis and Celery workers
- **Health Checks**: Built-in health monitoring endpoints
- **Production Ready**: Gunicorn WSGI server with worker processes

### 🤖 AI-Powered Detection
- **Google Gemini AI**: Advanced content analysis for scam detection
- **URL Classification**: Multi-category threat classification (benign, phishing, malware, defacement)
- **Content Analysis**: PDF and text file processing for threat detection
- **Confidence Scoring**: AI confidence levels for detection results

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Client    │    │   API Client    │    │   Mobile App    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │     Flask Application     │
                    │   (Rate Limiting + Auth)  │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │      Redis Cache         │
                    │  (Rate Limiting + Queue) │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │    Celery Workers        │
                    │   (Async Processing)     │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │    Google Gemini AI      │
                    │   (Threat Detection)     │
                    └───────────────────────────┘
```

## 🛠️ Technology Stack

- **Backend**: Flask 2.3.3, Python 3.11+
- **AI/ML**: Google Gemini AI, PyPDF2
- **Database**: Redis (caching, rate limiting, task queue)
- **Task Queue**: Celery with Redis broker
- **Security**: Flask-Limiter, API key authentication
- **Deployment**: Local development server
- **Monitoring**: Health checks, API statistics

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Google AI API key

### 1. Clone and Setup
```bash
git clone <repository-url>
cd threatguard
```

### 2. Environment Configuration
```bash
# Create .env file
echo "GOOGLE_API_KEY=your_google_api_key_here" > .env
echo "SECRET_KEY=your_secret_key_here" >> .env
```

### 3. Run the Application
```bash
# Install dependencies
pip install -r requirements.txt

# Run the simplified version (recommended)
python main_simple.py

# OR run the full version with Redis (optional)
# redis-server
# celery -A main.celery worker --loglevel=info
# python main.py
```

## 📚 API Documentation

### Authentication
All API endpoints require an API key in the header:
```bash
curl -H "X-API-Key: demo-key-123" http://localhost:5000/api/v1/stats
```

### Core Endpoints

#### 1. Health Check
```bash
GET /api/health
```

#### 2. Generate API Key
```bash
POST /api/generate-key
```

#### 3. Async URL Scanning
```bash
POST /api/v1/scan-url
Content-Type: application/json

{
    "url": "https://example.com"
}

# Response
{
    "task_id": "uuid-here",
    "status": "processing",
    "check_url": "/api/v1/task/uuid-here"
}
```

#### 4. Get Task Result
```bash
GET /api/v1/task/{task_id}
```

#### 5. Content Analysis
```bash
POST /api/v1/scan-content
Content-Type: application/json

{
    "content": "Your text content here"
}
```

#### 6. API Statistics
```bash
GET /api/v1/stats
```

## 🔧 Configuration

### Rate Limiting
- Default: 1000 requests/hour, 100 requests/minute
- Per-endpoint limits: Configurable in code
- Redis-backed: Persistent across restarts

### Security Features
- API key authentication
- Input validation and sanitization
- CORS configuration
- Request size limits
- Error handling and logging

## 📊 Monitoring & Observability

### Health Endpoints
- `/api/health` - Application health status
- `/api/v1/stats` - API usage statistics

### Logging
- Structured logging with timestamps
- Error tracking and monitoring
- Request/response logging

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=main

# Run specific test file
pytest tests/test_api.py
```

## 🚀 Production Deployment

### Environment Variables
```bash
GOOGLE_API_KEY=your_api_key
SECRET_KEY=your_secret_key
FLASK_ENV=production
```

### Running in Production
```bash
# For production, use a WSGI server like Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main_simple:app
```

## 📈 Performance Features

- **Async Processing**: Non-blocking URL analysis
- **Redis Caching**: Fast response times
- **Rate Limiting**: Protection against abuse
- **Horizontal Scaling**: Multiple Celery workers
- **Health Monitoring**: Proactive issue detection

## 🔒 Security Features

- **API Authentication**: Token-based security
- **Input Validation**: XSS and injection protection
- **Rate Limiting**: DDoS protection
- **CORS Configuration**: Secure cross-origin requests
- **Error Handling**: Secure error responses

## 📝 Resume Keywords

This project demonstrates expertise in:
- **API Security** & Rate Limiting
- **Asynchronous Processing** & Task Queues
- **Docker Containerization** & DevOps
- **AI/ML Integration** & Threat Detection
- **High Concurrency Design** & Scalability
- **Redis Caching** & Performance Optimization
- **Flask Framework** & Python Development
- **Enterprise Architecture** & Production Deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation
- Review the health endpoints

---

**Built with ❤️ for enterprise security applications**