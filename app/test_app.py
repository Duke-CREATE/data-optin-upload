# create dummy test function
from app import create_app
from flask import Flask
def test_app():
    app = create_app()
    # write test to check if app is running and html returned from endpoint
    with app.test_client() as test_client:
        response = test_client.get('/')
        assert response.status_code == 200
        assert b'Name' in response.data
        assert b'Subject' in response.data
        assert b'File' in response.data
        assert b'Upload' in response.data
