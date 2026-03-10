"""
Unit tests for ML modules:
  - ml/stage_classifier.py (classify_stage)
  - ml/severity_estimator.py (estimate_severity)
  - services/pesticide_service.py (get_severity_level, get_application_note)
"""
import pytest
import sys
import os
import numpy as np
from unittest.mock import patch, MagicMock
import tempfile
import cv2

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Direct imports for testable pure functions
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ml'))

from stage_classifier import classify_stage
from severity_estimator import estimate_severity
from services.pesticide_service import get_severity_level, get_application_note


# ─── Stage Classifier ─────────────────────────────────────────────────
class TestClassifyStage:
    def test_healthy_stage(self):
        assert classify_stage(0) == "Healthy Stage"
        assert classify_stage(5) == "Healthy Stage"
        assert classify_stage(9.9) == "Healthy Stage"

    def test_early_stage(self):
        assert classify_stage(10) == "Early Stage"
        assert classify_stage(20) == "Early Stage"
        assert classify_stage(29.9) == "Early Stage"

    def test_moderate_stage(self):
        assert classify_stage(30) == "Moderate Stage"
        assert classify_stage(45) == "Moderate Stage"
        assert classify_stage(59.9) == "Moderate Stage"

    def test_severe_stage(self):
        assert classify_stage(60) == "Severe Stage"
        assert classify_stage(80) == "Severe Stage"
        assert classify_stage(100) == "Severe Stage"

    def test_boundary_values(self):
        assert classify_stage(9.99) == "Healthy Stage"
        assert classify_stage(10.0) == "Early Stage"
        assert classify_stage(29.99) == "Early Stage"
        assert classify_stage(30.0) == "Moderate Stage"
        assert classify_stage(59.99) == "Moderate Stage"
        assert classify_stage(60.0) == "Severe Stage"


# ─── Severity Level (Pesticide Service) ───────────────────────────────
class TestGetSeverityLevel:
    def test_healthy(self):
        assert get_severity_level(0) == "Healthy"
        assert get_severity_level(4.9) == "Healthy"

    def test_early_stage(self):
        assert get_severity_level(5) == "Early Stage"
        assert get_severity_level(24.9) == "Early Stage"

    def test_moderate(self):
        assert get_severity_level(25) == "Moderate"
        assert get_severity_level(49.9) == "Moderate"

    def test_severe(self):
        assert get_severity_level(50) == "Severe"
        assert get_severity_level(74.9) == "Severe"

    def test_critical(self):
        assert get_severity_level(75) == "Critical"
        assert get_severity_level(100) == "Critical"


# ─── Application Note ─────────────────────────────────────────────────
class TestGetApplicationNote:
    def test_healthy_note(self):
        note = get_application_note(2.0)
        assert "prevention" in note.lower()

    def test_early_note(self):
        note = get_application_note(15.0)
        assert "recommended intervals" in note.lower()

    def test_moderate_note(self):
        note = get_application_note(35.0)
        assert "7-10 days" in note

    def test_severe_note(self):
        note = get_application_note(70.0)
        assert "immediate" in note.lower()
        assert "5-7 days" in note


# ─── Severity Estimator ───────────────────────────────────────────────
class TestEstimateSeverity:
    def _create_test_image(self, color_bgr, filename="test_img.jpg"):
        """Create a temporary test image with a uniform color."""
        tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        img = np.full((256, 256, 3), color_bgr, dtype=np.uint8)
        cv2.imwrite(tmp.name, img)
        return tmp.name

    def test_green_image_low_severity(self):
        """A pure green leaf should have low severity (no disease colors)."""
        path = self._create_test_image([0, 200, 0])
        severity = estimate_severity(path)
        assert severity < 20  # mostly green = healthy
        os.unlink(path)

    def test_yellow_image_high_severity(self):
        """A yellow-brown image should be detected as diseased."""
        # HSV target: H=10-35, S=40-255, V=40-255
        # BGR for a yellowish-brown color
        path = self._create_test_image([30, 180, 220])
        severity = estimate_severity(path)
        assert severity > 0  # some diseased pixels
        os.unlink(path)

    def test_nonexistent_image(self):
        """Should return 0.0 for a missing file."""
        severity = estimate_severity("/non/existent/path.jpg")
        assert severity == 0.0

    def test_return_type(self):
        path = self._create_test_image([100, 150, 100])
        severity = estimate_severity(path)
        assert isinstance(severity, float)
        os.unlink(path)
