"""
Unit tests for utils/validators.py
Tests all validation functions: email, phone, password, land area, crop type,
language, image file, input sanitization, coordinates, registration, and diagnosis.
"""
import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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


# ─── Email Validation ─────────────────────────────────────────────────
class TestValidateEmail:
    def test_valid_email(self):
        assert validate_email("user@example.com") is True

    def test_valid_email_with_dots(self):
        assert validate_email("first.last@domain.co.in") is True

    def test_valid_email_with_plus(self):
        assert validate_email("user+tag@gmail.com") is True

    def test_invalid_email_no_at(self):
        assert validate_email("userexample.com") is False

    def test_invalid_email_no_domain(self):
        assert validate_email("user@") is False

    def test_invalid_email_no_tld(self):
        assert validate_email("user@domain") is False

    def test_invalid_email_empty(self):
        assert validate_email("") is False

    def test_invalid_email_spaces(self):
        assert validate_email("user @example.com") is False

    def test_invalid_email_double_at(self):
        assert validate_email("user@@example.com") is False


# ─── Phone Validation ─────────────────────────────────────────────────
class TestValidatePhone:
    def test_valid_indian_phone(self):
        assert validate_phone("9876543210") is True

    def test_valid_phone_with_country_code(self):
        assert validate_phone("+919876543210") is True

    def test_valid_phone_with_spaces(self):
        assert validate_phone("98765 43210") is True

    def test_valid_phone_with_dashes(self):
        assert validate_phone("9876-543-210") is True

    def test_invalid_phone_too_short(self):
        assert validate_phone("12345") is False

    def test_invalid_phone_starts_with_low_digit(self):
        assert validate_phone("1234567890") is False

    def test_invalid_phone_empty(self):
        assert validate_phone("") is False


# ─── Password Validation ──────────────────────────────────────────────
class TestValidatePassword:
    def test_valid_password(self):
        result = validate_password("secure123")
        assert result['is_valid'] is True

    def test_password_too_short(self):
        result = validate_password("abc")
        assert result['is_valid'] is False
        assert "6 characters" in result['message']

    def test_password_too_long(self):
        result = validate_password("a" * 51)
        assert result['is_valid'] is False
        assert "50 characters" in result['message']

    def test_password_minimum_length(self):
        result = validate_password("123456")
        assert result['is_valid'] is True

    def test_password_maximum_length(self):
        result = validate_password("a" * 50)
        assert result['is_valid'] is True

    def test_password_empty(self):
        result = validate_password("")
        assert result['is_valid'] is False


# ─── Land Area Validation ─────────────────────────────────────────────
class TestValidateLandArea:
    def test_valid_area(self):
        result = validate_land_area(10.0)
        assert result['is_valid'] is True

    def test_negative_area(self):
        result = validate_land_area(-5.0)
        assert result['is_valid'] is False

    def test_zero_area(self):
        # 0 is not negative, so it should be valid per current logic
        result = validate_land_area(0.0)
        assert result['is_valid'] is True

    def test_too_large_area(self):
        result = validate_land_area(10001.0)
        assert result['is_valid'] is False

    def test_boundary_area_10000(self):
        result = validate_land_area(10000.0)
        assert result['is_valid'] is True

    def test_small_fractional_area(self):
        result = validate_land_area(0.5)
        assert result['is_valid'] is True


# ─── Crop Type Validation ─────────────────────────────────────────────
class TestValidateCropType:
    def test_valid_crops(self):
        for crop in ['tomato', 'rice', 'grape', 'maize', 'potato']:
            assert validate_crop_type(crop) is True

    def test_valid_crop_uppercase(self):
        assert validate_crop_type("TOMATO") is True

    def test_invalid_crop(self):
        assert validate_crop_type("banana") is False

    def test_empty_crop(self):
        assert validate_crop_type("") is False


# ─── Language Validation ───────────────────────────────────────────────
class TestValidateLanguage:
    def test_valid_languages(self):
        for lang in ['en', 'hi', 'te', 'ta', 'kn', 'mr']:
            assert validate_language(lang) is True

    def test_invalid_language(self):
        assert validate_language("fr") is False

    def test_empty_language(self):
        assert validate_language("") is False


# ─── Image File Validation ─────────────────────────────────────────────
class TestValidateImageFile:
    def test_valid_jpg(self):
        assert validate_image_file("photo.jpg") is True

    def test_valid_jpeg(self):
        assert validate_image_file("photo.jpeg") is True

    def test_valid_png(self):
        assert validate_image_file("photo.png") is True

    def test_invalid_gif(self):
        assert validate_image_file("photo.gif") is False

    def test_invalid_pdf(self):
        assert validate_image_file("document.pdf") is False

    def test_no_extension(self):
        assert validate_image_file("photo") is False

    def test_case_insensitive(self):
        assert validate_image_file("photo.JPG") is True


