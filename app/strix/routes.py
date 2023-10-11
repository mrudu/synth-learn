from app.main import bp
from flask import request
from flask import render_template, send_file, jsonify, session

@bp.route('/strix', methods=['GET', 'POST'])
def execute_strix_route():
    if request.method == 'POST':
        session['number'] = random.randint(100, 1000)
        return execute_strix(request.form)
    else:
        file_name = bp.root_path + '/examples.json'
        with open(file_name) as example_json:
            examples = json.load(example_json)
        return render_template('StrixDemo.html', examples=examples, type="strix")