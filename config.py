"""Flask configuration variables"""

from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

class Config:
    """Set Flask configuration from .env file"""

    # General config
    FLASK_APP = environ.get('FLASK_APP')
    FLASK_ENV = environ.get('FLASK_ENV')
    DEBUG = True


    # Database
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://chrisadmin:chrisadmin@localhost:3306/ckplay_db'
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False