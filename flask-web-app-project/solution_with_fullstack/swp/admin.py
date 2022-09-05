from flask import Blueprint, render_template, redirect, flash, url_for, jsonify, request
from flask_login import login_required, current_user
from . import db
from secrets import token_hex
from . import passwd

admin = Blueprint('admin', __name__)

@admin.route('/panel')
@login_required
def panel():
    if not current_user.is_admin:
        flash('You are not authorized!','error')
        return redirect(url_for('main.profile'))
    
    return render_template('panel.html', online_table=onlineusers().json, user_table=user_list().json)

@admin.get('/onlineusers')
@login_required
def onlineusers():
    if not current_user.is_admin:
        flash('You are not authorized!','error')
        return redirect(url_for('main.profile'))
    out = db.list_table("session_table",("username","ipaddress","logindatetime"))
    return jsonify(out)

@admin.get('/user/list')
@login_required
def user_list():
    if not current_user.is_admin:
        flash('You are not authorized!','error')
        return redirect(url_for('main.profile'))
    out = db.list_table("user_table",("username","email","firstname","middlename","lastname","birthdate"))
    return jsonify(out)



@admin.get('/user/create')
def user_create_get():
    return render_template('signup.html')

@admin.post('/user/create')
def user_create_post():
    if db.check_user(request.form.get('username'),email=request.form.get('email')):
        flash('Email address or username already exists!')
        return redirect(url_for('admin.user_create_get'))
    if not passwd.validate(request.form.get('password')):
        flash('Please use at least one uppercase letter, one lower case letter, and one number.')
        return redirect(url_for('admin.user_create_get'))
    
    creds = request.form.to_dict()
    creds['priviledge'] = 1
    token = token_hex(32)
    creds['password'] = f'{passwd.secure(creds["password"],token)}:{token}'
    db.insert_user(creds)
    return redirect(url_for('admin.panel'))

@admin.get('/user/delete/<username>')
def user_delete(username):
    if not current_user.is_admin:
        flash('You are not authorized!','error')
        return redirect(url_for('main.profile'))

    db.delete_user(username)
    return redirect(url_for('admin.panel'))

@admin.get('/user/update/<username>')
@login_required
def user_update_get(username):
    if not current_user.is_admin:
        flash('You are not authorized!','error')
        return redirect(url_for('main.profile'))
    out = db.__parse_dict(("username","email","firstname","middlename","lastname","birthdate"),[db.get_user(username)])
    return render_template('update.html', user=out[0])

@admin.post('/user/update/<username>')
@login_required
def user_update_post(username):
    if not current_user.is_admin:
        flash('You are not authorized!','error')
        return redirect(url_for('main.profile'))
    creds = request.form.to_dict()
    db.update_user(username, creds)
    return redirect(url_for('admin.panel'))

@admin.get('/logs')
@login_required
def dump_logs():
    if not current_user.is_admin:
        flash('You are not authorized!','error')
        return redirect(url_for('main.profile'))
    out = db.list_table("log_table",("username","logindatetime","activity"))
    return jsonify(out)