#!flask/bin/python
import os
from flask import Flask, request, jsonify, g, session
from werkzeug.security import generate_password_hash, check_password_hash
from db.dbConfig import get_db, query_db 
from misc.config import app_secret
from misc.helpers import verify_email, send_error_message
from misc.decorators import login_required
import sqlite3


app = Flask(__name__)
app.secret_key = app_secret

@app.route('/auth/signup', methods=["POST"])
def signup():
    '''
    User signs up, given that the required parameters (email, password) are embedded into the request body.
    Hashes password, saves new User to users.db.
    Should return Json response with status 200
    '''
    try:
        email = request.form.get("email")
        password = request.form.get("password")
        if not email or not password or not verify_email(email):
            raise Exception("422") # Exception 422 - Unprocessable Entity
        
        db = get_db("users.db", g)
        if db is None:
            raise Exception("500") # Exception 500 - Internal Server/Database Error
        
        already_exists = query_db("SELECT * FROM users WHERE email=?", (email, ), g)
        if already_exists:
            raise Exception("409") # Exception 409 - Conflict - The Email is already registered
            
        hashed_pw = generate_password_hash(password)
        query_db("INSERT INTO users(email, password) VALUES(?, ?)", ( email, hashed_pw ), g) 
        
        return jsonify(message="You've signed up successfully. Please validate your email address by clicking on the link we've sent you.", data=[]), 200
        
    except Exception as e:
        return send_error_message(str(e))
    
    
@app.route("/auth/login", methods=["POST"])
def login():
    try:
        session.clear()
        
        email = request.form.get("email")
        password = request.form.get("password")
        
        if not email or not password:
            raise Exception("422")  # Exception 422 - Unprocessable Entity
        db = get_db("users.db", g)
        result = query_db("SELECT * FROM users WHERE email=?", (email, ), g)
        if not len(result):
            raise Exception("404") # Exception 404 - Resource not found (Email is not signed up for service)
        
        if not check_password_hash(result[0]["PASSWORD"], password):
            raise Exception("401") # Exception 401 - Not authorized (Wrong password)
        
        session["user_id"] = email
        return jsonify(message="You are now logged in", data=[]), 200
        
    except Exception as e:
        return send_error_message(str(e))

@app.route("/mock/protected")
@login_required
def protected_mock_route():
    '''Protected "mock" route to test session API'''
    return jsonify(message="Success!!!! You are now viewing a protected route...this must mean you are logged in ;)", data=[{"The answer to life, the universe and everything": 42}]), 200

@app.route("/auth/logout")
def logout():
    '''Deletes session to log user out'''
    session.clear()
    return jsonify(message="Logged out successfully", data=[]), 200


@app.teardown_appcontext
def close_connection(exception):
    '''Closes database connection on app teardown as specified per docs - http://flask.pocoo.org/docs/0.12/patterns/sqlite3/
    '''
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'),port=8080)
