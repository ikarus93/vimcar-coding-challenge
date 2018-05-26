#!flask/bin/python
from db.dbConfig import get_db, query_db 
from flask import Flask, request, jsonify, g, session
from flask_mail import Mail, Message
from misc.config import app_secret, mail_username, mail_password
from misc.helpers import verify_email, send_error_message
from misc.decorators import login_required
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = app_secret

'''Config for flask-mail'''
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = mail_username
app.config['MAIL_PASSWORD'] = mail_password
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)  #Creating instance of Mail


@app.route('/auth/signup', methods=["POST"])
def signup():
    '''
    User signs up, given that the required parameters (email, password) are embedded into the request body.
    Hashes password, saves new User to users.db.
    Should return JSON response with status 200
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
        query_db("INSERT INTO users(email, password, verified) VALUES(?, ?, ?)", ( email, hashed_pw, 0 ), g) 
        
        user_id = query_db("SELECT ID FROM users WHERE email=?", (email, ), g)[0]["ID"]
        mail_link = "https://vimcar-coding-challenge-atheos.c9users.io/verify?id={id}".format(id = user_id)
        
        msg = Message("Welcome", sender = mail_username, recipients = [email])
        msg.body = "Please verify your email by clicking on the following Link\n{link}".format(link = mail_link)
        #mail.send(msg)
        
        #added mail link to response data for integration test purposes
        return jsonify(message="You've signed up successfully. Please validate your email address by clicking on the link we've sent you.", data=[dict(link = mail_link)]), 200
        
    except Exception as e:
        return send_error_message(str(e))


@app.route('/verify')
def verify():
    ''' Route that extracts user id from query string and lets user verify his email address '''
    try:
        user_id = request.args.get("id")
        db = get_db("users.db", g)
        if db is None:
            raise Exception("500") # Exception 500 - Internal Server/Database Error
        
        status = query_db("SELECT VERIFIED FROM users WHERE id = ?", (user_id, ), g)
        if not len(status):
            raise Exception("404")  # Exception 404: Resource not found (user_id is invalid)
        
        if status[0]["VERIFIED"] == 1:
            return jsonify(message="You've already verified your email.", data=[]), 200
        
        query_db("UPDATE users SET VERIFIED = 1 WHERE id = ?", (user_id, ), g)
        return jsonify(message="You've now been verified. Enjoy using our service", data=[]), 200
    
    except Exception as e:
        print(e)
        return send_error_message(str(e))
    
@app.route('/auth/login', methods=["POST"])
def login():
    ''' Route that logs in user,
        Expects two values in Request Body - email and password
        Checks Email for validity by querying database, then if valid - compares given password with password hash from db query
        Should return JSON response with status code 200
    '''
    try:
        session.clear()   #clear any open sessions to maintain a clean session state
        
        email = request.form.get("email")
        password = request.form.get("password")
        if not email or not password:
            raise Exception("422")  # Exception 422 - Unprocessable Entity
            
        db = get_db("users.db", g)
        if db is None:
            raise Exception("500") # Exception 500 - Internal Server/Database Error
        
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
