# create dummy test function
import app
from flask import Flask
def test_app():
    # write test to check if app is running and html returned from endpoint
    with app.test_client() as test_client:
        response = test_client.get('/')
        assert response.status_code == 200
        assert b'File Upload Form' in response.data
        assert b'Name' in response.data
        assert b'Subject' in response.data
        assert b'File' in response.data
        assert b'Upload' in response.data
        assert b'No file part. Please try again.' not in response.data
        assert b'No selected file. Please try again.' not in response.data
        assert b'Thank you for contributing' not in response.data
        assert b'Something went wrong. Please try again.' not in response.data

