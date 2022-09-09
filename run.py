from flask import Flask
from flask import request
from flask import render_template, send_file, jsonify

from LTLsynthesis.algorithm import build_mealy
from LTLsynthesis.LStarLearning import learning
import logging
import json
import os

from aalpy.utils import load_automaton_from_file

import sys
sys.path.insert(0, 'sample/')

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'dot'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


logger = logging.getLogger("algo-logger")
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

def parse_json(file_name, new_traces = [], k=1):
	with open('examples/' + file_name + ".json", "r") as read_file:
	    data = json.load(read_file)
	LTL_formula = "((" + ') & ('.join(data['assumptions']) + "))->((" + ') & ('.join(data['guarantees']) + "))"
	if len(new_traces) == 0:
		traces = data['traces']
		traces = list(map(lambda trace: trace.split('.'), traces))
	else:
		traces = copy.deepcopy(new_traces)
	m = build_mealy(LTL_formula, data['input_atomic_propositions'], data['output_atomic_propositions'], traces, file_name, data['target'], k)
	learning(m)

@app.route('/', methods=['GET', 'POST'])
def execute():
    if request.method == 'POST':
        target_file = None
        if 'target' in request.files:
            target_file = request.files['target']
        return execute_algorithm(request.form, target_file)
    else:
        return render_template('index.html', LTL_formula="Nothing")

@app.route('/download/dot')
def download_dot():
    return send_file('static/temp_model_files/LearnedModel.dot', as_attachment=True)

@app.route('/download/pdf')
def download_pdf():
    return send_file('static/temp_model_files/LearnedModel.pdf', as_attachment=True)

@app.route('/download/target')
def download_target():
    return send_file('static/temp_model_files/TargetModel.pdf', as_attachment=True)

def execute_algorithm(data, target_file):
    target_filename = ""
    input_atomic_propositions = data['inputs']
    input_atomic_propositions = input_atomic_propositions.split(',')
    output_atomic_propositions = data['outputs']
    output_atomic_propositions = output_atomic_propositions.split(',')
    
    traces = data['traces']
    traces = traces.split('\n')
    traces = list(map(lambda x: x.split('.'), traces))
    
    if (len(target_file.filename) > 0) and (allowed_file(target_file.filename)):
        target_filename = "static/temp_model_files/TargetModel.dot"
        target_file.save(target_filename)
    elif len(target_file.filename) > 0:
        print("Not a dot file!")
        target_file.save(os.path.join("static/temp_model_files", target_file.filename))

    m, stats = build_mealy(
        data['formula'],
        input_atomic_propositions,
        output_atomic_propositions,
        traces, "Sample",
        target_filename, 2)
    svg_file = open('static/temp_model_files/LearnedModel.svg', 'r', encoding = 'utf-8').read()
    svg_file = ''.join(svg_file.split('\n')[6:])
    return jsonify({
        'msg': 'success',
        'img': svg_file,
        'traces': stats['traces']
   })

