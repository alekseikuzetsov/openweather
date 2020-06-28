from app import app
import unittest

class FlaskTestCase(unittest.TestCase):

    def test_register(self):
        tester = app.test_client(self)
        response = tester.post('/register')
        self.assertEqual(response.status_code, 200)