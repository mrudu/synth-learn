from flask import Flask

from config import Config
from logging.config import fileConfig

def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(config_class)
    fileConfig('src/logging_conf.ini')

	# Initialize Flask extensions here

	# Register blueprints here
	from app.main import bp as main_bp
    app.register_blueprint(main_bp)

	@app.route('/test/')
	def test_page():
		return '<h1>Testing the Flask Application Factory Pattern</h1>'

    return app