from flask import Blueprint, request, render_template, redirect, url_for, session
from .utils import upload_data_to_server
from requests_oauthlib import OAuth2Session
import os
import uuid

app_routes = Blueprint('app_routes', __name__)


# Duke OATH URLs
# TODO: Make sure these are correct and secure
DUKE_AUTHORIZATION_BASE_URL = 'https://oauth.oit.duke.edu/oidc/authorize'
DUKE_REDIRECT_URI = 'https://127.0.0.1:5000/auth'
DUKE_TOKEN_URL = 'https://oauth.oit.duke.edu/oidc/token'
DUKE_USERINFO_URL = 'https://oauth.oit.duke.edu/oidc/userinfo'
DUKE_LOGOUT_URL = 'https://oauth.oit.duke.edu/oidc/logout.jsp'

DUKE_CLIENT_ID = os.getenv('DUKE_CLIENT_ID','')
DUKE_CLIENT_SECRET = os.getenv('DUKE_CLIENT_SECRET','')


@app_routes.route('/')
def index():
    return render_template('upload.html')

@app_routes.route('/upload', methods=['POST'])
def upload_file():
    name = request.form['name']
    subject = request.form['subject']

    if 'file' not in request.files:
        return render_template('upload.html', message='No file part. Please try again.')

    file = request.files['file']

    if file.filename == '':
        return render_template('upload.html', message='No selected file. Please try again.')

    if file:
        if upload_data_to_server(file, name, subject):
            return render_template('upload.html', message='Thank you for contributing')
        else:
            return render_template('upload.html', message='Something went wrong. Please try again.')

   
@app_routes.route('/sso', methods=['GET'])
def sso_login():
    responseType = 'code'
    
    client_id = DUKE_CLIENT_ID
    client_secret = DUKE_CLIENT_SECRET
    authorization_base_url = DUKE_AUTHORIZATION_BASE_URL
    redirect_uri = DUKE_REDIRECT_URI

    state = str(uuid.uuid4())
    SSO = OAuth2Session(client_id = client_id, state=state, redirect_uri=redirect_uri)
    authorization_url, state = SSO.authorization_url(authorization_base_url)
    session['oath_state'] = state
    return redirect(authorization_url)

@app_routes.route('/auth', methods=['GET'])
def duke_auth():
    expected_state = session['oath_state']
    state = request.args.get('state', None)
    if state != expected_state:
        return redirect(url_for("sso_login"))
    
    # Get correct token url and redirect uri for Duke
    
    token_url = DUKE_TOKEN_URL
    redirect_uri = DUKE_REDIRECT_URI
    responseType = 'code'
    client_id = DUKE_CLIENT_ID
    client_secret = DUKE_CLIENT_SECRET
    
    # get user info from the SSO
    SSO = OAuth2Session(client_id = client_id, state=state, redirect_uri=redirect_uri)
    response_url = request.url  
    if "http:" in response_url:
        response_url = "https:" + response_url[5:]
    token = SSO.fetch_token(token_url, client_secret=client_secret, authorization_response=response_url)
    session['oath_token'] = token
    userInfo = SSO.get(DUKE_USERINFO_URL)
    userInfo = userInfo.json()
    email = userInfo['email']
    email = email.lower().strip()
    print(email)
    session['usr'] = email

    # Remove university and status from session
    # session.pop('university_sso')
    # session.pop('status_sso')

    # if 'course' in session:
    #     session.pop('course')

    return redirect(url_for("index"))