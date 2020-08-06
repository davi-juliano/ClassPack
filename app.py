from configparser import ConfigParser
from flask import Flask
from flask_cors import CORS


class User():

	def __init__(self, id):
		self.id = id


def authenticate(nouser, nopass):

	from uuid import uuid4
	return User(str(uuid4()))


def identity(payload):

	return payload['identity']


# Factory
def create_app(ini_file):

	app = Flask(__name__)
	CORS(app)

	config = ConfigParser()
	config.read(ini_file)

	__URL_PREFIX = config.get('ClassPack', 'url.prefix', fallback='/')
	__SECRET_KEY = config.get('ClassPack', 'auth.secret')
	__JWT_EXPIRATION = config.getint('ClassPack', 'auth.expiration.minutes', fallback=24 * 60)

	app.config['SECRET_KEY'] = __SECRET_KEY
	app.config['JWT_AUTH_URL_RULE'] = __URL_PREFIX + '/authuser'
	app.config['JWT_AUTH_USERNAME_KEY'] = 'nouser'
	app.config['JWT_AUTH_PASSWORD_KEY'] = 'nopass'

	from datetime import timedelta
	app.config['JWT_EXPIRATION_DELTA'] = timedelta(__JWT_EXPIRATION)

	from optimizer import optimizer, config_optimizer
	config_optimizer(config)
	app.register_blueprint(optimizer, url_prefix=__URL_PREFIX)

	from database import init_db
	init_db(config, app)

	from flask_jwt import JWT
	JWT(app, authenticate, identity)

	return app


if __name__ == '__main__':

	app = create_app("./cp_config.ini")

	app.run(host="0.0.0.0")
