from flask import Blueprint, render_template,redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from .models import *
from . import db, bcrypt
from flask import Flask, render_template
from .forms import RegistrationForm

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')    
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, password): 
        flash('Please check your login details and try again.', 'danger')
        return redirect(url_for('auth.login')) # if user doesn't exist or password is wrong, reload the page
    login_user(user, remember=True)
    if user.roles[0].name == 'Admin':
        return redirect(url_for('main.da_list'))
    else:
        return redirect(url_for('main.agent_view'))

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        flash('You are already logged in!', 'info')
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        name = form.username.data
        email = form.email.data
        password = form.password.data
        phonenumber = form.phone.data
        default_role = Role.query.filter_by(name='Agent').first()
        new_user = User(username=name, email=email, phone_no=phonenumber, password=bcrypt.generate_password_hash(password).decode('utf-8'), is_working=True)
        new_user.roles.append(default_role)
        db.session.add(new_user)
        db.session.commit()
        #return redirect(url_for('main.agent_view'))
        return redirect(url_for('main.agent_view'))
    return render_template('signup.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))