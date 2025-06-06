import os
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
# Create dummy secrey key so we can use sessions
SECRET_KEY = os.getenv("SECRET_KEY")

# Create in-memory database
DATABASE_FILE = os.getenv("DATABASE_FILE")
SQLALCHEMY_DATABASE_URI = 'mysql+' + DATABASE_FILE

SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True,
    'pool_recycle': 1800,  # Recycle connections every 30 minutes
    'pool_size': 5,
    'max_overflow': 10,
    'connect_args': {
        'connect_timeout': 10,
        'read_timeout': 30,
        'write_timeout': 30,
    },
}

SQLALCHEMY_POOL_RECYCLE= 299
SQLALCHEMY_TRACK_MODIFICATIONS= False

SQLALCHEMY_ECHO = True

# Flask-Security config
SECURITY_URL_PREFIX = "/admin"
SECURITY_PASSWORD_HASH = os.getenv("SECURITY_PASSWORD_HASH")
SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT")

# Flask-Security URLs, overridden because they don't put a / at the end
SECURITY_LOGIN_URL = "/login/"
SECURITY_LOGOUT_URL = "/logout/"
SECURITY_REGISTER_URL = "/register/"

SECURITY_POST_LOGIN_VIEW = "/admin/"
SECURITY_POST_LOGOUT_VIEW = "/admin/"
SECURITY_POST_REGISTER_VIEW = "/admin/"

# Flask-Security features
SECURITY_REGISTERABLE = True
SECURITY_SEND_REGISTER_EMAIL = False
SQLALCHEMY_TRACK_MODIFICATIONS = False

ENG_LEVELS = ['Beginner', 'Elementary', 'Pre-Intermediate', 'Intermediate', 'Advanced']
INPUTS_TYPES = ['add_missing', 'check_grammar', 'check_answer', 'choose_variant']

TWILlIO_SID=os.getenv("TWILlIO_SID")
TWILLIO_KEY=os.getenv("TWILLIO_KEY")
TWILLIO_SMS=os.getenv("TWILLIO_SMS")

PAYMENT_HOST = os.getenv("PAYMENT_HOST")
SECRET_KEY = os.getenv("SECRET_KEY")
SEVICE_ID = os.getenv("SEVICE_ID")
LOGIN=os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")

GPT_KEY = os.getenv("GPT_KEY")


ENKRKEY = os.getenv("ENKRKEY")