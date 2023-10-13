from flask import Flask
from flask import request
from flask import render_template, send_file, jsonify, session

from logging.config import fileConfig

app = Flask(__name__, template_folder="./templates")
app.config.from_pyfile('config.py')
fileConfig('LTLsynthesis/logging_conf.ini')