from aalpy.utils import visualize_automaton

from prefixTreeBuilder import *
from mealyMachineBuilder import * 
from completeAlgorithm import *

import copy
import json

file_name = input("Enter name of json_file:")
with open('examples/' + file_name, "r") as read_file:
    data = json.load(read_file)

traces = data['traces']
traces = list(map(lambda x: x.split('.'), traces))


def build_mealy(LTL_formula, input_atomic_propositions, output_atomic_propositions, traces, k = 2):
	### STEP 1 ###
	# Build Prefix Tree Mealy Machine
	mealy_machine = build_prefix_tree(traces)

	# Check if K is appropriate
	kunSafe = True
	UCBWrapper = UCB(k, LTL_formula, input_atomic_propositions, output_atomic_propositions)
	while kunSafe:
		initialize_counting_function(mealy_machine, UCBWrapper.num_states)
		if checkCFSafety(mealy_machine, UCBWrapper):
			kunSafe = False
			break
		k = k + 1
		UCBWrapper = UCB(k, LTL_formula, input_atomic_propositions, output_atomic_propositions)

	### STEP 2 ###
	# Merge compatible nodes
	pair = get_compatible_node(mealy_machine)
	exclude_pairs = []
	while pair is not None:
		mealy_machine, exclude_pairs = merge_compatible_nodes(pair,
			exclude_pairs, mealy_machine, UCBWrapper)
		pair = get_compatible_node(mealy_machine, exclude_pairs)
	
	### STEP 3 ###
	# Complete mealy machine
	complete_mealy_machine(mealy_machine, UCBWrapper)
	visualize_automaton(
		mealy_machine,
		file_type="pdf"
	)

	return mealy_machine

def merge_compatible_nodes(pair, exclude_pairs, mealy_machine, 
	UCBWrapper):
	old_mealy_machine = copy.deepcopy(mealy_machine)
	mealy_machine = mergeAndPropogate(pair[0], pair[1], mealy_machine)
	initialize_counting_function(mealy_machine, UCBWrapper.num_states)
	if not checkCFSafety(mealy_machine, UCBWrapper):
		mealy_machine = old_mealy_machine
		exclude_pairs.append(pair)
	else:
		exclude_pairs = []
	return [mealy_machine, exclude_pairs]

build_mealy(data['LTL'], data['input_atomic_propositions'],
	data['output_atomic_propositions'], traces, 2)