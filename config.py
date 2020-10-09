import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

DB_USER = os.getenv('DB_USER', 'rossloney')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'xochim1lc0')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'fyyur')

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgres://{}:{}@{}:5432/{}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
