from flask import Flask

from logging.config import fileConfig

app = Flask(__name__)
app.config.from_pyfile('config.py')
fileConfig('LTLsynthesis/logging_conf.ini')