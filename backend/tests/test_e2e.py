"""
End-to-End tests for the Smart Crop Health API.
Simulates real user workflows through the complete API.
Tests the full system from input to output for normal usage scenarios.
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


# ─── E2E: System Health Verification ──────────────────────────────────
class TestE2ESystemHealth:
    """Simulate a user checking if the system is online."""

    def test_full_health_flow(self, client):
        """User opens the app, check root + health + API info."""
        # Step 1: Root endpoint
        resp = client.get('/')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'online'

        # Step 2: Health check
        resp = client.get('/health')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'healthy'

        # Step 3: API info
        resp = client.get('/api')
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data['supported_crops']) == 5
        assert len(data['supported_languages']) == 6


# ─── E2E: User Registration and Login ─────────────────────────────────
class TestE2EUserRegistrationLogin:
    """Simulate a new farmer registering and then logging in."""

    @patch('api.routes.user.db')
    def test_register_then_login_flow(self, mock_db, client):
        import bcrypt

        # Step 1: Register
        mock_db.execute_query.return_value = []  # not exists
        mock_db.execute_insert.return_value = "user_001"

        reg_data = {
            'email': 'farmer@village.com',
            'password': 'crops2024',
            'name': 'Ramu Farmer',
            'phone': '9876543210',
            'farm_location': 'Hyderabad',
            'farm_size': 5
        }
        resp = client.post('/api/user/register',
                           data=json.dumps(reg_data),
                           content_type='application/json')
        assert resp.status_code == 201
        reg_resp = resp.get_json()
        assert reg_resp['user_id'] == 'user_001'

        # Step 2: Login with the same credentials
        stored_hash = bcrypt.hashpw('crops2024'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        mock_db.execute_query.return_value = [{
            '_id': 'user_001',
            'email': 'farmer@village.com',
            'password_hash': stored_hash,
            'name': 'Ramu Farmer',
            'preferred_language': 'te'
        }]

        login_data = {
            'email': 'farmer@village.com',
            'password': 'crops2024'
        }
        resp = client.post('/api/user/login',
                           data=json.dumps(login_data),
                           content_type='application/json')
        assert resp.status_code == 200
        login_resp = resp.get_json()
        assert 'token' in login_resp
        assert login_resp['user']['name'] == 'Ramu Farmer'


# ─── E2E: Disease Diagnosis Flow ──────────────────────────────────────
class TestE2EDiagnosisFlow:
    """Simulate a farmer uploading a leaf image and getting diagnosis."""

    @patch('api.routes.diagnosis.full_prediction')
    @patch('api.routes.diagnosis.check_image_quality')
    @patch('api.routes.diagnosis.check_content_validity')
    @patch('api.routes.diagnosis.db')
    @patch('api.routes.diagnosis.generate_diagnosis_voice')
    @patch('api.routes.diagnosis.get_severity_based_recommendations')
    def test_anonymous_diagnosis_flow(
        self, mock_recs, mock_voice, mock_db, mock_validity,
        mock_quality, mock_prediction, client
    ):
        """Anonymous user uploads an image for diagnosis."""
        mock_quality.return_value = {'is_valid': True, 'quality_score': 0.85}
        mock_validity.return_value = {'is_valid': True, 'confidence': 0.92}
        mock_prediction.return_value = {
            'crop': 'tomato',
            'disease': 'Bacterial spot',
            'confidence': 88.5,
            'severity_percent': 30.0,
            'stage': 'Moderate Stage'
        }
        mock_recs.return_value = {
            'severity_level': 'Moderate',
            'recommended_pesticides': [{
                'name': 'Copper Oxychloride',
                'dosage_per_acre': '2 kg',
                'frequency': 'Every 7 days',
                'cost_per_liter': 600,
                'is_organic': False,
                'warnings': 'Avoid during rain'
            }],
            'treatment_approach': 'Apply fungicides',
            'urgency': 'high'
        }
        mock_voice.return_value = None
        mock_db.execute_query.return_value = []
        mock_db.execute_insert.return_value = "diag_001"

        data = {
            'image': (io.BytesIO(b"fake_leaf_image_bytes"), 'tomato_leaf.jpg'),
            'crop': 'tomato'
        }
        resp = client.post('/api/diagnosis/detect',
                           data=data,
                           content_type='multipart/form-data')
        assert resp.status_code == 200
        result = resp.get_json()

        # Verify the response structure
        assert 'prediction' in result
        assert result['prediction']['disease'] == 'Bacterial spot'
        assert result['prediction']['confidence'] == 88.5
        assert 'pesticide_recommendations' in result
        assert 'image_quality' in result

    @patch('api.routes.diagnosis.check_image_quality')
    def test_low_quality_image_rejected(self, mock_quality, client):
        """User uploads a blurry image — should be rejected."""
        mock_quality.return_value = {
            'is_valid': False,
            'quality_score': 0.05,
            'reason': 'Image is too blurry. Please capture a clearer image.'
        }

        data = {
            'image': (io.BytesIO(b"blurry_image"), 'blurry.jpg'),
            'crop': 'rice'
        }
        resp = client.post('/api/diagnosis/detect',
                           data=data,
                           content_type='multipart/form-data')
        assert resp.status_code == 400
        result = resp.get_json()
        assert 'error' in result


# ─── E2E: Input Validation Edge Cases ─────────────────────────────────
class TestE2EInputValidation:
    """Simulate edge-case inputs that users might send."""

    def test_empty_body_register(self, client):
        resp = client.post('/api/user/register',
                           data=json.dumps({}),
                           content_type='application/json')
        assert resp.status_code in [400, 500]

    def test_no_json_body(self, client):
        resp = client.post('/api/user/register',
                           data='not json',
                           content_type='text/plain')
        assert resp.status_code in [400, 415, 500]

    def test_diagnose_without_any_data(self, client):
        resp = client.post('/api/diagnosis/detect')
        assert resp.status_code == 400

    @patch('api.routes.user.db')
    def test_forgot_password_nonexistent(self, mock_db, client):
        """Forgot password for non-existent email returns success (security)."""
        mock_db.execute_query.return_value = []
        data = {'email': 'ghost@nowhere.com'}
        resp = client.post('/api/user/forgot-password',
                           data=json.dumps(data),
                           content_type='application/json')
        assert resp.status_code == 200  # doesn't reveal if email exists

    @patch('api.routes.user.db')
    def test_reset_password_missing_fields(self, mock_db, client):
        data = {'email': 'test@test.com'}
        resp = client.post('/api/user/reset-password',
                           data=json.dumps(data),
                           content_type='application/json')
        assert resp.status_code == 400
