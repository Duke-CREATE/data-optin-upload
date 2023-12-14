# create dummy test function
import app
from flask import Flask
def test_app():
    # assert that the app is a flask instance
    assert isinstance(app, Flask)
