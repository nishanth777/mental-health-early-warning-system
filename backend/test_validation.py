import unittest
from unittest.mock import patch, MagicMock
import sys

# Mock cv2 and torch completely before importing app modules
sys.modules['cv2'] = MagicMock()
sys.modules['torch'] = MagicMock()
sys.modules['torch.nn'] = MagicMock()
sys.modules['torchvision'] = MagicMock()
sys.modules['torchvision.transforms'] = MagicMock()

from app import create_app
import math
import json

class TestAssessmentValidation(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['JWT_SECRET_KEY'] = 'test-secret'
        self.client = self.app.test_client()

        # Mock jwt_required and get_jwt_identity
        self.jwt_patcher = patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
        self.mock_jwt_required = self.jwt_patcher.start()

        self.identity_patcher = patch('flask_jwt_extended.utils.get_jwt_identity')
        self.mock_get_jwt_identity = self.identity_patcher.start()
        self.mock_get_jwt_identity.return_value = 1  # Mock user ID 1

        # Mock database session
        self.db_patcher = patch('app.extensions.db.session')
        self.mock_db_session = self.db_patcher.start()

    def tearDown(self):
        self.jwt_patcher.stop()
        self.identity_patcher.stop()
        self.db_patcher.stop()

    def test_nan_rejection(self):
        payload = {
            "sleep_hours": float('nan'),
            "sleep_quality": 3,
            "stress_level": 3,
            "academic_pressure": 3,
            "mood": 3,
            "energy_level": 3,
            "social_interaction": 3,
            "exercise_minutes": 30,
            "screen_time": 2,
            "study_hours": 4,
            "journal_text": "Testing NaN"
        }
        response = self.client.post('/assessment/',
                                    data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Input values must be finite numbers.", response.data)

    def test_inf_rejection(self):
        payload = {
            "sleep_hours": float('inf'),
            "sleep_quality": 3,
            "stress_level": 3,
            "academic_pressure": 3,
            "mood": 3,
            "energy_level": 3,
            "social_interaction": 3,
            "exercise_minutes": 30,
            "screen_time": 2,
            "study_hours": 4,
            "journal_text": "Testing Inf"
        }
        response = self.client.post('/assessment/',
                                    data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Input values must be finite numbers.", response.data)

    def test_negative_inf_rejection(self):
        payload = {
            "sleep_hours": float('-inf'),
            "sleep_quality": 3,
            "stress_level": 3,
            "academic_pressure": 3,
            "mood": 3,
            "energy_level": 3,
            "social_interaction": 3,
            "exercise_minutes": 30,
            "screen_time": 2,
            "study_hours": 4,
            "journal_text": "Testing -Inf"
        }
        response = self.client.post('/assessment/',
                                    data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Input values must be finite numbers.", response.data)

    def test_daily_24h_violation(self):
        # 10 + (60/60) + max(14, 14) = 10 + 1 + 14 = 25 > 24
        payload = {
            "sleep_hours": 10,
            "sleep_quality": 3,
            "stress_level": 3,
            "academic_pressure": 3,
            "mood": 3,
            "energy_level": 3,
            "social_interaction": 3,
            "exercise_minutes": 60,
            "screen_time": 14,
            "study_hours": 14,
            "journal_text": "Testing 24h violation"
        }
        response = self.client.post('/assessment/',
                                    data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"exceeds 24 hours", response.data)

    @patch('app.assessment.routes.predict_depression')
    @patch('app.assessment.routes.predict_nlp_risk')
    @patch('app.assessment.routes.generate_recommendations')
    def test_valid_entry(self, mock_rec, mock_nlp, mock_pred):
        # 8 + (0/60) + max(12, 13) = 8 + 13 = 21 <= 24
        mock_pred.return_value = ("Normal", 0.1)
        mock_nlp.return_value = {"valid": True, "risk_score": 0.05, "validation": {"is_meaningful": True}}
        mock_rec.return_value = ["Keep it up"]

        payload = {
            "sleep_hours": 8,
            "sleep_quality": 3,
            "stress_level": 3,
            "academic_pressure": 3,
            "mood": 3,
            "energy_level": 3,
            "social_interaction": 3,
            "exercise_minutes": 0,
            "screen_time": 13,
            "study_hours": 12,
            "journal_text": "Testing valid entry"
        }
        response = self.client.post('/assessment/',
                                    data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn(b"Assessment submitted successfully", response.data)

if __name__ == '__main__':
    unittest.main()
