from CustomAALpy.FileHandler import visualize_automaton, save_automaton_to_file, load_automaton_from_file
import logging
from flask import session
from functools import reduce
from LTLsynthesis.prefixTreeBuilder import build_prefix_tree, trace_to_int_function, checkCFSafety, expand_traces
from LTLsynthesis.mealyMachineBuilder import get_compatible_nodes, isCrossProductCompatible, merge_compatible_nodes
from LTLsynthesis.completeAlgo import complete_mealy_machine
from LTLsynthesis.utilities import *
from LTLsynthesis.UCBBuilder import UCB

logger = logging.getLogger("algo-logger")

def generated_prefixes(traces):
	prefixes = []
	for trace in traces:
		for i in range(0, len(trace)-1, 2):
			prefixes.append(trace[0:(i+2)])
			logger.debug("Extended trace: " + str(trace[0:(i+2)]))
	return list(set(list(map(lambda trace: '.'.join(trace), prefixes))))

def generalization_algorithm(traces, LTL_formula, merging_strategy, I, O):
	node_queue = [mealy_machine.initial_state]
	visited_nodes = []
	while node_queue:
		current_node = node_queue.pop(0)
		visited_nodes.append(current_node)


def build_mealy(LTL_formula, I, O, traces, file_name, target, k = 2):	
	global ordered_inputs, bdd_inputs, ucb, UCBWrapper

	### STEP 1 ###

	# Check if K is appropriate
	logger.debug("Checking if K is appropriate...")

	logger.debug("Checking if K is appropriate for LTL")
	k_unsafe = True
	UCBWrapper = UCB(k, LTL_formula, I, O)
	count = 0
	while UCBWrapper.ucb is None:
		logger.debug("LTL Specification is unsafe for k=" + str(k))
		count += 1
		if count == 10:
			if check_to_continue():
				count = 0
			else:
				return None
		k = k + 1
		UCBWrapper = UCB(k, LTL_formula, I, O)
	
	logger.info("LTL Specification is safe for k=" + str(k))
	bdd_inputs = UCBWrapper.bdd_inputs
	ucb = UCBWrapper.ucb

	# Build Prefix Tree Mealy Machine
	logger.info("Building Prefix Tree Mealy Machine...")
	traces = expand_traces(traces)
	traces = generated_prefixes(traces)
	traces = list(map(lambda trace: trace.split('.'), traces))
	ordered_inputs = list(map(lambda prop: bdd_to_str(prop), bdd_inputs))
	logger.debug("Traces coming from here: (sorting traces)")
	traces = sorted(traces, key=lambda trace: trace_to_int_function(trace))
	mealy_machine = build_prefix_tree(traces)

	logger.info("Prefix Tree Mealy Machine built")
	
	count = 0
	# Check if K is appropriate for traces
	logger.info("Checking if K is appropriate for traces")
	while k_unsafe:
		initialize_counting_function(mealy_machine, UCBWrapper)
		if checkCFSafety(mealy_machine):
			logger.info("Traces is safe for k=" + str(k))
			k_unsafe = False
			break
		k = k + 1
		logger.debug("Traces is unsafe for k=" + str(k))
		count += 1
		if count == 10:
			if check_to_continue():
				count = 0
			else:
				return None
		UCBWrapper = UCB(k, LTL_formula, I, O)

	# Check if K is appropriate for target
	target_machine = None
	if len(target) > 0:
		logger.info("Checking if K is appropriate for target machine")
		target_machine = load_automaton_from_file(target)
		save_mealy_machile(target_machine, "static/temp_model_files/TargetModel", ['svg', 'pdf'])
		k_unsafe = True
		count = 0
		while k_unsafe:
			initialize_counting_function(target_machine, UCBWrapper)
			if checkCFSafety(target_machine):
				logger.info('Target is safe for k=' + str(k))
				k_unsafe = False
				break
			k = k + 1
			logger.debug('Target is unsafe for k=' + str(k))
			count += 1
			if count == 10:
				if check_to_continue():
					count = 0
				else:
					return None
			UCBWrapper = UCB(k, LTL_formula, I, O)

	logger.debug("Chosen appropriate K.")
	### STEP 2 ###
	# Merge compatible nodes
	logger.info("Merging compatible nodes in prefix tree...")
	pairs = get_compatible_nodes(mealy_machine)
	exclude_pairs = []
	count = 1
	while len(pairs) > 0:
		pair = pairs[0]
		logger.debug("Attempting to merge nodes: " + pair[0].state_id + ", " + pair[1].state_id)
		if is_excluded(pair, exclude_pairs):
			logger.debug("Pair excluded. Moving on...")
			pairs = pairs[1:]
			continue
		mealy_machine, exclude_pairs, isMerged = merge_compatible_nodes(
			pair, exclude_pairs, mealy_machine, UCBWrapper)
		pairs = get_compatible_nodes(mealy_machine)
		if not isMerged:
			logger.debug("Merge unsuccessful. Moving on...")
			pairs = pairs[count:]
			count += 1
		else:
			logger.debug("Merge successful.")
			logger.debug("Next in line:")
			for pair in pairs:
				logger.debug("[{}, {}]".format(pair[0].state_id, pair[1].state_id))
			count = 1

	### STEP 2.5 ###
	# Mark nodes in "pre-machine"
	mark_nodes(mealy_machine)

	logger.debug("Pre-machine complete.")
	num_premachine_nodes = len(mealy_machine.states)
	### STEP 3 ###
	# Complete mealy machine
	complete_mealy_machine(mealy_machine, UCBWrapper)
	if target_machine is not None:
		isComp, cex = isCrossProductCompatible(target_machine, mealy_machine)
		if not isComp:
			logger.warning('Counter example: ' + ".".join(cex))
			traces.append(cex)
			logger.debug("Traces: "+ str(traces))

			return build_mealy(
				LTL_formula, 
				I, 
				O, traces, 
				file_name, target, k)
	save_mealy_machile(mealy_machine, "static/temp_model_files/LearnedModel", ['dot'])
	cleaner_display(mealy_machine, UCBWrapper.ucb)
	save_mealy_machile(mealy_machine, "static/temp_model_files/LearnedModel", ['svg', 'pdf'])
	print_log(target_machine, mealy_machine, num_premachine_nodes, traces, k, UCBWrapper)
	return mealy_machine, {'traces': traces, 'num_premachine_nodes': num_premachine_nodes, 'k': k}

def display_mealy_machine(mealy_machine, file_name, file_type="pdf"):
	visualize_automaton(
		mealy_machine,
		path="examples/" + file_name + '_' + str(session['number']),
		file_type="pdf"
	)
def save_mealy_machile(mealy_machine, file_name, file_type = ['dot']):
	for type in file_type:
		save_automaton_to_file(
			mealy_machine,
			file_type=type,
			path=file_name + '_' + str(session['number'])
		)
def mark_nodes(mealy_machine):
	for state in mealy_machine.states:
		state.special_node = True
		state.premachine_transitions = list(state.transitions.keys())