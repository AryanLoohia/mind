from flask import Blueprint

main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
assessment_bp = Blueprint('assessment', __name__)

from . import main_routes, auth_routes, assessment_routes
