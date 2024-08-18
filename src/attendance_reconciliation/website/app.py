from attendance_reconciliation.generic.web_server import app
from flask import render_template, url_for, redirect, flash, request, jsonify, session
import structlog
import requests
from flask_cors import CORS
from functools import wraps

CORS(app)


app.config['SECRET_KEY'] = 'kwVYKHCvT!eA7yvK'
CONTENT_TYPE_APPLICATION_JSON = "application/json"

logger = structlog.getLogger(__name__)
base_url = ''
# Helper function to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            return redirect(url_for('login_panel'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def login_panel():
    return render_template('login.html')

def unauthorized_count():
    url = f'{base_url}/unauthorized_access'
    headers = {
        "Authorization": f"Bearer {session.get('token')}"
    }
    response = requests.get(url, headers=headers).json()
    return len(response)

@app.route('/login', methods=['POST'])
def login_authentication():
    username = request.form['username']
    password = request.form['password']

    url = f'{base_url}/secured/users/login'
    data = {'username': username, 'password': password}
    response = requests.post(url, json=data)

    if response.status_code == 200:
        token = response.json().get('accessToken')
        session['token'] = token  # Store token in session
        return redirect(url_for('home'))
    else:
        flash('Invalid credentials, please try again.')
        return redirect(url_for('login_panel'))

@app.route('/logout')
def logout():
    session.pop('token', None)  # Remove token from session
    return redirect(url_for('login_panel'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html',unauthcount=unauthorized_count())

@app.route('/employee')
@login_required
def employees():
    return render_template('employees.html',unauthcount=unauthorized_count(),url=base_url,token=session.get('token'))

@app.route('/attendances')
@login_required
def attendance():
    return render_template('attendance.html',unauthcount=unauthorized_count(),url=base_url,token=session.get('token'))

@app.route('/users')
@login_required
def users():
    return render_template('users.html',unauthcount=unauthorized_count(),url=base_url,token=session.get('token'))

@app.route('/wfh_employees')
@login_required
def wfh_employees():
    return render_template('wfh_employees.html',unauthcount=unauthorized_count(),url=base_url,token=session.get('token'))

@app.route('/devices')
@login_required
def devices():
    return render_template('devices.html',unauthcount=unauthorized_count(),url=base_url,token=session.get('token'))

@app.route('/unauthorized_users')
@login_required
def unauthorized_users():
    return render_template('unauthorized_users.html',unauthcount=unauthorized_count(),url=base_url,token=session.get('token'))

def initialize_website_server(baseUrl):
    global base_url
    base_url = baseUrl
    logger.info(f"Website started at {base_url}")
