from flask import Blueprint, request, render_template, redirect, url_for, session
from .utils import upload_data_to_server
from requests_oauthlib import OAuth2Session
import os
import uuid

app_routes = Blueprint('app_routes', __name__)


# Duke OATH URLs
DUKE_AUTHORIZATION_BASE_URL = 'https://oauth.oit.duke.edu/oidc/authorize'
DUKE_REDIRECT_URI = 'https://duke-data-donation.azurewebsites.net/auth'
DUKE_TOKEN_URL = 'https://oauth.oit.duke.edu/oidc/token'
DUKE_USERINFO_URL = 'https://oauth.oit.duke.edu/oidc/userinfo'
DUKE_LOGOUT_URL = 'https://oauth.oit.duke.edu/oidc/logout.jsp'

DUKE_CLIENT_ID = os.getenv('DUKE_CLIENT_ID','')
DUKE_CLIENT_SECRET = os.getenv('DUKE_CLIENT_SECRET','')



@app_routes.route('/login', methods=['GET'])
def loginpage():
    return render_template('login.html')

@app_routes.route('/')
def index():
    '''
    This route renders the home page if the user is logged in
    routes to the login page if the user is not logged in
    '''
    if 'usr' in session:
        return render_template('upload.html', user=session['usr'])
    else:
        return redirect(url_for('app_routes.loginpage'))

# Uncomment this route to enable offline testing - useful for development without SSO
# @app_routes.route('/offlinetesting', methods=['GET'])
# def offlinetesting():
#     '''
#     FOR TESTING PURPOSES ONLY! Circumvents SSO and logs in a test user
#     '''
#     session['usr'] = 'testuser'
#     session['user_info'] = {'name': 'test', 'dukeNetID': 'test123', 'email': 'test@test', 'dukePrimaryAffiliation': 'tester'}
#     return render_template('upload.html', user=session['usr'])

@app_routes.route('/upload', methods=['POST'])
def upload_file():
    '''
    This route handles the file upload and metadata storage
    '''
    name = session['user_info']['name']
    primaryAffiliation = session['user_info']['dukePrimaryAffiliation']
    netid = session['user_info']['dukeNetID']
    subject = request.form['subject']
    print(f"Uploading file for {name} ({netid})"
            f" with primary affiliation {primaryAffiliation} and subject {subject}")

    if 'file' not in request.files:
        return render_template('upload.html', message='No file part. Please try again.')

    file = request.files['file']

    if file.filename == '':
        return render_template('upload.html', message='No selected file. Please try again.')

    elif not file.filename.endswith(('.pdf')):
        return render_template('upload.html', message='Invalid file type. Please upload a .pdf file.')
    
    elif file:
        if upload_data_to_server(file, name, netid, primaryAffiliation, subject):
            return render_template('upload.html', message='Thank you for contributing')
        else:
            return render_template('upload.html', message='Something went wrong. Please try again.')

   
@app_routes.route('/dukesso', methods=['GET'])
def sso_login():   
    '''
    This route redirects the user to the Duke SSO login page
    '''
    responseType = 'code'
    client_id = DUKE_CLIENT_ID
    authorization_base_url = DUKE_AUTHORIZATION_BASE_URL
    redirect_uri = DUKE_REDIRECT_URI
    client_secret = DUKE_CLIENT_SECRET

    state = str(uuid.uuid4())
    SSO = OAuth2Session(client_id = client_id, state=state, redirect_uri=redirect_uri)
    authorization_url, state = SSO.authorization_url(authorization_base_url)
    session['oath_state'] = state
    return redirect(authorization_url)

@app_routes.route('/auth', methods=['GET'])
def duke_auth():
    '''
    This route handles the Duke SSO authentication and redirects the user to the home page
    '''
    expected_state = session['oath_state']
    state = request.args.get('state', None)
    if state != expected_state:
        print(f"State does not match: {state} | {expected_state}" )
        return redirect(url_for('app_routes.loginpage'))
    
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
    # Get user info
    userInfo = SSO.get(DUKE_USERINFO_URL)
    userInfo = userInfo.json()
    email = userInfo['email']
    email = email.lower().strip()
    user_info = userInfo
    name = userInfo['name']
    primaryAffiliation = userInfo['dukePrimaryAffiliation']
    netid = userInfo['dukeNetID']

    session['usr'] = f'{name} ({netid})'
    session['user_info'] = user_info

    return redirect(url_for('app_routes.index'))