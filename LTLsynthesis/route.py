from LTLsynthesis import app
from flask import request
from flask import render_template, send_file, jsonify, session

from LTLsynthesis.algorithm import build_mealy
from LTLsynthesis.LStarLearning import learning
from LTLsynthesis.UCBBuilder import build_strix
import random
from logging.config import fileConfig
import json
import os

ALLOWED_EXTENSIONS = {'dot'}

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def execute_algorithm(data, target_file):
    target_filename = ""
    input_atomic_propositions = data['inputs']
    input_atomic_propositions = input_atomic_propositions.split(',')
    output_atomic_propositions = data['outputs']
    output_atomic_propositions = output_atomic_propositions.split(',')
    
    traces = data['traces']
    traces = traces.split('\n')
    k = int(data['k'])
    traces = list(map(lambda x: x.replace('\r', '').split('.'), traces))
    
    if (len(target_file.filename) > 0) and (allowed_file(target_file.filename)):
        target_filename = app.root_path + app.config['MODEL_FILES_DIRECTORY'] + "TargetModel_{}.dot".format(session['number'])
        target_file.save(target_filename)
    elif len(target_file.filename) > 0:
        print("Not a dot file!")
        target_file.save(app.root_path + app.config['MODEL_FILES_DIRECTORY'] + target_file.filename)

    m, stats = build_mealy(
        data['formula'],
        input_atomic_propositions,
        output_atomic_propositions,
        traces, "Sample",
        target_filename, k)
    if m is None:
        return stats, 400
    return {
        'query_number': session['number'], 
        'traces': stats['traces']
   }, 200

def execute_strix(data):
    input_atomic_propositions = data['inputs']
    input_atomic_propositions = input_atomic_propositions.split(',')
    output_atomic_propositions = data['outputs']
    output_atomic_propositions = output_atomic_propositions.split(',')

    m= build_strix(
        data['formula'],
        input_atomic_propositions,
        output_atomic_propositions)
    return jsonify({
        'msg': 'success',
        'img': m
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
        return render_template('AcaciaSynth.html', LTL_formula="Nothing", type="acacia")

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

@app.route('/download/target')
def download_target():
    return send_file(app.root_path + app.config['MODEL_FILES_DIRECTORY'] + 'TargetModel.pdf', as_attachment=True)

@app.route('/clear')
def clear_files():
    dir = 'static/temp_model_files'
    for file in os.scandir(dir):
        os.remove(file.path)
    return render_template('AcaciaSynth.html', type="acacia")