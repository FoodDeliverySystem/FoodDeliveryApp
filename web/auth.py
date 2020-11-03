from flask import Blueprint, render_template,redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from .models import *
from . import db, bcrypt
from flask import Flask, render_template

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
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if user doesn't exist or password is wrong, reload the page
    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=True)
    print(user.roles)
    print(user.roles[0].name)
    if user.roles[0].name == 'Admin':
        return redirect(url_for('main.da_list'))
    else:
        return redirect(url_for('main.index'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    name = request.form.get('username')
    email = request.form.get('email')    
    password = request.form.get('password')
    confirm_password = request.form.get('confirmpassword')
    phonenumber = request.form.get('phonenumber')

    if password != confirm_password:
        flash("Passwords don't match!")
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first() 

    if user:
        flash('Email address already exists, please login!')
        return redirect(url_for('auth.signup'))
    
    new_user = User(username=name, email=email,phone_no=phonenumber,password=bcrypt.generate_password_hash(password).decode('utf-8'), is_working=True)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))