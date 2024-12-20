import os

from flask import Flask


def create_app(test_config=None):
	# Create and configure the app
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_mapping(
		SECRET_KEY='dev',  # Change this to a random secure key in production
		DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
	)
	app.config['UPLOAD_FOLDER_PATH'] = os.path.join(app.instance_path, 'uploads')

	if test_config is None:
		# Load the instance config, if it exists
		app.config.from_pyfile('config.py', silent=True)
	else:
		# Load the test config
		app.config.update(test_config)

	# Ensure the instance folder exists
	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	# Ensure the uploads folder exists
	try:
		os.makedirs(app.config['UPLOAD_FOLDER_PATH'])
	except OSError:
		pass

	# Database setup
	from . import db
	db.init_app(app)

	# Register blueprints
	from . import auth, document
	app.register_blueprint(auth.bp)
	app.register_blueprint(document.bp)
	app.add_url_rule('/', endpoint='index')

	return app
