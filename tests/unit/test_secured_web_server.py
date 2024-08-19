import unittest
from flask import json
from attendance_reconciliation.generic.secured_web_server import app

class TestSecuredWebServer(unittest.TestCase):
    def setUp(self):
        """Set up the test client and other necessary components."""
        self.app = app
        self.client = self.app.test_client()
        self.client.testing = True
    
    def test_get_user_details_success(self):
        """Test that the endpoint returns user details successfully with a valid token."""
        # Use a valid token or mock the authentication
        valid_token = 'valid_token'
        response = self.client.get('/secured/users', headers={'Authorization': f'Bearer {valid_token}'})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIsInstance(data, list)  # Assuming the endpoint returns a list of users
        self.assertGreater(len(data), 0)  # Assuming there should be at least one user
    
    def test_get_user_details_unauthorized(self):
        """Test that the endpoint returns 401 Unauthorized with an invalid token."""
        invalid_token = 'invalid_token'
        response = self.client.get('/secured/users', headers={'Authorization': f'Bearer {invalid_token}'})
        self.assertEqual(response.status_code, 401)
    
    def test_post_user_success(self):
        """Test that the endpoint successfully creates a user with valid data."""
        valid_token = 'valid_token'
        new_user = {
            'name': 'John Doe',
            'email': 'john.doe@example.com'
        }
        response = self.client.post('/secured/users', 
                                    headers={'Authorization': f'Bearer {valid_token}'},
                                    data=json.dumps(new_user),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'John Doe')
        self.assertEqual(data['email'], 'john.doe@example.com')
    
    def test_post_user_bad_request(self):
        """Test that the endpoint returns 400 Bad Request when required data is missing."""
        valid_token = 'valid_token'
        invalid_user = {}  # Missing required fields
        response = self.client.post('/secured/users', 
                                    headers={'Authorization': f'Bearer {valid_token}'},
                                    data=json.dumps(invalid_user),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    def tearDown(self):
        """Clean up any resources or state after each test."""
        pass  # Add cleanup code if needed

if __name__ == '__main__':
    unittest.main()
