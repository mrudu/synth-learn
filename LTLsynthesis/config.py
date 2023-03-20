"""Flask configuration."""

TESTING = True
DEBUG = True
FLASK_ENV = 'development'
SECRET_KEY = '97db21348530a03c3a836519c3d636b1f42d4fae7c98038349a9ea87a20dcc36'

STRIX_TOOL = '/Users/mrudula/Downloads/strix'
ACACIA_BONSAI_TOOL = '/home/ubuntu/acacia-bonsai/build/src/acacia-bonsai'
STRIX_COMMAND = '{} -f \'{}\' --ins=\"{}\" --outs=\"{}\" -m both'
ACACIA_BONSAI_COMMAND = '{} -f \'{}\' -i \'{}\' -o \'{}\' --K={} --negative {}'
MODEL_FILES_DIRECTORY = '/static/temp_model_files/'