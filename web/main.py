from flask import Blueprint
from . import db
from .models import *
from flask import Blueprint, render_template
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return 'Index'

# @main.route('/profile')
# def profile():
#     return 'Profile'

@main.route("/da_list")
@login_required
def da_list():
    agents = DeliveryAgent.query.all()
    return render_template('da_list.html', agents=agents)