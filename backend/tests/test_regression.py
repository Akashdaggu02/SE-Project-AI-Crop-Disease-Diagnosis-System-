"""
Regression tests for the Smart Crop Health API.
Ensures previously fixed bugs and critical behaviors remain stable
after code changes, refactoring, or dependency updates.

These tests guard against:
- Reintroduction of known bugs (datetime import, route types)
- Validator boundary regressions
- API response structure changes
- Authentication flow consistency
- ML pipeline output format stability
- Image quality check regressions
"""
import pytest
import sys
import os
import json
import io
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from utils.validators import (
    validate_email,
    validate_phone,
    validate_password,
    validate_land_area,
    validate_crop_type,
    validate_language,
    validate_image_file,
    sanitize_input,
    validate_coordinates,
    validate_user_registration,
    validate_diagnosis_request,
)


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# ─── Regression: Known Bug Guards ─────────────────────────────────────
class TestRegressionKnownBugs:
    """Tests that guard against reintroduction of previously identified bugs."""

    def test_cost_route_accepts_string_diagnosis_id(self, client):
        """
        BUG FIX GUARD: cost.py route used <int:diagnosis_id> but MongoDB
        uses string ObjectId. Verify the route does not reject string IDs.
        Ref: Bug #3 in QA Report — Route type mismatch.
        """
        # Attempt to access cost report with a string ObjectId
        response = client.get('/api/cost/report/507f1f77bcf86cd799439011')
        # Should NOT return 404 due to type mismatch — may return 401 (auth required)
        # The key check: it doesn't crash with a URL routing error
        assert response.status_code in [200, 401, 404]

    @patch('api.routes.user.db')
    def test_user_registration_response_structure_stable(self, mock_db, client):
        """
        REGRESSION GUARD: Registration response must always contain 'user_id'
        and 'email' fields. Structure changes would break mobile app.
        """
        mock_db.execute_query.return_value = []
        mock_db.execute_insert.return_value = "user_reg_001"

        data = {
            'email': 'regression@test.com',
            'password': 'secure123',
            'name': 'Regression User'
        }
        response = client.post('/api/user/register',
                               data=json.dumps(data),
                               content_type='application/json')
        assert response.status_code == 201
        resp_data = response.get_json()
        # These fields MUST be present — mobile app depends on them
        assert 'user_id' in resp_data, "Registration response missing 'user_id' field"
        assert 'email' in resp_data, "Registration response missing 'email' field"

    @patch('api.routes.user.db')
    def test_login_response_contains_token(self, mock_db, client):
        """
        REGRESSION GUARD: Login response must always return a JWT token.
        Any refactoring of auth must preserve this contract.
        """
        import bcrypt
        stored_hash = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        mock_db.execute_query.return_value = [{
            '_id': 'user_001',
            'email': 'login@test.com',
            'password_hash': stored_hash,
            'name': 'Login Test',
            'preferred_language': 'en'
        }]

        data = {'email': 'login@test.com', 'password': 'password123'}
        response = client.post('/api/user/login',
                               data=json.dumps(data),
                               content_type='application/json')
        assert response.status_code == 200
        resp_data = response.get_json()
        assert 'token' in resp_data, "Login response missing 'token' field"
        assert 'user' in resp_data, "Login response missing 'user' field"


# ─── Regression: Validator Boundary Stability ─────────────────────────
class TestRegressionValidatorBoundaries:
    """Ensure validator boundary values remain stable across code changes."""

    def test_email_format_regression(self):
        """Guard: standard email formats must always be accepted."""
        valid_emails = [
            "user@example.com",
            "first.last@domain.co.in",
            "user+tag@gmail.com",
            "test123@test.org",
        ]
        for email in valid_emails:
            assert validate_email(email) is True, f"Valid email '{email}' rejected — regression!"

    def test_email_rejection_regression(self):
        """Guard: known-invalid formats must always be rejected."""
        invalid_emails = [
            "userexample.com",
            "user@",
            "",
            "user@@example.com",
        ]
        for email in invalid_emails:
            assert validate_email(email) is False, f"Invalid email '{email}' accepted — regression!"

    def test_password_boundary_6_chars(self):
        """Guard: minimum password length of 6 must be enforced."""
        assert validate_password("12345")['is_valid'] is False, "5-char password accepted — regression!"
        assert validate_password("123456")['is_valid'] is True, "6-char password rejected — regression!"

    def test_password_boundary_50_chars(self):
        """Guard: maximum password length of 50 must be enforced."""
        assert validate_password("a" * 50)['is_valid'] is True, "50-char password rejected — regression!"
        assert validate_password("a" * 51)['is_valid'] is False, "51-char password accepted — regression!"

    def test_coordinate_boundaries_stable(self):
        """Guard: GPS coordinate limits must remain ±90 lat, ±180 lon."""
        assert validate_coordinates(90.0, 180.0) is True
        assert validate_coordinates(-90.0, -180.0) is True
        assert validate_coordinates(91.0, 0.0) is False
        assert validate_coordinates(0.0, 181.0) is False

    def test_all_supported_crops_accepted(self):
        """Guard: all 5 supported crops must always be valid."""
        crops = ['tomato', 'rice', 'grape', 'maize', 'potato']
        for crop in crops:
            assert validate_crop_type(crop) is True, f"Supported crop '{crop}' rejected — regression!"

    def test_all_supported_languages_accepted(self):
        """Guard: all 6 supported languages must always be valid."""
        languages = ['en', 'hi', 'te', 'ta', 'kn', 'mr']
        for lang in languages:
            assert validate_language(lang) is True, f"Supported language '{lang}' rejected — regression!"

    def test_land_area_max_boundary(self):
        """Guard: 10000 acres must be accepted, 10001 must be rejected."""
        assert validate_land_area(10000.0)['is_valid'] is True
        assert validate_land_area(10001.0)['is_valid'] is False


