from app.synthlearn.computeWinningRegionsUCB import acacia_bonsai_command
from app.synthlearn.utils import checkCFSafety, expand_symbolic_trace, mergeEdges, cfThenPrefix, prefixThenCF
from app.synthlearn.rpni import build_PTA, generalize, pretty_print
from app.synthlearn.completeMealy import complete_mealy_machine
import logging

logger = logging.getLogger("overallLogger")

def build_mealy(examples, formula, inputs, outputs, config, k, merging_strategy):
	# arbitrarily setting k_max as a function of k
	k_max = int(k*1.5) if k > 7 else 10

	# computing ucb and winning region using acacia
	ucb, antichain_vectors = acacia_bonsai_command(formula, inputs,
		outputs, k, config)
	while ucb is None and k < k_max:
		k += 1
		ucb, antichain_vectors = acacia_bonsai_command(formula, inputs,
		outputs, k, config)
		logger.debug("UCB is unrealizable. Increasing k")

	# LTL Formula not safe with UCB<k_max
	if ucb is None:
		return None, {'realizable': False, 'message': 'Check formula and try again?'}

	# expanding symbolic traces
	expanded_examples = []
	for e in examples:
		expanded_examples.extend(expand_symbolic_trace(e, ucb))

	# building prefix tree automata
	mealy_machine = build_PTA(expanded_examples)
	if mealy_machine is None:
		return None, {'realizable': False, 'message': 'Conflicting examples. Check examples and try again?'}

	# check safety of PTA (examples)
	# (The above is done to find appropriate k value for examples)
	cfs = None
	safe, cfs = checkCFSafety(mealy_machine, ucb, 
		antichain_vectors, cfs)
	print(antichain_vectors)

	while not safe and k < k_max:
		k += 1
		ucb, antichain_vectors = acacia_bonsai_command(formula, inputs,
		outputs, k, config)
		safe, cfs = checkCFSafety(mealy_machine, ucb, 
			antichain_vectors, cfs)

	# Examples not safe with UCB<k_max
	if not safe:
		return None, {'realizable': False, 'message': 'Check examples and try again?'}

	# Building Mealy Machine with RPNI algorithm
	# returns Partially Complete Mealy Machine
	num_premachine_nodes = 0
	if merging_strategy == "CF":
		strategy = cfThenPrefix
	else:
		strategy = prefixThenCF
	mealy_machine = generalize(mealy_machine, ucb, antichain_vectors, strategy)
	num_premachine_nodes = len(mealy_machine.states)
	# Completing Mealy Machine
	complete_mealy_machine(mealy_machine, ucb, antichain_vectors)

	mergeEdges(mealy_machine, ucb)

	pretty_print(mealy_machine)

	return mealy_machine, {'traces': examples,
	'num_premachine_nodes': num_premachine_nodes, 'k': k, 
	'realizable': True, 'message': ''}
