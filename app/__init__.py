import os
import logging
from flask import Flask, request
from flask_login import LoginManager
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from logging.handlers import RotatingFileHandler
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l


appl = Flask(__name__)
appl.config.from_object(Config)
db = SQLAlchemy(app=appl)
migrate = Migrate(app=appl, db=db)

login = LoginManager(app=appl)
login.login_view = "login"
login.login_message = _l("Please, log in to access this page.")

mail = Mail(appl)
bootstrap = Bootstrap(appl)
moment = Moment(appl)
babel = Babel(appl)




if not appl.debug:
    if not os.path.exists("logs"):
        os.mkdir("logs")
    file_handler = RotatingFileHandler("logs/microblog.log", maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d"))
    file_handler.setLevel(logging.INFO)
    appl.logger.addHandler(file_handler)

    appl.logger.setLevel(logging.INFO)
    appl.logger.info("Microblog2 startup")


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(appl.config["LANGUAGES"])
    # return 'ru'

from app import routes, models, errors