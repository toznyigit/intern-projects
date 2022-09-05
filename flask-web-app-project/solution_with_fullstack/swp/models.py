class User(object):
    
    def __init__(self, user):
        self._user = user
        self.is_admin = user.type

    def get_id(self):
        return self._user.username

    def is_active(self):
        return self._user.enabled

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True


class DBUser():

    def __init__(self, name, type):
        self.username = name
        self.type = type
        self.enabled = False