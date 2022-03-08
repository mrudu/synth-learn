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
	k_unsafe = True
	UCBWrapper = UCB(k, LTL_formula, input_atomic_propositions, output_atomic_propositions)
	while k_unsafe:
		initialize_counting_function(mealy_machine, UCBWrapper.num_states)
		if checkCFSafety(mealy_machine, UCBWrapper):
			k_unsafe = False
			break
		k = k + 1
		UCBWrapper = UCB(k, LTL_formula, input_atomic_propositions, output_atomic_propositions)

	### STEP 2 ###
	# Merge compatible nodes
	pairs = get_compatible_node(mealy_machine)
	exclude_pairs = []
	count = 0
	while len(pairs) > 0 and count < 35:
		pair = pairs[0]
		if checkIfExcluded(pair, exclude_pairs):
			pairs = pairs[1:]
			continue
		mealy_machine, exclude_pairs, isMerged = merge_compatible_nodes(
			pair, exclude_pairs, mealy_machine, UCBWrapper)
		if isMerged:
			pairs = get_compatible_node(mealy_machine)
			print("Printing compatible nodes")
			print(list("{} {}".format(pair[0].state_id, 
				pair[1].state_id) for pair in pairs))
		else:
			pairs = get_compatible_node(mealy_machine)
			pairs = pairs[1:]
			print("Printing excluded pairs")
			print(list("{} {}".format(pair[0].state_id, 
				pair[1].state_id) for pair in exclude_pairs))
		print("Printing States:")
		print(list(state.state_id for state in mealy_machine.states))
		count += 1
		print(count)
	
	### STEP 3 ###
	# Complete mealy machine
	# complete_mealy_machine(mealy_machine, UCBWrapper)
	visualize_automaton(
		mealy_machine,
		file_type="pdf"
	)

	return mealy_machine

def checkIfExcluded(pair, exclude_pairs):
	print("Checking exclusion")
	print("{} {}".format(pair[0].state_id, pair[1].state_id))
	print(list("{} {}".format(pair[0].state_id, 
		pair[1].state_id) for pair in exclude_pairs))
	for p in exclude_pairs:
		if p[0].state_id == pair[0].state_id and p[1].state_id == pair[1].state_id \
			or p[1].state_id == pair[0].state_id and p[0].state_id == pair[1].state_id:
			return True
	return False

def merge_compatible_nodes(pair, exclude_pairs, mealy_machine, 
	UCBWrapper):
	print("Attempting Merge")
	print("{} {}".format(pair[0].state_id, pair[1].state_id))
	old_mealy_machine = copy.deepcopy(mealy_machine)
	merged = False
	mealy_machine = mergeAndPropogate(pair[0], pair[1], mealy_machine)
	initialize_counting_function(mealy_machine, UCBWrapper.num_states)
	if not checkCFSafety(mealy_machine, UCBWrapper):
		print("Merge Unsuccessful")
		mealy_machine = old_mealy_machine
		exclude_pairs.append(pair)
	else:
		print("Merge Successful")
		exclude_pairs = []
		merged = True
	return [mealy_machine, exclude_pairs, merged]

build_mealy(data['LTL'], data['input_atomic_propositions'],
	data['output_atomic_propositions'], traces, 2)