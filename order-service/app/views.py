from flask import Blueprint, render_template
from flask import send_from_directory

router = Blueprint('router', __name__)


@router.route('/')
def index():
    return render_template('index.html')

@router.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@router.route('/static')
def indexx():
    return render_template('index.html')