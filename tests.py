'''Integration Tests'''

from app import app
from unittest import TestCase, main
import json
from misc.helpers import generate_pseudo_random_email

class TestSignup(TestCase):
    ''' Tests signup process '''
    def setUp(self):
        self.app = app.test_client()

    def test_user_signup(self):
        ''' 
        Test Case for valid email signup 
        Expected status code: 200
        '''
        response = self.app.post('/auth/signup', data=dict(email=generate_pseudo_random_email(), password="1234test"))
        assert(response.status_code == 200)
        self.assertEqual(json.loads(response.get_data().decode()), {'message': "You've signed up successfully. Please validate your email address by clicking on the link we've sent you.", 'data': []})
    
    def test_user_signup_with_duplicate(self):
        ''' 
        Tests appropriate error message for duplicate email signup 
        Expected status code: 409
        '''
        email = generate_pseudo_random_email()
        self.app.post('/auth/signup', data=dict(email=email, password="1234test"))
        response = self.app.post('/auth/signup', data=dict(email=email, password="1234test"))
        assert(response.status_code == 409)  
        self.assertEqual(json.loads(response.get_data().decode()), {'message': "Conflict - The Email already exists", 'data': []})

    def test_missing_request_parameters(self):
        '''
        Tests appropriate error message for missing request parameters (email, password)
        Expected status code: 422
        '''
        #password is not supplied
        response = self.app.post('/auth/signup', data=dict(email=generate_pseudo_random_email()))
        #email is not supplied
        second_response =  self.app.post('/auth/signup', data=dict(password="email-is-missing-in-action"))
        
        assert(response.status_code == 422) 
        assert(second_response.status_code == 422)
        self.assertEqual(json.loads(response.get_data().decode()), {'message': "Unprocessable Entity", 'data': []})
        self.assertEqual(json.loads(second_response.get_data().decode()), {'message': "Unprocessable Entity", 'data': []})


class TestLogin(TestCase):
    ''' Tests login functionality '''
    def setUp(self):
        self.app = app.test_client()
        self.email = generate_pseudo_random_email()
        self.password = "1234test"
        self.app.post('/auth/signup', data=dict(email=self.email, password = self.password))
    
    def test_login_works(self):
        
        response = self.app.post('auth/login', data=dict(email = self.email, password = self.password))
        
        assert(response.status_code == 200)
        self.assertEqual(json.loads(response.get_data().decode()), {'message': "You are now logged in", 'data': []})




if __name__ == "__main__":
    main()