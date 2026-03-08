"""
Unit tests for services/cost_service.py
Tests cost calculation functions: extract_quantity, treatment cost, prevention cost, 
total cost, cost report generation, and per-acre comparison.
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.cost_service import (
    extract_quantity,
    calculate_treatment_cost,
    calculate_prevention_cost,
    calculate_total_cost,
    generate_cost_report,
    get_cost_per_acre_comparison,
)


# ─── extract_quantity ──────────────────────────────────────────────────
class TestExtractQuantity:
    def test_single_number_liters(self):
        assert extract_quantity("2 liters") == 2.0

    def test_range_numbers(self):
        result = extract_quantity("2-3 kg")
        assert result == 2.5  # average of 2 and 3

    def test_ml_conversion(self):
        result = extract_quantity("500 ml")
        assert result == 0.5  # 500/1000

    def test_gram_conversion(self):
        result = extract_quantity("250 grams")
        assert result == 0.25

    def test_no_numbers(self):
        result = extract_quantity("some dosage")
        assert result == 1.0  # default

    def test_decimal_number(self):
        result = extract_quantity("1.5 liters")
        assert result == 1.5

    def test_empty_string(self):
        result = extract_quantity("")
        assert result == 1.0  # default


# ─── calculate_treatment_cost ──────────────────────────────────────────
class TestCalculateTreatmentCost:
    def test_empty_pesticides(self):
        result = calculate_treatment_cost([], 10.0, 20.0)
        assert result['pesticide_cost'] == 0
        assert result['labor_cost'] == 0
        assert result['total_treatment_cost'] == 0
        assert result['applications_needed'] == 0

    def test_with_pesticides_low_severity(self):
        pesticides = [{
            'name': 'Mancozeb',
            'dosage_per_acre': '2 liters',
            'cost_per_liter': 500
        }]
        result = calculate_treatment_cost(pesticides, 5.0, 3.0)
        assert result['applications_needed'] == 1
        assert result['pesticide_cost'] > 0
        assert result['labor_cost'] > 0

    def test_with_pesticides_high_severity(self):
        pesticides = [{
            'name': 'Mancozeb',
            'dosage_per_acre': '2 liters',
            'cost_per_liter': 500
        }]
        result = calculate_treatment_cost(pesticides, 5.0, 60.0)
        assert result['applications_needed'] == 4

    def test_severity_thresholds(self):
        pesticides = [{'name': 'Test', 'dosage_per_acre': '1 liter', 'cost_per_liter': 100}]
        
        r1 = calculate_treatment_cost(pesticides, 1.0, 3.0)
        assert r1['applications_needed'] == 1  # < 5%
        
        r2 = calculate_treatment_cost(pesticides, 1.0, 15.0)
        assert r2['applications_needed'] == 2  # < 25%
        
        r3 = calculate_treatment_cost(pesticides, 1.0, 35.0)
        assert r3['applications_needed'] == 3  # < 50%
        
        r4 = calculate_treatment_cost(pesticides, 1.0, 55.0)
        assert r4['applications_needed'] == 4  # >= 50%

    def test_max_three_pesticides(self):
        pesticides = [
            {'name': f'Pest{i}', 'dosage_per_acre': '1 liter', 'cost_per_liter': 100}
            for i in range(5)
        ]
        result = calculate_treatment_cost(pesticides, 1.0, 10.0)
        assert len(result['pesticide_details']) == 3  # max 3

    def test_cost_scaling_with_land_area(self):
        pesticides = [{'name': 'Test', 'dosage_per_acre': '1 liter', 'cost_per_liter': 100}]
        r1 = calculate_treatment_cost(pesticides, 1.0, 10.0)
        r2 = calculate_treatment_cost(pesticides, 2.0, 10.0)
        assert r2['total_treatment_cost'] == r1['total_treatment_cost'] * 2


# ─── calculate_prevention_cost ─────────────────────────────────────────
class TestCalculatePreventionCost:
    def test_basic_prevention_cost(self):
        result = calculate_prevention_cost(1.0, 'tomato')
        assert result['total_prevention_cost'] > 0
        assert result['applications'] == 2
        assert result['land_area'] == 1.0

    def test_prevention_cost_scaling(self):
        r1 = calculate_prevention_cost(1.0, 'tomato')
        r2 = calculate_prevention_cost(2.0, 'tomato')
        assert r2['total_prevention_cost'] == r1['total_prevention_cost'] * 2

    def test_prevention_cost_components(self):
        result = calculate_prevention_cost(1.0, 'rice')
        assert 'preventive_spray_cost' in result
        assert 'monitoring_cost' in result
        assert 'good_practices_cost' in result
        total = (
            result['preventive_spray_cost'] +
            result['monitoring_cost'] +
            result['good_practices_cost']
        )
        assert result['total_prevention_cost'] == total


# ─── calculate_total_cost ──────────────────────────────────────────────
class TestCalculateTotalCost:
    @patch('services.cost_service.get_severity_based_recommendations')
    def test_total_cost_with_mocked_recommendations(self, mock_rec):
        mock_rec.return_value = {
            'severity_level': 'Moderate',
            'urgency': 'high',
            'recommended_pesticides': [{
                'name': 'Mancozeb',
                'dosage_per_acre': '2 liters',
                'cost_per_liter': 500,
                'is_organic': False
            }]
        }
        result = calculate_total_cost('Early Blight', 35.0, 5.0, 'tomato')
        assert 'treatment' in result
        assert 'prevention' in result
        assert 'comparison' in result
        assert result['comparison']['total_cost'] > 0

    @patch('services.cost_service.get_severity_based_recommendations')
    def test_total_cost_without_prevention(self, mock_rec):
        mock_rec.return_value = {
            'severity_level': 'Early',
            'urgency': 'low',
            'recommended_pesticides': []
        }
        result = calculate_total_cost('Healthy', 2.0, 1.0, 'tomato', include_prevention=False)
        assert result['prevention']['total_prevention_cost'] == 0

    @patch('services.cost_service.get_severity_based_recommendations')
    def test_total_cost_no_pesticides(self, mock_rec):
        mock_rec.return_value = {
            'severity_level': 'Unknown',
            'urgency': 'medium',
            'recommended_pesticides': []
        }
        result = calculate_total_cost('Unknown', 10.0, 1.0, 'grape')
        assert result['treatment']['total_treatment_cost'] == 0


# ─── generate_cost_report ─────────────────────────────────────────────
class TestGenerateCostReport:
    def test_report_generation(self):
        cost_data = {
            'crop': 'tomato',
            'disease': 'Early Blight',
            'severity_level': 'Moderate',
            'land_area': 5.0,
            'urgency': 'high',
            'treatment': {
                'pesticide_cost': 5000.0,
                'labor_cost': 2000.0,
                'total_treatment_cost': 7000.0,
                'applications_needed': 3
            },
            'prevention': {
                'total_prevention_cost': 3000.0
            },
            'comparison': {
                'total_cost': 10000.0
            }
        }
        report = generate_cost_report(cost_data)
        assert 'Tomato' in report
        assert 'Early Blight' in report
        assert 'HIGH' in report
        assert '₹' in report
        assert isinstance(report, str)

    def test_report_contains_all_sections(self):
        cost_data = {
            'crop': 'rice',
            'disease': 'Brown spot',
            'severity_level': 'Early Stage',
            'land_area': 2.0,
            'urgency': 'medium',
            'treatment': {
                'pesticide_cost': 1000.0,
                'labor_cost': 500.0,
                'total_treatment_cost': 1500.0,
                'applications_needed': 2
            },
            'prevention': {
                'total_prevention_cost': 900.0
            },
            'comparison': {
                'total_cost': 2400.0
            }
        }
        report = generate_cost_report(cost_data)
        assert 'TREATMENT COST BREAKDOWN' in report
        assert 'PREVENTION COST' in report
        assert 'TOTAL ESTIMATED COST' in report
