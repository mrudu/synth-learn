from flask import Flask

from config import Config
from logging.config import fileConfig

def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(config_class)
	fileConfig('app/logging_conf.ini')

	# Initialize Flask extensions here

	# Register blueprints here
	from app.web import bp as web_bp
	from app.strix import bp as strix_bp
	
	app.register_blueprint(web_bp)
	app.register_blueprint(strix_bp)

	return app