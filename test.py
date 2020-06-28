from base64 import b64encode

from app.app import app
import unittest
import json


class FlaskTestCase(unittest.TestCase):
    # TODO test cases for good scenario

    def test_register(self):
        tester = app.test_client(self)
        response = tester.post('/register')
        self.assertEqual(response.status_code, 200)

    def test_register_used_un(self):
        tester = app.test_client(self)
        credentials = b64encode(b"bob:bob").decode('utf-8')
        response = tester.post('/register', headers={"Authorization": f"Basic {credentials}"})
        json_resp = json.loads(response.data)
        self.assertEqual(json_resp['message'], 'USERNAME IS IN USE')

    def test_register_no_un(self):
        tester = app.test_client(self)
        credentials = b64encode(b":bob").decode('utf-8')
        response = tester.post('/register', headers={"Authorization": f"Basic {credentials}"})
        json_resp = json.loads(response.data)
        self.assertEqual(json_resp['message'], 'USERNAME MUST BE NON-EMPTY')

    def test_register_no_pw(self):
        tester = app.test_client(self)
        credentials = b64encode(b"bob:").decode('utf-8')
        response = tester.post('/register', headers={"Authorization": f"Basic {credentials}"})
        json_resp = json.loads(response.data)
        self.assertEqual(json_resp['message'], 'PASSWORD MUST BE NON-EMPTY')

    def test_register_no_cred(self):
        tester = app.test_client(self)
        credentials = b64encode(b"").decode('utf-8')
        response = tester.post('/register', headers={"Authorization": f"Basic {credentials}"})
        json_resp = json.loads(response.data)
        self.assertEqual(json_resp['message'], 'CREDENTIAL DETAILS REQUIRED')

    def test_login(self):
        tester = app.test_client(self)
        response = tester.post('/login')
        self.assertEqual(response.status_code, 200)

    def test_login_no_cd(self):
        tester = app.test_client(self)
        credentials = b64encode(b"").decode('utf-8')
        response = tester.post('/login', headers={"Authorization": f"Basic {credentials}"})
        json_resp = json.loads(response.data)
        self.assertEqual(json_resp['message'], 'CREDENTIAL DETAILS REQUIRED')

    def test_login_no_login(self):
        tester = app.test_client(self)
        credentials = b64encode(b"sdsd:sdsdds").decode('utf-8')
        response = tester.post('/login', headers={"Authorization": f"Basic {credentials}"})
        json_resp = json.loads(response.data)
        self.assertEqual(json_resp['message'], 'INVALID LOGIN OR PASSWORD')


if __name__ == '__main__':
    unittest.main()
