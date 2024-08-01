from flask import Flask

app = Flask(__name__)

app.app_context().push()

from app import views