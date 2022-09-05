from flask import Blueprint, jsonify, request
from . import db, passwd

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return ('',204)

@main.post('/login')
def login():
    req = request.get_json()
    if "username" not in req.keys():
        return (jsonify({"response": "Who will enter?"}), 418)
    if not db.check_user(req["username"]):
        return (jsonify({"response": "Username not exists!"}), 418)
    if "password" not in req.keys():
        return (jsonify({"response": "No password provided!"}), 418)

    salt = db.__get_salt(req["username"])
    enc_passwd = passwd.secure(req["password"], salt)
    if not db.check_user(req["username"],enc_passwd=f'{enc_passwd}:{salt}'):
        return (jsonify({"response": "Please check your login details and try again."}), 418)
    if db.is_online(req["username"]):
        return (jsonify({"response": "User is online."}), 418)

    db.login_user(req["username"], request.remote_addr)
    return ('',204)

@main.post('/logout')
def logout():
    req = request.get_json()
    if "username" not in req.keys():
        return (jsonify({"response": "Who will exit?"}), 418)
    if not db.check_user(req["username"]):
        return (jsonify({"response": "Username not exists!"}), 418)
    if not db.is_online(req["username"]):
        return (jsonify({"response": "User is offline."}), 418)

    db.logout_user(req["username"], request.remote_addr)
    return ('',204)

@main.get('/user/list')
def list():
    out = db.list_table("user_table",("username","email","firstname","middlename","lastname","birthdate"))
    return jsonify(out)

@main.post('/user/create')
def create():
    req = request.get_json()
    if not passwd.validate(req['password']):
        return (jsonify({"response": "Password not valid!"}), 418)
    if not passwd.verify(req['username'], req['email']):
        return (jsonify({"response": "Email or username not valid!"}), 418)
    if db.check_user(req["username"], email=req["email"]):
        return (jsonify({"response": "Email address or username already exists!"}), 418)
    if "" in (req["username"], req["email"], req["password"], req["birthdate"], req["firstname"], req["lastname"]):
        return (jsonify({"response": "Fields must non-epmty!"}), 418)

    req['priviledge'] = 1
    token = passwd.token_hex(32)
    req['password'] = f'{passwd.secure(req["password"],token)}:{token}'
    db.insert_user(request.remote_addr, req)
    return ('',204)

@main.delete('/user/delete/<id>')
def delete(id):
    if db.check_user(id):
        db.delete_user(id, request.remote_addr)
        return ('',200)
    else:
        return ('',406)

@main.put('/user/update/<id>')
def update(id):
    req = request.get_json()
    if not db.check_user(id):
        return (jsonify({"response": "Username not exists!"}), 418)
    if "password" in req.keys():
        if not passwd.validate(req['password']):
            return (jsonify({"response": "Password not valid!"}), 418)
        token = passwd.token_hex(32)
        req['password'] = f'{passwd.secure(req["password"],token)}:{token}'
    if "username" in req.keys():
        if not passwd.verify_username(req['username']):
            return (jsonify({"response": "Username not valid!"}), 418)
        if db.check_user(req["username"]):
            return (jsonify({"response": "Username already exists!"}), 418)
    if "email" in req.keys():
        if not passwd.verify_email(req['email']):
            return (jsonify({"response": "Email address not valid!"}), 418)
        if db.check_user(None, email=req["email"]):
            return (jsonify({"response": "Email address already exists!"}), 418)
    for k in req.keys():
        if req[k] == "":
            return (jsonify({"response": "Fields must non-epmty!"}), 418)

    db.update_user(id, request.remote_addr, req)
    return ('',204)

@main.get('/onlineusers')
def onlineusers():
    out = db.list_table("session_table",("username","ipaddress","logindatetime"))
    return jsonify(out)