import os

class Config(object):
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SECRET_KEY = os.getenv('SECRET_KEY')
	BCRYPT_LOG_ROUNDS = 13
	DEBUG = True