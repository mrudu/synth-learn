from flask import Flask
from flask import request
from flask import render_template

from aalpy.utils import load_automaton_from_file

import sys
sys.path.insert(0, 'sample/')

from sample.algorithm import *

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def execute():
    if request.method == 'POST':
        return execute_algorithm(request.form)
    else:
        return render_template('index.html', LTL_formula="Nothing")

def execute_algorithm(data):
    input_atomic_propositions = data['input_atomic_propositions']
    input_atomic_propositions = input_atomic_propositions.split(' ')
    output_atomic_propositions = data['output_atomic_propositions']
    output_atomic_propositions = output_atomic_propositions.split(' ')
    traces = data['traces']
    traces = traces.split(',')
    traces = list(map(lambda x: x.split('.'), traces))
    target = data['target']

    things = build_mealy(data['LTL'], input_atomic_propositions, output_atomic_propositions, traces, None, 2)
    return render_template('index.html', LTL_formula=data['LTL'])
