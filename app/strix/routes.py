from app.web import bp
from flask import request, render_template, send_file, current_app, session
import json, random, subprocess, spot, traceback


@bp.route('/strix', methods=['GET', 'POST'])
def strix():
    if request.method == 'POST':
        session['number'] = random.randint(100, 1000)
        directory = current_app.root_path + \
            current_app.config['MODEL_FILES_DIRECTORY']

        src_file = current_app.config['STRIX_TOOL']
        command = current_app.config['STRIX_COMMAND'].format(
            src_file, request.form['formula'],
            request.form['inputs'], request.form['outputs'])
        try:
            op = subprocess.run(command, shell=True, capture_output=True)
            automata_lines = []
            ucb = None
            
            for line in op.stdout.splitlines():
                l = line.decode()
                automata_lines.append(l)

            for a in spot.automata('\n'.join(automata_lines[1:])):
                ucb = a
            with open(current_app.root_path + \
                current_app.config['MODEL_FILES_DIRECTORY'] + \
                "Model_{}.svg".format(session['number']), 'w') as f:
                f.write(a.show().data)
            return {
                'msg': automata_lines[0], 
                'img': a.show().data, 
                'svg': "Model_{}.svg".format(session['number'])
            }
        except Exception as e:
            print(command)
            traceback.print_exc()
            return {
                'msg': False,
                'img': 'Error'
            }
    else:
        file_name = current_app.root_path + '/static/data/examples.json'
        with open(file_name) as example_json:
            examples = json.load(example_json)
        return render_template('StrixDemo.html', examples=examples)