# ─── Input Sanitization ───────────────────────────────────────────────
class TestSanitizeInput:
    def test_removes_html_tags(self):
        result = sanitize_input("<script>alert('xss')</script>Hello")
        assert "<script>" not in result
        assert "Hello" in result

    def test_truncates_long_input(self):
        result = sanitize_input("a" * 600, max_length=500)
        assert len(result) == 500

    def test_strips_whitespace(self):
        result = sanitize_input("  hello world  ")
        assert result == "hello world"

    def test_empty_input(self):
        result = sanitize_input("")
        assert result == ""

    def test_none_input(self):
        result = sanitize_input(None)
        assert result == ""

    def test_normal_input(self):
        result = sanitize_input("My tomato has spots")
        assert result == "My tomato has spots"


# ─── Coordinate Validation ────────────────────────────────────────────
class TestValidateCoordinates:
    def test_valid_coordinates(self):
        assert validate_coordinates(17.385, 78.486) is True

    def test_none_coordinates(self):
        assert validate_coordinates(None, None) is True

    def test_invalid_latitude_too_high(self):
        assert validate_coordinates(91.0, 78.0) is False

    def test_invalid_latitude_too_low(self):
        assert validate_coordinates(-91.0, 78.0) is False

    def test_invalid_longitude_too_high(self):
        assert validate_coordinates(17.0, 181.0) is False

    def test_invalid_longitude_too_low(self):
        assert validate_coordinates(17.0, -181.0) is False

    def test_boundary_values(self):
        assert validate_coordinates(90.0, 180.0) is True
        assert validate_coordinates(-90.0, -180.0) is True


# ─── User Registration Validation ─────────────────────────────────────
class TestValidateUserRegistration:
    def test_valid_registration(self):
        data = {
            'email': 'test@example.com',
            'password': 'secure123',
            'name': 'Test User'
        }
        result = validate_user_registration(data)
        assert result['is_valid'] is True
        assert len(result['errors']) == 0

    def test_missing_email(self):
        data = {'password': 'secure123', 'name': 'Test User'}
        result = validate_user_registration(data)
        assert result['is_valid'] is False
        assert 'Email is required' in result['errors']

    def test_invalid_email(self):
        data = {'email': 'bad-email', 'password': 'secure123', 'name': 'Test User'}
        result = validate_user_registration(data)
        assert result['is_valid'] is False

    def test_missing_password(self):
        data = {'email': 'test@example.com', 'name': 'Test User'}
        result = validate_user_registration(data)
        assert result['is_valid'] is False

    def test_short_password(self):
        data = {'email': 'test@example.com', 'password': '123', 'name': 'Test User'}
        result = validate_user_registration(data)
        assert result['is_valid'] is False

    def test_missing_name(self):
        data = {'email': 'test@example.com', 'password': 'secure123'}
        result = validate_user_registration(data)
        assert result['is_valid'] is False

    def test_short_name(self):
        data = {'email': 'test@example.com', 'password': 'secure123', 'name': 'A'}
        result = validate_user_registration(data)
        assert result['is_valid'] is False

    def test_invalid_phone(self):
        data = {
            'email': 'test@example.com',
            'password': 'secure123',
            'name': 'Test User',
            'phone': '12345'
        }
        result = validate_user_registration(data)
        assert result['is_valid'] is False

    def test_valid_with_optional_fields(self):
        data = {
            'email': 'test@example.com',
            'password': 'secure123',
            'name': 'Test User',
            'phone': '9876543210',
            'farm_size': '5.0'
        }
        result = validate_user_registration(data)
        assert result['is_valid'] is True

    def test_invalid_farm_size(self):
        data = {
            'email': 'test@example.com',
            'password': 'secure123',
            'name': 'Test User',
            'farm_size': 'not-a-number'
        }
        result = validate_user_registration(data)
        assert result['is_valid'] is False

    def test_empty_data(self):
        data = {}
        result = validate_user_registration(data)
        assert result['is_valid'] is False
        assert len(result['errors']) >= 3  # email, password, name


# ─── Diagnosis Request Validation ─────────────────────────────────────
class TestValidateDiagnosisRequest:
    def test_valid_request(self):
        data = {'crop': 'tomato', 'image': 'leaf.jpg'}
        result = validate_diagnosis_request(data)
        assert result['is_valid'] is True

    def test_missing_crop(self):
        data = {'image': 'leaf.jpg'}
        result = validate_diagnosis_request(data)
        assert result['is_valid'] is False

    def test_invalid_crop(self):
        data = {'crop': 'banana', 'image': 'leaf.jpg'}
        result = validate_diagnosis_request(data)
        assert result['is_valid'] is False

    def test_missing_image(self):
        data = {'crop': 'tomato'}
        result = validate_diagnosis_request(data)
        assert result['is_valid'] is False

    def test_invalid_coordinates(self):
        data = {'crop': 'tomato', 'image': 'leaf.jpg', 'latitude': 100.0, 'longitude': 200.0}
        result = validate_diagnosis_request(data)
        assert result['is_valid'] is False
