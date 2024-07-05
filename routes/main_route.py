from flask import render_template
from . import main_bp
from reg.models import db, User

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/search')
def search():
    return render_template('search.html')

@main_bp.route('/player', methods=['GET', 'POST'])
def player():
    if request.method == 'POST':
        # Handle POST request logic here
        pass
    return render_template('player.html')
