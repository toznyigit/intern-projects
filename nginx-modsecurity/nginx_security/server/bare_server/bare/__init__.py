import os
from flask import Flask

def create_app():
    app = Flask(__name__)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .db import check_user, __db_init
    db.__db_init()

    return app