from LTLsynthesis.RevampCode.computeWinningRegionsUCB import acacia_bonsai_command
from LTLsynthesis.RevampCode.utils import checkCFSafety, expand_symbolic_trace
from LTLsynthesis.RevampCode.rpni import build_PTA, rpni_mealy, pretty_print
from LTLsynthesis.RevampCode.completeMealy import complete_mealy_machine

def build_mealy(examples, formula, inputs, outputs, app, k=1):
	# arbitrarily setting k_max as a function of k
	k_max = int(k*1.5) if k > 7 else 10

	# computing ucb and winning region using acacia
	ucb, antichain_vectors = acacia_bonsai_command(formula, inputs,
		outputs, k, app)
	while ucb is None and k < k_max:
		k += 1
		ucb, antichain_vectors = acacia_bonsai_command(formula, inputs,
		outputs, k, app)

	# LTL Formula not safe with UCB<k_max
	if ucb is None:
		return None

	# expanding symbolic traces
	expanded_examples = []
	for e in examples:
		expanded_examples.extend(expand_symbolic_trace(e, ucb))

	# building prefix tree automata
	mealy_machine = build_PTA(expanded_examples)

	# check safety of PTA (examples)
	# (The above is done to find appropriate k value for examples)
	cfs = None
	safe, cfs = checkCFSafety(mealy_machine, ucb, 
		antichain_vectors, cfs)

	while not safe and k < k_max:
		k += 1
		ucb, antichain_vectors = acacia_bonsai_command(formula, inputs,
		outputs, k, app)
		safe, cfs = checkCFSafety(mealy_machine, ucb, 
			antichain_vectors, cfs)

	# Examples not safe with UCB<k_max
	if ucb is None:
		return None

	# Building Mealy Machine with RPNI algorithm
	# returns Partially Complete Mealy Machine
	num_premachine_nodes = 0
	mealy_machine = rpni_mealy(mealy_machine, ucb, antichain_vectors)
	num_premachine_nodes = len(mealy_machine.states)
	# Completing Mealy Machine
	complete_mealy_machine(mealy_machine, ucb, antichain_vectors)

	pretty_print(mealy_machine)

	return mealy_machine, {'traces': examples,
	'num_premachine_nodes': num_premachine_nodes, 'k': k}

def build_strix(LTL_formula, I, O, app):
	src_file = app.config['STRIX_TOOL']
	command = app.config['STRIX_COMMAND'].format(src_file, LTL_formula, 
			",".join(I), ",".join(O))
	try:
		op = subprocess.run(command, shell=True, capture_output=True)
		automata_lines = []
		ucb = None
		
		for line in op.stdout.splitlines():
			l = line.decode()
			automata_lines.append(l)

		for a in spot.automata('\n'.join(automata_lines[1:])):
			ucb = a
		with open(app.root_path + app.config['MODEL_FILES_DIRECTORY']
			+ "StrixModel.svg", 'w') as f:
			f.write(a.show().data)
		return a.show().data
	except Exception as e:
		traceback.print_exc()

	return ""