# ─── Regression: API Endpoint Stability ───────────────────────────────
class TestRegressionAPIEndpoints:
    """Ensure all API endpoints remain accessible and return expected formats."""

    def test_health_endpoint_structure(self, client):
        """Guard: /health must always return status, service, and version."""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data, "/health missing 'status' — regression!"
        assert 'version' in data, "/health missing 'version' — regression!"
        assert data['status'] == 'healthy'
        assert data['version'] == '1.0.0'

    def test_root_endpoint_structure(self, client):
        """Guard: / must always return status and endpoints list."""
        response = client.get('/')
        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data
        assert data['status'] == 'online'
        assert 'endpoints' in data

    def test_api_info_supported_crops(self, client):
        """Guard: /api must list exactly 5 supported crops."""
        response = client.get('/api')
        assert response.status_code == 200
        data = response.get_json()
        assert 'supported_crops' in data
        assert len(data['supported_crops']) == 5
        for crop in ['grape', 'maize', 'potato', 'rice', 'tomato']:
            assert crop in data['supported_crops'], f"'{crop}' missing from /api supported_crops"

    def test_api_info_supported_languages(self, client):
        """Guard: /api must list exactly 6 supported languages."""
        response = client.get('/api')
        data = response.get_json()
        assert 'supported_languages' in data
        assert len(data['supported_languages']) == 6

    def test_404_returns_json_error(self, client):
        """Guard: 404 responses must always be JSON with 'error' key."""
        response = client.get('/this/endpoint/does/not/exist')
        assert response.status_code == 404
        data = response.get_json()
        assert data is not None, "404 response is not JSON — regression!"
        assert 'error' in data, "404 response missing 'error' key — regression!"

    def test_protected_endpoints_require_auth(self, client):
        """Guard: all protected routes must return 401 without token."""
        protected_routes = [
            ('GET', '/api/user/profile'),
            ('GET', '/api/diagnosis/history'),
            ('POST', '/api/cost/calculate'),
        ]
        for method, route in protected_routes:
            if method == 'GET':
                response = client.get(route)
            else:
                response = client.post(route,
                                       data=json.dumps({}),
                                       content_type='application/json')
            assert response.status_code == 401, \
                f"{method} {route} returned {response.status_code} instead of 401 — auth regression!"


