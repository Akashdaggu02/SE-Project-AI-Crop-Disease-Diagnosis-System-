"""
Unit tests for utils/image_quality_check.py
Tests image quality validation and content validity checking.
"""
import pytest
import sys
import os
import numpy as np
import cv2
import tempfile

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.image_quality_check import (
    check_image_quality,
    get_quality_feedback,
    check_content_validity,
)


def _create_temp_image(width=300, height=300, color=(100, 150, 100)):
    """Helper to create a temporary image with specified properties."""
    tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    img = np.full((height, width, 3), color, dtype=np.uint8)
    cv2.imwrite(tmp.name, img)
    return tmp.name


def _create_noisy_image(width=300, height=300):
    """Create an image with random noise (high detail, not blurry)."""
    tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    img = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    cv2.imwrite(tmp.name, img)
    return tmp.name


def _create_blurry_image(width=300, height=300):
    """Create a very blurry (uniform) image."""
    tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    img = np.full((height, width, 3), 128, dtype=np.uint8)
    cv2.imwrite(tmp.name, img)
    return tmp.name


# ─── check_image_quality ──────────────────────────────────────────────
class TestCheckImageQuality:
    def test_valid_image(self):
        path = _create_noisy_image()
        result = check_image_quality(path)
        assert result['is_valid'] is True
        assert 'quality_score' in result
        os.unlink(path)

    def test_too_small_image(self):
        path = _create_temp_image(50, 50)
        result = check_image_quality(path)
        assert result['is_valid'] is False
        assert 'too small' in result['reason']
        os.unlink(path)

    def test_too_large_image(self):
        path = _create_temp_image(5000, 5000)
        result = check_image_quality(path)
        assert result['is_valid'] is False
        assert 'too large' in result['reason']
        os.unlink(path)

    def test_nonexistent_image(self):
        result = check_image_quality("/nonexistent/path.jpg")
        assert result['is_valid'] is False
        assert result['quality_score'] == 0.0

    def test_quality_score_range(self):
        path = _create_noisy_image()
        result = check_image_quality(path)
        assert 0.0 <= result['quality_score'] <= 1.0
        os.unlink(path)

    def test_dimensions_in_result(self):
        path = _create_temp_image(400, 300)
        result = check_image_quality(path)
        if 'dimensions' in result:
            assert result['dimensions'] == (400, 300)
        os.unlink(path)

    def test_blurry_image_low_blur_score(self):
        path = _create_blurry_image()
        result = check_image_quality(path)
        assert result['blur_score'] < 0.1
        os.unlink(path)


# ─── get_quality_feedback ─────────────────────────────────────────────
class TestGetQualityFeedback:
    def test_excellent_quality(self):
        result = {'is_valid': True, 'quality_score': 0.85}
        feedback = get_quality_feedback(result)
        assert "Excellent" in feedback

    def test_good_quality(self):
        result = {'is_valid': True, 'quality_score': 0.6}
        feedback = get_quality_feedback(result)
        assert "Good" in feedback

    def test_acceptable_quality(self):
        result = {'is_valid': True, 'quality_score': 0.35}
        feedback = get_quality_feedback(result)
        assert "Acceptable" in feedback

    def test_failed_quality(self):
        result = {'is_valid': False, 'quality_score': 0.1, 'reason': 'Image is too blurry'}
        feedback = get_quality_feedback(result)
        assert "✗" in feedback
        assert "blurry" in feedback


# ─── check_content_validity ───────────────────────────────────────────
class TestCheckContentValidity:
    def test_green_plant_image(self):
        """A green image should be detected as valid plant content."""
        path = _create_temp_image(300, 300, color=(0, 200, 0))  # BGR green
        result = check_content_validity(path)
        assert result['is_valid'] is True
        os.unlink(path)

    def test_non_plant_image_blue(self):
        """A pure blue image should be rejected as non-plant."""
        path = _create_temp_image(300, 300, color=(255, 0, 0))  # BGR blue
        result = check_content_validity(path)
        assert result['is_valid'] is False
        os.unlink(path)

    def test_nonexistent_image(self):
        result = check_content_validity("/nonexistent/path.jpg")
        # Should handle gracefully
        assert 'is_valid' in result
