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
        self.assertEqual(json.loads(response.get_data().decode())['message'], "You've signed up successfully. Please validate your email address by clicking on the link we've sent you.")
    
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
        '''
        Test Case for valid Login request
        Expected status code: 200
        '''
        response = self.app.post('auth/login', data=dict(email = self.email, password = self.password))
        
        assert(response.status_code == 200)
        self.assertEqual(json.loads(response.get_data().decode()), {'message': "You are now logged in", 'data': []})
        
    def test_login_invalid_password(self):
        '''
        Test Case for invalid password supplied
        Expected status code: 401
        '''
        response = self.app.post('auth/login', data=dict(email = self.email, password = "randomString"))
        
        assert(response.status_code == 401)
        self.assertEqual(json.loads(response.get_data().decode()), {'message': "Not Authorized", 'data': []})
    
    def test_login_invalid_email(self):
        '''
        Test Case for invalid email supplied/mistyped email address
        Expected status code: 404
        '''
        response = self.app.post('auth/login', data=dict(email = "randomemailstring@randomemail.com", password = self.password))
        
        assert(response.status_code == 404)
        self.assertEqual(json.loads(response.get_data().decode()), {'message': "Not found", 'data': []})
    
    def test_missing_request_parameters(self):
        '''
        Tests appropriate error message for missing request parameters (email, password)
        Expected status code: 422
        '''
        #password is not supplied
        response = self.app.post('/auth/login', data=dict(email=generate_pseudo_random_email()))
        #email is not supplied
        second_response =  self.app.post('/auth/login', data=dict(password="email-is-missing-in-action"))
        
        assert(response.status_code == 422) 
        assert(second_response.status_code == 422)
        self.assertEqual(json.loads(response.get_data().decode()), {'message': "Unprocessable Entity", 'data': []})
        self.assertEqual(json.loads(second_response.get_data().decode()), {'message': "Unprocessable Entity", 'data': []})



class TestSessionHandling(TestCase):
    ''' Tests APIs Session Handling, logout functionality and access of protected routes '''
    def setUp(self):
        self.app = app.test_client()
        self.email = generate_pseudo_random_email()
        self.password = "1234test"
        self.app.post('/auth/signup', data=dict(email=self.email, password=self.password))
        self.app.post('auth/login', data=dict(email=self.email, password=self.password))
    
    def test_access_of_protected_route(self):
        '''
        Should be able to access protected route, as user is logged in in setUp
        Expected status code: 200
        '''
        
        response = self.app.get('/mock/protected')
        
        assert(response.status_code == 200)
        self.assertEqual(json.loads(response.get_data().decode()), {'message': "Success!!!! You are now viewing a protected route...this must mean you are logged in ;)", 'data': [{"The answer to life, the universe and everything": 42}]})

    def test_logout_and_protection_of_route(self):
        '''
        Should be able to log user out and to protect route if a session doesn't exist
        Expected status codes: 200 (for logout request), 401 (for failed session access)
        '''
        
        logout_response = self.app.get('/auth/logout')
        assert(logout_response.status_code == 200)
        
        protected_route_response = self.app.get('/mock/protected')
        assert(protected_route_response.status_code == 401)


class TestEmailVerification(TestCase):
    ''' Tests output and validity of email verification process '''
    
    def setUp(self):
        self.app = app.test_client()
        response = self.app.post('/auth/signup', data=dict(email=generate_pseudo_random_email(), password="1234Test"))
        self.mail_link = json.loads(response.get_data().decode())["data"][0]["link"]
    
    def test_verification_works(self):
        '''
        Tests if verification works as it should
        Expected status code: 200
        '''
        uri = self.mail_link.split("/")[-1]
        response = self.app.get(uri)
        
        assert(response.status_code == 200)
        
    def test_verification_error_on_invalid_id(self):
        '''
        Tests if verification rejects invalid id
        Expected status code: 404
        '''
        response = self.app.get('/verify?id=invalidId')
        
        assert(response.status_code == 404)

if __name__ == "__main__":
    main()