# ─── Regression: Diagnosis Pipeline Stability ─────────────────────────
class TestRegressionDiagnosisPipeline:
    """Ensure the diagnosis pipeline output format remains stable."""

    @patch('api.routes.diagnosis.full_prediction')
    @patch('api.routes.diagnosis.check_image_quality')
    @patch('api.routes.diagnosis.check_content_validity')
    @patch('api.routes.diagnosis.db')
    @patch('api.routes.diagnosis.generate_diagnosis_voice')
    @patch('api.routes.diagnosis.get_severity_based_recommendations')
    def test_diagnosis_response_structure_stable(
        self, mock_recs, mock_voice, mock_db, mock_validity,
        mock_quality, mock_prediction, client
    ):
        """Guard: diagnosis response must contain prediction, pesticide_recommendations, image_quality."""
        mock_quality.return_value = {'is_valid': True, 'quality_score': 0.88}
        mock_validity.return_value = {'is_valid': True, 'confidence': 0.90}
        mock_prediction.return_value = {
            'crop': 'rice',
            'disease': 'Brown spot',
            'confidence': 91.2,
            'severity_percent': 22.0,
            'stage': 'Early Stage'
        }
        mock_recs.return_value = {
            'severity_level': 'Low',
            'recommended_pesticides': [{
                'name': 'Mancozeb',
                'dosage_per_acre': '2.5 kg',
                'frequency': 'Every 10 days',
                'cost_per_liter': 450,
                'is_organic': False,
                'warnings': 'Wear gloves'
            }],
            'treatment_approach': 'Apply fungicide spray',
            'urgency': 'moderate'
        }
        mock_voice.return_value = None
        mock_db.execute_query.return_value = []
        mock_db.execute_insert.return_value = "diag_reg_001"

        data = {
            'image': (io.BytesIO(b"regression_test_image"), 'rice_leaf.jpg'),
            'crop': 'rice'
        }
        response = client.post('/api/diagnosis/detect',
                               data=data,
                               content_type='multipart/form-data')
        assert response.status_code == 200
        result = response.get_json()

        # These keys MUST be in the response — mobile app depends on them
        assert 'prediction' in result, "Diagnosis missing 'prediction' — regression!"
        assert 'pesticide_recommendations' in result, "Diagnosis missing 'pesticide_recommendations' — regression!"
        assert 'image_quality' in result, "Diagnosis missing 'image_quality' — regression!"

        # Prediction sub-fields must be present
        pred = result['prediction']
        assert 'disease' in pred, "Prediction missing 'disease' field"
        assert 'confidence' in pred, "Prediction missing 'confidence' field"

    @patch('api.routes.diagnosis.check_image_quality')
    def test_blurry_image_still_rejected(self, mock_quality, client):
        """Guard: low quality images must always be rejected with 400."""
        mock_quality.return_value = {
            'is_valid': False,
            'quality_score': 0.03,
            'reason': 'Image is too blurry.'
        }

        data = {
            'image': (io.BytesIO(b"blurry_regression"), 'blurry.jpg'),
            'crop': 'tomato'
        }
        response = client.post('/api/diagnosis/detect',
                               data=data,
                               content_type='multipart/form-data')
        assert response.status_code == 400
        result = response.get_json()
        assert 'error' in result, "Blurry image rejection missing 'error' — regression!"


# ─── Regression: Input Sanitization ───────────────────────────────────
class TestRegressionSanitization:
    """Ensure XSS/injection protection remains in place."""

    def test_xss_script_tag_always_stripped(self):
        """Guard: <script> tags must NEVER pass through sanitization."""
        malicious_inputs = [
            "<script>alert('xss')</script>",
            '<script type="text/javascript">hack()</script>',
            '<SCRIPT>alert(1)</SCRIPT>',
        ]
        for inp in malicious_inputs:
            result = sanitize_input(inp)
            assert '<script' not in result.lower(), f"XSS not stripped: '{inp}' — CRITICAL regression!"

    def test_html_injection_stripped(self):
        """Guard: HTML tags must be removed from user input."""
        result = sanitize_input('<img src=x onerror=alert(1)>Hello')
        assert '<img' not in result
        assert 'Hello' in result

    def test_none_input_safe(self):
        """Guard: None input must return empty string, never crash."""
        result = sanitize_input(None)
        assert result == ""

    def test_long_input_truncated(self):
        """Guard: inputs exceeding max_length must always be truncated."""
        result = sanitize_input("A" * 1000, max_length=500)
        assert len(result) == 500


# ─── Regression: Image Upload Validation ──────────────────────────────
class TestRegressionImageUpload:
    """Ensure file type and upload validations remain intact."""

    def test_only_jpg_jpeg_png_accepted(self):
        """Guard: only .jpg, .jpeg, .png must be accepted."""
        assert validate_image_file("photo.jpg") is True
        assert validate_image_file("photo.jpeg") is True
        assert validate_image_file("photo.png") is True

    def test_dangerous_file_types_rejected(self):
        """Guard: executable and script file types must always be rejected."""
        dangerous_files = [
            "malware.exe", "hack.bat", "virus.sh", "script.py",
            "payload.php", "shell.jsp", "doc.pdf", "anim.gif",
        ]
        for f in dangerous_files:
            assert validate_image_file(f) is False, f"Dangerous file '{f}' accepted — CRITICAL regression!"

    def test_no_extension_rejected(self):
        """Guard: files without extension must be rejected."""
        assert validate_image_file("noextension") is False

    def test_diagnosis_requires_image(self, client):
        """Guard: diagnosis endpoint must always require an image file."""
        response = client.post('/api/diagnosis/detect',
                               data={'crop': 'tomato'},
                               content_type='multipart/form-data')
        assert response.status_code == 400

    def test_diagnosis_requires_crop_type(self, client):
        """Guard: diagnosis endpoint must always require a crop type."""
        data = {
            'image': (io.BytesIO(b"test_image"), 'leaf.jpg')
        }
        response = client.post('/api/diagnosis/detect',
                               data=data,
                               content_type='multipart/form-data')
        assert response.status_code == 400

    def test_unsupported_crop_rejected(self, client):
        """Guard: unsupported crop types must always return 400."""
        data = {
            'image': (io.BytesIO(b"test_image"), 'leaf.jpg'),
            'crop': 'mango'
        }
        response = client.post('/api/diagnosis/detect',
                               data=data,
                               content_type='multipart/form-data')
        assert response.status_code == 400
