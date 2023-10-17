from app.web import bp
from flask import request, render_template, send_file, current_app, session
from app.synthlearn.algorithm import build_mealy
import json, random
from app.utils import process_data, save_mealy_machile

@bp.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		session['number'] = random.randint(100, 1000)
		directory = current_app.root_path + \
			current_app.config['MODEL_FILES_DIRECTORY']
		inputs, outputs, formula, traces, k, strategy = process_data(
			request.form)

		m, stats = build_mealy(traces, formula, inputs, outputs,
		    current_app.config, k, strategy)
		if m is None:
		    return stats, 400

		automata_filename = directory + "Model_{}.svg".format(
		    session['number'])
		save_mealy_machile(m, automata_filename, ['svg', 'dot', 'pdf'])
		return {
		    'query_number': session['number'], 
		    'traces': stats['traces'],
		    'realizable': stats['realizable'],
		    'message': stats['message']
		}, 200
	else:
		file_name = current_app.root_path + '/static/data/examples.json'
		with open(file_name) as example_json:
			examples = json.load(example_json)
		return render_template('SynthLearn.html', examples=examples)

@bp.route('/download/<filetype>')
def download_pdf(filetype):
    return send_file(
        current_app.root_path + current_app.config['MODEL_FILES_DIRECTORY'] + \
        'Model_{}.{}'.format(session['number'], filetype), as_attachment=True)