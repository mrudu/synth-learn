from flask import Flask
app = Flask(__name__)
app.config.from_pyfile('src/config.py')

import src.route
import sys
from logging.config import fileConfig


fileConfig('src/logging_conf.ini')