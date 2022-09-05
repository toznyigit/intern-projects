from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from . import db
from .models import DBUser, User
from . import passwd

auth = Blueprint('auth', __name__)

@auth.get('/login')
def login():
    return render_template('login.html')

@auth.post('/login')
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    salt = db.__get_salt(username)
    enc_passwd = passwd.secure(password, salt)
    if not db.check_user(username,enc_passwd=f'{enc_passwd}:{salt}'):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))

    user = DBUser(username, db.is_admin(username))
    db.login_user(username, request.remote_addr)
    login_user(User(user), remember=remember)
    return redirect(url_for('main.profile'))

@auth.get('/signup')
def signup():
    return render_template('signup.html')

@auth.post('/signup')
def signup_post():
    if db.check_user(request.form.get('username'),email=request.form.get('email')):
        flash('Email address or username already exists!')
        return redirect(url_for('auth.signup'))
    if request.form.get('password') != request.form.get('repassword'):
        flash('Passwords not matched!')
        return redirect(url_for('auth.signup'))
    if not passwd.validate(request.form.get('password')):
        flash('Please use at least one uppercase letter, one lower case letter, and one number.')
        return redirect(url_for('auth.signup'))

    creds = request.form.to_dict()
    creds['priviledge'] = 1
    token = passwd.token_hex(32)
    creds['password'] = f'{passwd.secure(creds["password"],token)}:{token}'
    db.insert_user(creds)
    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    db.logout_user(current_user._user.username)
    logout_user()
    return redirect(url_for('main.index'))