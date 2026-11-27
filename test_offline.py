import unittest
from pathlib import Path
import graphing_calc as calculator
import FinCalc

class AlgebraTests(unittest.TestCase):
    def setUp(self):
        calculator.functions_store.clear()
        calculator.app.config['TESTING'] = True
        self.client = calculator.app.test_client()

    def test_page_uses_browser_chart_bundle(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'chart.umd.min.js', response.data)
        self.assertIn('chart.umd.min.js', Path(__file__).with_name('graphing_calc.py').read_text())

    def test_function_and_quadratic(self):
        self.assertTrue(self.client.post('/api/add_function', json={'expression':'x^2'}).json['success'])
        result = self.client.post('/api/solve_quadratic', json={'a':1, 'b':-3, 'c':2}).json
        self.assertEqual(sorted(result['results']['roots']), [1, 2])

    def test_zero_interest_mortgage(self):
        self.assertAlmostEqual(FinCalc.mortgage_monthly_payment(100000, 0, 10), 100000/120)

if __name__ == '__main__':
    unittest.main()
