from flask import Flask
from .views import router

app = Flask(__name__, static_folder='static')

app.register_blueprint(router)
