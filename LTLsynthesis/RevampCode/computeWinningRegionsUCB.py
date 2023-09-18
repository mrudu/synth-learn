import spot
import subprocess
import traceback
from LTLsynthesis.RevampCode.ucbHelperFunctions import create_bdd_list

def parse_command(op_lines):
	antichain_vectors = []
	hoa_ucb = ""
	ucb = None
	captureUCB = False
	captureAntichain = False
	
	for line in op_lines:
		l = line.decode().strip('\n')
		if l.startswith("AUTOMATA"):
			captureUCB = not captureUCB
		elif captureUCB:
			hoa_ucb += l + "\n"
		elif l.startswith("ANTICHAIN"):
			captureAntichain = not captureAntichain
		elif captureAntichain:
			antichain_vectors.append(list(map(lambda x: int(x), 
				l.strip('{ }\n').split(" "))))
		elif l == "UNKNOWN" or l == "UNREALIZABLE":
			break
	
	if len(hoa_ucb) > 0:
		for a in spot.automata(hoa_ucb[:-1]):
			ucb = a
	return [ucb, antichain_vectors]

def acacia_bonsai_command(formula, inputs, outputs, k, app):
	command = app.config['ACACIA_BONSAI_COMMAND'].format(
		app.config['ACACIA_BONSAI_TOOL'], formula, ",".join(inputs),
		",".join(outputs), k)
	ucb = None
	antichain_vectors = []
	try:
		op = subprocess.run(command, shell=True, capture_output=True)
		ucb, antichain_vectors = parse_command(op.stdout.splitlines())
		ucb.bdd_inputs = create_bdd_list(ucb, inputs)
		ucb.bdd_outputs = create_bdd_list(ucb, outputs)
	except Exception as e:
		traceback.print_exc()
	return [ucb, antichain_vectors]