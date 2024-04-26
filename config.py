# Create dummy secrey key so we can use sessions
SECRET_KEY = '123456790'

# Create in-memory database
DATABASE_FILE = 'sample_db.sqlite'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_FILE
SQLALCHEMY_ECHO = True

# Flask-Security config
SECURITY_URL_PREFIX = "/admin"
SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
SECURITY_PASSWORD_SALT = "ATGUOHAELKiubahiughaerGOJAEGj"

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
INPUTS_TYPES = ['add_missing', 'check_grammar', 'check_answer']

TWILlIO_SID="AC5bff8bc22a46f90839da21091f6a263c"
TWILLIO_KEY="e53347056fb3218d73d2738788cce60b"
TWILLIO_SMS='VAa315c20274179a49fcaff0d7c42eab5b'