from flask import Blueprint, request, render_template

default = Blueprint('default', __name__)

@default.route('/')
def index():
    return render_template('index.html')  