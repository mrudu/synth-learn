import os
import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	PERMANENT_SESSION_LIFETIME = datetime.timedelta(minutes=1)
	FLASK_ENV = os.environ.get('FLASK_ENV')
	DEBUG = True
	TESTING = True
	SECRET_KEY = os.environ.get('SECRET_KEY')
	STRIX_TOOL = '/Users/mrudula/Downloads/strix'
	ACACIA_BONSAI_TOOL = '/home/ubuntu/acacia-bonsai/build/src/acacia-bonsai'
	STRIX_COMMAND = '{} -f \'{}\' --ins=\"{}\" --outs=\"{}\" -m both'
	ACACIA_BONSAI_COMMAND = 'multipass exec affecting-pademelon -- {} -f \'{}\' -i \'{}\' -o \'{}\' --K={}'
	MODEL_FILES_DIRECTORY = '/static/temp_model_files/'