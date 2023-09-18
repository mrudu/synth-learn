from flask import Flask
from computeWinningRegionsUCB import acacia_bonsai_command
from utils import checkCFSafety, expand_symbolic_trace
from logging.config import fileConfig
from rpni import build_PTA, rpni_mealy, prune_machine, pretty_print
from completeMealy import complete_mealy_machine

# app = Flask(__name__)
# app.config.from_pyfile('config.py')
# fileConfig('LTLsynthesis/logging_conf.ini')

def execute_algorithm(examples, formula, inputs, outputs, k=1):
	# arbitrarily setting k_max as a function of k
	k_max = int(k*1.5) if k > 7 else 10

	# parsing inputs and outputs
	inputs = list(map(str.strip, inputs.split(',')))
	outputs = list(map(str.strip, outputs.split(',')))

	# computing ucb and winning region using acacia
	ucb, antichain_vectors = acacia_bonsai_command(formula, inputs,
		outputs, k)
	while ucb is None and k < k_max:
		k += 1
		ucb, antichain_vectors = acacia_bonsai_command(formula, inputs,
		outputs, k)

	# LTL Formula not safe with UCB<k_max
	if ucb is None:
		return None

	# expanding symbolic traces
	expanded_examples = []
	for e in examples:
		expanded_examples.extend(expand_symbolic_trace(e.split('.'), ucb))

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
		outputs, k)
		safe, cfs = checkCFSafety(mealy_machine, ucb, 
			antichain_vectors, cfs)

	# Examples not safe with UCB<k_max
	if ucb is None:
		return None

	# Building Mealy Machine with RPNI algorithm
	# returns Partially Complete Mealy Machine
	mealy_machine = rpni_mealy(mealy_machine, ucb, antichain_vectors)
	prune_machine(mealy_machine)
	# Completing Mealy Machine
	complete_mealy_machine(mealy_machine, ucb, antichain_vectors)

	pretty_print(mealy_machine)

	return mealy_machine
