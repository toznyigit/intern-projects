from hashlib import sha256
from secrets import token_hex
import re

PEPPER = "Thq68yG0N$axW^m1Cih^Ef&xw5A8G2sD"
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$")
NAME_REGEX = re.compile(r"^(?=.{8,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$")

def validate(password):
    if len(password) < 8:
        return False
    elif re.search('[a-z]',password) is None:
        return False
    elif re.search('[A-Z]',password) is None:
        return False
    elif re.search('[0-9]',password) is None:
        return False
        
    return True

def secure(password, salt):
    enc_passwd = password
    for i in range(64):
        if i%2:
            enc_passwd = sha256((enc_passwd+salt).encode('utf-16')).hexdigest()
        else:
            enc_passwd = sha256((enc_passwd+salt).encode('utf-16')).hexdigest()
            enc_passwd = sha256((enc_passwd+PEPPER).encode('utf-16')).hexdigest()
    return enc_passwd

def verify(username, email):
    if verify_username(username) and verify_email(email):
        return True
    return False

def verify_username(username):
    if NAME_REGEX.match(username):
        return True
    return False

def verify_email(email):
    if EMAIL_REGEX.match(email):
        return True
    return False