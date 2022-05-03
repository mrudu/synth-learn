from aalpy.utils import visualize_automaton, load_automaton_from_file

from prefixTreeBuilder import *
from mealyMachineBuilder import * 
from completeAlgorithm import *

import copy
import json

file_name = input("Enter name of json_file:")


def build_mealy(LTL_formula, input_atomic_propositions, output_atomic_propositions, traces, file_name, target, k = 2):
	### STEP 1 ###
	# Build Prefix Tree Mealy Machine
	mealy_machine = build_prefix_tree(traces)
	target_machine = None
	if len(target) > 0:
		target_machine = load_automaton_from_file("examples/" + target, automaton_type="mealy")

	# Check if K is appropriate
	k_unsafe = True
	UCBWrapper = UCB(k, LTL_formula, input_atomic_propositions, output_atomic_propositions)
	while UCBWrapper.ucb is None:
		k = k + 1
		UCBWrapper = UCB(k, LTL_formula, input_atomic_propositions, output_atomic_propositions)
	
	while k_unsafe:
		initialize_counting_function(mealy_machine, UCBWrapper)
		if checkCFSafety(mealy_machine, UCBWrapper):
			k_unsafe = False
			break
		k = k + 1
		UCBWrapper = UCB(k, LTL_formula, input_atomic_propositions, output_atomic_propositions)

	### STEP 2 ###
	# Merge compatible nodes
	pairs = get_compatible_node(mealy_machine)
	exclude_pairs = []
	count = 1
	while len(pairs) > 0:
		pair = pairs[0]
		if is_excluded(pair, exclude_pairs):
			pairs = pairs[1:]
			continue
		mealy_machine, exclude_pairs, isMerged = merge_compatible_nodes(
			pair, exclude_pairs, mealy_machine, UCBWrapper)
		pairs = get_compatible_node(mealy_machine)
		if not isMerged:
			pairs = pairs[count:]
			count += 1
		else:
			count = 1


	
	### STEP 3 ###
	# Complete mealy machine
	complete_mealy_machine(mealy_machine, UCBWrapper)
	if target_machine is not None:
		isComp, cex = isCrossProductCompatible(target_machine, mealy_machine)
		if not isComp:
			print('Counter example: ' + ".".join(cex))
			traces.append(cex)
			print("Traces: "+ str(traces))
			return parse_json(file_name, traces)
		else:
			print("Final machine required traces: " + str(traces))
			visualize_automaton(
				mealy_machine,
				path="examples/" + file_name + 'mealy',
				file_type="pdf"
			)
			visualize_automaton(
				target_machine,
				path="examples/" + file_name + 'target',
				file_type="pdf"
			)
	else:
		visualize_automaton(
			mealy_machine,
			path="examples/" + file_name,
			file_type="dot"
		)
		visualize_automaton(
			mealy_machine,
			path="examples/" + file_name + 'visual',
			file_type="pdf"
		)

	return mealy_machine

def merge_compatible_nodes(pair, exclude_pairs, mealy_machine, 
	UCBWrapper):
	old_mealy_machine = copy.deepcopy(mealy_machine)
	merged = False
	mealy_machine = mergeAndPropogate(pair[0], pair[1], mealy_machine)
	initialize_counting_function(mealy_machine, UCBWrapper)
	if not checkCFSafety(mealy_machine, UCBWrapper):
		mealy_machine = old_mealy_machine
		exclude_pairs.append(pair)
	else:
		exclude_pairs = []
		merged = True
	return [mealy_machine, exclude_pairs, merged]

def parse_json(file_name, new_traces = []):
	with open('examples/' + file_name + ".json", "r") as read_file:
	    data = json.load(read_file)
	LTL_formula = "((" + ') & ('.join(data['assumptions']) + "))->((" + ') & ('.join(data['guarantees']) + "))"
	if len(new_traces) == 0:
		traces = data['traces']
		traces = list(map(lambda x: x.split('.'), traces))
	else:
		traces = copy.deepcopy(new_traces)
	build_mealy(LTL_formula, data['input_atomic_propositions'], data['output_atomic_propositions'], traces, file_name, data['target'], 1)

parse_json(file_name)