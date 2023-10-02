from LTLsynthesis import app
from flask import request
from flask import render_template, send_file, jsonify, session
from flask import Flask
from LTLsynthesis.RevampCode.algorithm import build_mealy
from LTLsynthesis.RevampCode.utils import save_mealy_machile
import random
import json
import os

ALLOWED_EXTENSIONS = {'dot'}

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def execute_algorithm(data, target_file):
    target_filename = ""

    # parsing inputs and outputs
    inputs = data['inputs']
    inputs = list(map(str.strip, inputs.split(',')))
    outputs = data['outputs']
    outputs = list(map(str.strip, outputs.split(',')))
    
    # parsing traces
    traces = data['traces']
    traces = traces.split('\n')
    traces = list(map(lambda x: x.replace('\r', '').split('.'), traces))

    # k
    k = int(data['k'])

    directory = app.root_path + app.config['MODEL_FILES_DIRECTORY']

    # Target File (Not supported for now)
    
    if (len(target_file.filename) > 0) and (allowed_file(
        target_file.filename)):
        target_file.save(directory + "TargetModel_{}.dot".format(
            session['number']))
    elif len(target_file.filename) > 0:
        print("Not a dot file!")
        target_file.save(directory + target_file.filename)

    m, stats = build_mealy(traces, data['formula'], inputs, outputs,
        app, k)
    if m is None:
        return stats, 400

    automata_filename = directory + "LearnedModel_{}.svg".format(
        session['number'])
    save_mealy_machile(m, automata_filename, ['svg', 'dot', 'pdf'])
    svg_file = open(automata_filename,'r', encoding = 'utf-8').read()
    svg_file = ''.join(svg_file.split('\n')[6:])
    return {
        'query_number': session['number'], 
        'traces': stats['traces'],
        'realizable': stats['realizable'],
        'message': stats['message']
   }, 200

def execute_strix(data):
    # parsing inputs and outputs
    inputs = data['inputs']
    inputs = list(map(str.strip, inputs.split(',')))
    outputs = data['outputs']
    outputs = list(map(str.strip, outputs.split(',')))

    m = build_strix(data['formula'], inputs, outputs)
    return jsonify({
        'msg': m['realizable'],
        'img': m['automata'],
        'svg': "StrixModel_{}.svg".format(session['number'])
   })

@app.route('/', methods=['GET', 'POST'])
def execute():
    if request.method == 'POST':
        session['number'] = random.randint(100, 1000)
        target_file = None
        if 'target' in request.files:
            target_file = request.files['target']
        return execute_algorithm(request.form, target_file)
    else:
        file_name = app.root_path + '/examples.json'
        with open(file_name) as example_json:
            examples = json.load(example_json)
        return render_template('SynthLearn.html', 
            type="acacia", examples=examples)

# @app.route('/documentation/', methods=['GET'])
# def execute_example():
#     file_name = app.root_path + '/examples.json'
#     with open(file_name) as example_json:
#         examples = json.load(example_json)
#     return render_template('Documentation/index.html', 
#         examples=examples, exampleName='index')

@app.route('/documentation/<example>', methods=['GET'])
def execute_example(example):
    file_name = app.root_path + '/examples.json'
    with open(file_name) as example_json:
        examples = json.load(example_json)
    return render_template('Documentation/{}'.format(examples[
        example]['html']), examples=examples, exampleName=example)

@app.route('/strix', methods=['GET', 'POST'])
def execute_strix_route():
    if request.method == 'POST':
        session['number'] = random.randint(100, 1000)
        return execute_strix(request.form)
    else:
        return render_template('StrixDemo.html', LTL_formula="Nothing", type="strix")

@app.route('/download/dot')
def download_dot():
    return send_file(
        app.root_path + app.config['MODEL_FILES_DIRECTORY'] + 'LearnedModel_{}.dot'.format(session['number']), 
        as_attachment=True)

@app.route('/download/pdf')
def download_pdf():
    return send_file(
        app.root_path + app.config['MODEL_FILES_DIRECTORY'] + 'LearnedModel_{}.pdf'.format(session['number']), 
        as_attachment=True)

@app.route('/download/svg')
def download_svg():
    return send_file(
        app.root_path + app.config['MODEL_FILES_DIRECTORY'] + 'StrixModel_{}.svg'.format(session['number']), 
        as_attachment=True)

@app.route('/download/target')
def download_target():
    return send_file(app.root_path + app.config['MODEL_FILES_DIRECTORY'] + 'TargetModel.pdf', as_attachment=True)

@app.route('/clear')
def clear_files():
    dir = 'static/temp_model_files'
    for file in os.scandir(dir):
        os.remove(file.path)
    return render_template('AcaciaSynth.html', type="acacia")