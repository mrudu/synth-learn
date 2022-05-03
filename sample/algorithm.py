from aalpy.utils import visualize_automaton, load_automaton_from_file

from prefixTreeBuilder import *
from mealyMachineBuilder import * 
from completeAlgorithm import *

import copy
import json


def build_mealy(LTL_formula, input_atomic_propositions, output_atomic_propositions, traces, target, k = 2):
	### STEP 1 ###
	# Build Prefix Tree Mealy Machine
	mealy_machine = build_prefix_tree(traces)
	target_machine = None
	if len(target) > 0:
		target_machine = load_automaton_from_file("static/TargetModel", automaton_type="mealy")

	# Check if K is appropriate
	kunSafe = True
	kLimit = 10
	UCBWrapper = UCB(k, LTL_formula, input_atomic_propositions, output_atomic_propositions)
	while kunSafe:
		initialize_counting_function(mealy_machine, UCBWrapper.num_states)
		if checkCFSafety(mealy_machine, UCBWrapper):
			kunSafe = False
			break
		k = k + 1
		if k > kLimit:
			print('UNREALIZABLE')
			return None
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
	if target_machine is not None:
		isComp, cex = isCrossProductCompatible(target_machine, mealy_machine)
		if not isComp:
			print('Counter example: ' + ".".join(cex))
			traces.append(cex)
			print("Traces: "+ str(traces))
			return build_mealy(LTL_formula, input_atomic_propositions, output_atomic_propositions, traces, target, k)
		else:
			print("Final machine required traces: " + str(traces))
			visualize_automaton(
				mealy_machine,
				file_type="svg",
				path="static/LearnedModel"
			)
	else:
		visualize_automaton(
			mealy_machine,
			file_type="svg",
			path="static/LearnedModel"
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