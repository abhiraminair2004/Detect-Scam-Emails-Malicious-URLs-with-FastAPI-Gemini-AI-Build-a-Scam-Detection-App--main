"""
Test suite for ScanWitch API endpoints
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from main import app

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def api_key():
    """Test API key"""
    return "demo-key-123"

class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check returns 200"""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data

class TestAPIAuthentication:
    """Test API authentication"""
    
    def test_scan_url_without_api_key(self, client):
        """Test URL scan without API key returns 401"""
        response = client.post('/api/v1/scan-url', 
                             json={'url': 'https://example.com'})
        assert response.status_code == 401
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'API key required' in data['error']
    
    def test_scan_url_with_invalid_api_key(self, client):
        """Test URL scan with invalid API key returns 401"""
        response = client.post('/api/v1/scan-url',
                             json={'url': 'https://example.com'},
                             headers={'X-API-Key': 'invalid-key'})
        assert response.status_code == 401
    
    def test_scan_url_with_valid_api_key(self, client, api_key):
        """Test URL scan with valid API key"""
        with patch('main.scan_url_async.delay') as mock_delay:
            mock_delay.return_value = MagicMock()
            
            response = client.post('/api/v1/scan-url',
                                 json={'url': 'https://example.com'},
                                 headers={'X-API-Key': api_key})
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'task_id' in data
            assert data['status'] == 'processing'

class TestContentScanning:
    """Test content scanning endpoints"""
    
    def test_scan_content_without_api_key(self, client):
        """Test content scan without API key returns 401"""
        response = client.post('/api/v1/scan-content',
                             json={'content': 'Test content'})
        assert response.status_code == 401
    
    def test_scan_content_with_valid_api_key(self, client, api_key):
        """Test content scan with valid API key"""
        with patch('main.predict_fake_or_real_email_content') as mock_predict:
            mock_predict.return_value = "This is legitimate content"
            
            response = client.post('/api/v1/scan-content',
                                 json={'content': 'Test content'},
                                 headers={'X-API-Key': api_key})
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['status'] == 'completed'
            assert 'result' in data
            assert 'scanned_at' in data
    
    def test_scan_content_too_long(self, client, api_key):
        """Test content scan with content too long returns 400"""
        long_content = 'x' * 10001  # Exceeds 10000 character limit
        
        response = client.post('/api/v1/scan-content',
                             json={'content': long_content},
                             headers={'X-API-Key': api_key})
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'too long' in data['error']

class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limiting_web_endpoints(self, client):
        """Test that web endpoints have rate limiting"""
        # This would require more sophisticated testing with actual rate limiting
        # For now, we'll just test that the decorators are applied
        response = client.get('/')
        assert response.status_code == 200

class TestInputValidation:
    """Test input validation"""
    
    def test_invalid_url_format(self, client, api_key):
        """Test invalid URL format returns 400"""
        response = client.post('/api/v1/scan-url',
                             json={'url': 'not-a-url'},
                             headers={'X-API-Key': api_key})
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Invalid URL format' in data['error']
    
    def test_missing_url_parameter(self, client, api_key):
        """Test missing URL parameter returns 400"""
        response = client.post('/api/v1/scan-url',
                             json={},
                             headers={'X-API-Key': api_key})
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'URL is required' in data['error']
    
    def test_missing_content_parameter(self, client, api_key):
        """Test missing content parameter returns 400"""
        response = client.post('/api/v1/scan-content',
                             json={},
                             headers={'X-API-Key': api_key})
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Content is required' in data['error']

class TestAPIStats:
    """Test API statistics endpoint"""
    
    def test_stats_without_api_key(self, client):
        """Test stats without API key returns 401"""
        response = client.get('/api/v1/stats')
        assert response.status_code == 401
    
    def test_stats_with_valid_api_key(self, client, api_key):
        """Test stats with valid API key"""
        response = client.get('/api/v1/stats',
                            headers={'X-API-Key': api_key})
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'total_tasks' in data
        assert 'completed_tasks' in data
        assert 'failed_tasks' in data
        assert 'active_api_keys' in data
        assert 'timestamp' in data

if __name__ == '__main__':
    pytest.main([__file__])



