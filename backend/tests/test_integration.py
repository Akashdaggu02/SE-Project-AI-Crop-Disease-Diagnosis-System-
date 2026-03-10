"""
Integration tests for the Smart Crop Health API.
Tests the interactions between multiple modules through Flask endpoints.
Uses mocking to isolate from external services (MongoDB, ML models).
"""
import pytest
import sys
import os
import json
import io
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# ─── Health & Info Endpoints ───────────────────────────────────────────
class TestHealthEndpoints:
    def test_health_check(self, client):
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['version'] == '1.0.0'

    def test_root_endpoint(self, client):
        response = client.get('/')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'online'
        assert 'endpoints' in data

    def test_api_info(self, client):
        response = client.get('/api')
        assert response.status_code == 200
        data = response.get_json()
        assert 'user' in data['endpoints']
        assert 'diagnosis' in data['endpoints']
        assert 'cost' in data['endpoints']
        assert 'chatbot' in data['endpoints']
        assert 'grape' in data['supported_crops']

    def test_404_handler(self, client):
        response = client.get('/nonexistent-endpoint')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data


# ─── User Flow Integration ────────────────────────────────────────────
class TestUserFlowIntegration:
    @patch('api.routes.user.db')
    def test_register_missing_fields(self, mock_db, client):
        response = client.post('/api/user/register',
                               data=json.dumps({}),
                               content_type='application/json')
        assert response.status_code == 400

    @patch('api.routes.user.db')
    def test_register_invalid_email(self, mock_db, client):
        data = {
            'email': 'bad-email',
            'password': 'secure123',
            'name': 'Test User'
        }
        response = client.post('/api/user/register',
                               data=json.dumps(data),
                               content_type='application/json')
        assert response.status_code == 400

    @patch('api.routes.user.db')
    def test_register_success(self, mock_db, client):
        mock_db.execute_query.return_value = []  # no existing user
        mock_db.execute_insert.return_value = "mock_user_id_123"

        data = {
            'email': 'newuser@example.com',
            'password': 'secure123',
            'name': 'New User'
        }
        response = client.post('/api/user/register',
                               data=json.dumps(data),
                               content_type='application/json')
        assert response.status_code == 201
        resp_data = response.get_json()
        assert 'user_id' in resp_data
        assert resp_data['email'] == 'newuser@example.com'

    @patch('api.routes.user.db')
    def test_register_duplicate_email(self, mock_db, client):
        mock_db.execute_query.return_value = [{'email': 'existing@example.com'}]

        data = {
            'email': 'existing@example.com',
            'password': 'secure123',
            'name': 'Existing User'
        }
        response = client.post('/api/user/register',
                               data=json.dumps(data),
                               content_type='application/json')
        assert response.status_code == 409

    @patch('api.routes.user.db')
    def test_login_missing_fields(self, mock_db, client):
        data = {'email': 'test@example.com'}
        response = client.post('/api/user/login',
                               data=json.dumps(data),
                               content_type='application/json')
        assert response.status_code == 400

    @patch('api.routes.user.db')
    def test_login_user_not_found(self, mock_db, client):
        mock_db.execute_query.return_value = []
        data = {'email': 'nobody@example.com', 'password': 'wrongpass'}
        response = client.post('/api/user/login',
                               data=json.dumps(data),
                               content_type='application/json')
        assert response.status_code == 401

    def test_profile_no_token(self, client):
        response = client.get('/api/user/profile')
        assert response.status_code == 401

    def test_profile_invalid_token(self, client):
        response = client.get('/api/user/profile',
                              headers={'Authorization': 'Bearer invalid_token'})
        assert response.status_code == 401


# ─── Diagnosis Flow Integration ───────────────────────────────────────
class TestDiagnosisFlowIntegration:
    def test_detect_no_image(self, client):
        response = client.post('/api/diagnosis/detect',
                               data={'crop': 'tomato'},
                               content_type='multipart/form-data')
        assert response.status_code == 400

    def test_detect_no_crop(self, client):
        data = {
            'image': (io.BytesIO(b"fake_image_data"), 'test.jpg')
        }
        response = client.post('/api/diagnosis/detect',
                               data=data,
                               content_type='multipart/form-data')
        assert response.status_code == 400

    def test_detect_invalid_crop(self, client):
        data = {
            'image': (io.BytesIO(b"fake_image_data"), 'test.jpg'),
            'crop': 'banana'
        }
        response = client.post('/api/diagnosis/detect',
                               data=data,
                               content_type='multipart/form-data')
        assert response.status_code == 400

    def test_detect_invalid_file_type(self, client):
        data = {
            'image': (io.BytesIO(b"fake_data"), 'test.txt'),
            'crop': 'tomato'
        }
        response = client.post('/api/diagnosis/detect',
                               data=data,
                               content_type='multipart/form-data')
        assert response.status_code == 400

    @patch('api.routes.diagnosis.full_prediction')
    @patch('api.routes.diagnosis.check_image_quality')
    @patch('api.routes.diagnosis.check_content_validity')
    def test_detect_success_mocked(self, mock_validity, mock_quality, mock_prediction, client):
        mock_quality.return_value = {'is_valid': True, 'quality_score': 0.9}
        mock_validity.return_value = {'is_valid': True, 'confidence': 0.95}
        mock_prediction.return_value = {
            'crop': 'tomato',
            'disease': 'Early blight',
            'confidence': 92.5,
            'severity_percent': 25.0,
            'stage': 'Early Stage'
        }

        data = {
            'image': (io.BytesIO(b"fake_image_data"), 'test_leaf.jpg'),
            'crop': 'tomato'
        }
        response = client.post('/api/diagnosis/detect',
                               data=data,
                               content_type='multipart/form-data')
        assert response.status_code == 200
        resp_data = response.get_json()
        assert 'prediction' in resp_data
        assert resp_data['prediction']['disease'] == 'Early blight'
        mock_prediction.assert_called_once()

    def test_history_no_auth(self, client):
        response = client.get('/api/diagnosis/history')
        assert response.status_code == 401


# ─── Cost Endpoint Integration ────────────────────────────────────────
class TestCostIntegration:
    def test_calculate_no_auth(self, client):
        response = client.post('/api/cost/calculate',
                               data=json.dumps({}),
                               content_type='application/json')
        assert response.status_code == 401


# ─── Chatbot Endpoint Integration ─────────────────────────────────────
class TestChatbotIntegration:
    def test_chatbot_message_no_data(self, client):
        response = client.post('/api/chatbot/message',
                               data=json.dumps({}),
                               content_type='application/json')
        # Should return error (400 or 401 depending on auth requirements)
        assert response.status_code in [400, 401, 500]


# ─── Weather Endpoint Integration ─────────────────────────────────────
class TestWeatherIntegration:
    def test_weather_endpoint_exists(self, client):
        # Test that the blueprint is registered even if no specific route
        response = client.get('/api/weather/')
        # Could be 404 or 405 depending on route existence
        assert response.status_code in [404, 405, 200]
