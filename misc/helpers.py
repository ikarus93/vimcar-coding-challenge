from flask import jsonify
from .exceptionsMap import exceptions
import re
import time
import json



def verify_email(email):
    '''
    Verifys if the supplied email address is indeed valid - conforming to RFC 5322 Official Standard
    
    Takes Parameters: email(type="string") == the users email
    Returns: True or False depending on regex outcome
    '''
    return re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email) is not None

def send_error_message(status):
    '''
    handles different errors and maps them to the respective exception text
    
    Takes parameters: status(type="string") == the http status code of the error
    Returns: json response for request
    '''
    if status not in exceptions:
        #Edge case regarding arbitrary internal flask error --> set it to status code for internal server error
        status = "500"
    return jsonify(message=exceptions[status], data=[]), int(status)


def generate_pseudo_random_email():
    '''
    Generates pseudo random email address for integration tests, based on current Unix Timestamp (to assure randomness in testing approach)
    
    Returns: email(type="string") == generated email address
    '''
    timestamp = time.time()
    return "{timestamp}@test.com".format(timestamp = timestamp)
