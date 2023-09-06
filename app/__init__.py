from flask import Flask
from .views import router

app = Flask(__name__)

app.register_blueprint(router)
