import unittest
import os

from app import tasks
from app import create_app



class TestPredictionMethods(unittest.TestCase):

    ### get_quantile_score tests

    def test_very_small_score(self):
        prediction_result = -20.0
        score = tasks.get_quantile_score(prediction_result)
        self.assertEqual(score, 0.1)

    def test_big_score(self):
        prediction_result = 20.0
        score = tasks.get_quantile_score(prediction_result)
        self.assertEqual(score, 10.0)

    def test_minus_seven_first(self):
        prediction_result = -7.0
        score = tasks.get_quantile_score(prediction_result, "first")
        self.assertEqual(score, 0.2)

    def test_minus_seven_pref(self):
        prediction_result = -7.0
        score = tasks.get_quantile_score(prediction_result, "pref")
        self.assertEqual(score, 0.1)


class TestFlaskMethods(unittest.TestCase):

    def setUp(self):
        self.app = create_app(os.getenv('FLASK_CONFIG') or 'default').test_client()

    def test_flask(self):
        rv = self.app.get('/')
        assert '@' in rv.data



if __name__ == '__main__':
    unittest.main()