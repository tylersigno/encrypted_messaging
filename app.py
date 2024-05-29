'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''

from flask import Flask, redirect, render_template, request, abort, session, url_for, jsonify
from flask_socketio import SocketIO
import db
import secrets
import bleach
import os
import ssl
import bcrypt
from datetime import timedelta  
from functools import wraps 

# import logging

# this turns off Flask Logging, uncomment this to turn off Logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

app = Flask(__name__)

# secret key used to sign the session cookie
app.config['SECRET_KEY'] = secrets.token_hex()

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_COOKIE_SECURE'] = True  
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

socketio = SocketIO(app)

current_directory = os.path.dirname(__file__)

cert_path = os.path.join(current_directory, 'mydomain.crt')
key_path = os.path.join(current_directory, 'mydomain.key')

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(cert_path, keyfile=key_path)

# don't remove this!!
import socket_routes

# index page
@app.route("/")
def index():
    return render_template("index.jinja")

# login page
@app.route("/login")
def login():    
    return render_template("login.jinja")

# handles a post request when the user clicks the log in button
@app.route("/login/user", methods=["POST"])
def login_user():
    if not request.is_json:
        abort(404)

    username = bleach.clean(request.json.get("username"))
    password = bleach.clean(request.json.get("hashedpassword"))

    user =  db.get_user(username)
    if user is None:
        return "Error: User does not exist!"

    if bcrypt.checkpw(password.encode('utf-8'), user.password):
        session.clear()
        session['username'] = username
        # return url_for('home', username=request.json.get("username")) 
        return url_for('home')
    else:
        return "Error: Password does not match!"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/logout")
def logout():
    session.pop('username', None)
    session.clear()
    response = redirect(url_for('index'))
    response.headers['Clear-Site-Data'] = '"cookies"'
    return response

# handles a get request to the signup page
@app.route("/signup")
def signup():
    return render_template("signup.jinja")

# handles a post request when the user clicks the signup button
@app.route("/signup/user", methods=["POST"])
def signup_user():
    if not request.is_json:
        abort(404)
    username = bleach.clean(request.json.get("username"))
    password = bleach.clean(request.json.get("hashedpassword"))

    if db.get_user(username) is None:
        hashedpwd = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        db.insert_user(username, hashedpwd)
        session.clear()
        session['username'] = username
        return url_for('home', username=username)
    return "Error: User already exists!"

# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404

# home page, where the messaging app is
@app.route("/home")
@login_required
def home():
    # username = request.args.get("username")
    username = session.get('username') 
    if username is None:
        abort(404)
        

    friends = db.get_friends(username)
    return render_template("home.jinja", username=username, friends=friends)


@app.route("/send_friend_request", methods=["POST"])
@login_required
def send_friend_request():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    user_id = bleach.clean(request.json.get("user_id"))
    friend_id = bleach.clean(request.json.get("friend_id")) 

    if db.get_user(user_id) is None:
        return jsonify({"error": "User does not exist"}), 404


    if db.get_user(friend_id) is None:
        return jsonify({"error": "Friend user does not exist"}), 404

    if db.is_friend(user_id, friend_id):
        return jsonify({"error": "You are already friends"}), 400

    db.send_friend_request(user_id, friend_id, status="pending")

    socketio.emit('sent_friend_request')

    return jsonify({"message": "Friend request sent successfully"}), 200



@app.route("/friend_requests", methods=["GET"])
@login_required
def view_friend_requests():
    user_id = request.args.get("user_id")
    if user_id is None:
        return jsonify({"error": "User ID is required"}), 400

    requests = db.get_friend_requests(user_id)
    return jsonify([{"user_id": req.user_id, "friend_id": req.friend_id, "status": req.status} for req in requests]), 200

@app.route("/sent_friend_requests", methods=["GET"])
def view_sent_friend_requests():
    user_id = request.args.get("user_id")
    if user_id is None:
        return jsonify({"error": "User ID is required"}), 400

    requests = db.get_sent_friend_requests(user_id)
    return jsonify([{"user_id": req.user_id, "friend_id": req.friend_id, "status": req.status} for req in requests]), 200


@app.route("/respond_friend_request", methods=["POST"])
def respond_friend_request():
    if not request.is_json:
        abort(400, description="Request must be JSON")

    user_id = bleach.clean(request.json.get("user_id"))
    friend_id = bleach.clean(request.json.get("friend_id"))
    response = bleach.clean(request.json.get("response"))  # should be "accept" or "reject"

    if response not in ["accept", "reject"]:
        return jsonify({"error": "Invalid response"}), 400

    status = "accepted" if response == "accept" else "rejected"
    db.update_friend_request_status(friend_id, user_id, status)
    return jsonify({"message": f"Friend request {response}ed"}), 200

@app.route("/verify_password", methods=["POST"])
def verify_password():
    data = request.json
    username = data['username']
    password = data['password']

    user = db.get_user(username)
    if user is not None and bcrypt.checkpw(password.encode('utf-8'), user.password):
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False}), 401

@app.after_request
def add_security_headers(response):
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=8080, ssl_context=context)

