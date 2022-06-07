from aalpy.utils import visualize_automaton, load_automaton_from_file
import logging
from LTLsynthesis.prefixTreeBuilder import build_prefix_tree, sort_trace_function, checkCFSafety
from LTLsynthesis.mealyMachineBuilder import get_compatible_nodes, isCrossProductCompatible, merge_compatible_nodes
from LTLsynthesis.completeAlgo import complete_mealy_machine
from LTLsynthesis.utilities import *
from LTLsynthesis.UCBBuilder import UCB

logger = logging.getLogger("algo-logger")


def check_to_continue():
	answer = input("Are you sure you wish to continue? (y/Y for yes): ")
	return (answer in "yY")

def build_mealy(LTL_formula, input_atomic_propositions, output_atomic_propositions, traces, file_name, target, k = 2):
	### STEP 1 ###

	# Check if K is appropriate
	logger.debug("Checking if K is appropriate...")

	logger.debug("Checking if K is appropriate for LTL")
	k_unsafe = True
	UCBWrapper = UCB(k, LTL_formula, input_atomic_propositions, output_atomic_propositions)
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
		UCBWrapper = UCB(k, LTL_formula, input_atomic_propositions, output_atomic_propositions)
	
	logger.info("LTL Specification is safe for k=" + str(k))

	# Build Prefix Tree Mealy Machine
	logger.debug("Building Prefix Tree Mealy Machine...")
	ordered_inputs = list(map(lambda prop: bdd_to_str(prop), UCBWrapper.bdd_inputs))
	traces = sorted(traces, key=lambda trace: sort_trace_function(trace, ordered_inputs))
	mealy_machine = build_prefix_tree(traces)

	logger.debug("Prefix Tree Mealy Machine built")
	
	count = 0
	# Check if K is appropriate for traces
	logger.debug("Checking if K is appropriate for traces")
	while k_unsafe:
		initialize_counting_function(mealy_machine, UCBWrapper)
		if checkCFSafety(mealy_machine, UCBWrapper):
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
		UCBWrapper = UCB(k, LTL_formula, input_atomic_propositions, output_atomic_propositions)

	# Check if K is appropriate for target
	logger.debug("Checking if K is appropriate for target machine")
	target_machine = None
	if len(target) > 0:
		logger.debug("Checking if K is appropriate for target machine")
		target_machine = load_automaton_from_file("examples/" + target, automaton_type="mealy")
		k_unsafe = True
		count = 0
		while k_unsafe:
			initialize_counting_function(target_machine, UCBWrapper)
			if checkCFSafety(target_machine, UCBWrapper):
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
			UCBWrapper = UCB(k, LTL_formula, input_atomic_propositions, output_atomic_propositions)

	logger.debug("Chosen appropriate K.")
	### STEP 2 ###
	# Merge compatible nodes
	logger.debug("Merging compatible nodes in prefix tree...")
	pairs = get_compatible_nodes(mealy_machine)
	exclude_pairs = []
	count = 1
	while len(pairs) > 0:
		pair = pairs[0]
		if is_excluded(pair, exclude_pairs):
			pairs = pairs[1:]
			continue
		mealy_machine, exclude_pairs, isMerged = merge_compatible_nodes(
			pair, exclude_pairs, mealy_machine, UCBWrapper)
		pairs = get_compatible_nodes(mealy_machine)
		if not isMerged:
			pairs = pairs[count:]
			count += 1
		else:
			count = 1

	### STEP 2.5 ###
	# Mark nodes in "pre-machine"
	mark_nodes(mealy_machine)

	logger.debug("Pre-machine complete.")
	### STEP 3 ###
	# Complete mealy machine
	complete_mealy_machine(mealy_machine, UCBWrapper)
	if target_machine is not None:
		isComp, cex = isCrossProductCompatible(target_machine, mealy_machine)
		if not isComp:
			logger.warning('Counter example: ' + ".".join(cex))
			traces.append(cex)
			logger.debug("Traces: "+ str(traces))
			return parse_json(file_name, traces, k)
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
		print("No target machine. Saving dot file...")
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

def mark_nodes(mealy_machine):
	for state in mealy_machine.states:
		state.special_node = True