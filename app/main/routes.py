from app.main import bp
from flask import request
from flask import render_template, send_file, jsonify, session

@bp.route('/')
def index():
	return 'This is The Main Blueprint'

@app.route('/', methods=['GET', 'POST'])
def execute():
	if request.method == 'POST':
		session['number'] = random.randint(100, 1000)
		target_file = None
		if 'target' in request.files:
			target_file = request.files['target']
		return execute_algorithm(request.form, target_file)
	else:
		file_name = app.root_path + '/src/examples.json'
		with open(file_name) as example_json:
			examples = json.load(example_json)
		return render_template('SynthLearn.html', 
			type="acacia", examples=examples)