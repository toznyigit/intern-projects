from hashlib import sha256
from secrets import token_hex
import re

PEPPER = "Thq68yG0N$axW^m1Cih^Ef&xw5A8G2sD"

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