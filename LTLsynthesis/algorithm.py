from CustomAALpy.FileHandler import visualize_automaton, save_automaton_to_file, load_automaton_from_file
import logging
from flask import session
from functools import reduce
from LTLsynthesis.prefixTreeBuilder import build_prefix_tree, checkCFSafety
from LTLsynthesis.mealyMachineBuilder import isCrossProductCompatible, generalization_algorithm
from LTLsynthesis.completion_phase import complete_mealy_machine
from LTLsynthesis.utilities import *
from LTLsynthesis.UCBBuilder import UCB

logger = logging.getLogger("misc-logger")

def build_mealy(LTL_formula, I, O, traces, file_name, target, k = 2):	
	global ordered_inputs, bdd_inputs, ucb, UCBWrapper

	### STEP 1 ###

	# Check if K is appropriate
	logger.debug("Checking if K is appropriate...")

	logger.debug("Checking if K is appropriate for LTL")
	k_unsafe = True
	UCBWrapper = UCB(k, LTL_formula, I, O)
	while UCBWrapper.ucb is None:
		logger.debug("LTL Specification is unsafe for k=" + str(k))
		k = k + 1
		UCBWrapper = UCB(k, LTL_formula, I, O)
	
	logger.info("LTL Specification is safe for k=" + str(k))
	bdd_inputs = UCBWrapper.bdd_inputs
	ucb = UCBWrapper.ucb

	# Build Prefix Tree Mealy Machine
	logger.info("Building Prefix Tree Mealy Machine...")
	mealy_machine = build_prefix_tree(traces)

	logger.info("Prefix Tree Mealy Machine built")

	# Check if K is appropriate for traces
	logger.debug("Checking if K is appropriate for traces")
	while k_unsafe:
		initialize_counting_function(mealy_machine, UCBWrapper)
		if checkCFSafety(mealy_machine):
			logger.info("Traces is safe for k=" + str(k))
			k_unsafe = False
			break
		k = k + 1
		logger.debug("Traces is unsafe for k=" + str(k))
		UCBWrapper = UCB(k, LTL_formula, I, O)

	# Loading the target machine if it exists
	target_machine = None
	if len(target) > 0:
		logger.debug("Checking if K is appropriate for target machine")
		target_machine = load_automaton_from_file(target)
		save_mealy_machile(target_machine, "static/temp_model_files/TargetModel", ['svg', 'pdf'])

	logger.info("Finally, chosen K as " + str(k))
	
	### STEP 2 ###
	# Merge compatible nodes
	logger.debug("Merging compatible nodes in prefix tree...")
	mealy_machine = generalization_algorithm(mealy_machine, sort_merge_cand_by_min_cf, UCBWrapper)

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
			logger.info("Traces: "+ str(traces))

			return build_mealy(
				LTL_formula, 
				I, 
				O, traces, 
				file_name, target, k)
	
	save_mealy_machile(mealy_machine, "static/temp_model_files/LearnedModel", ['dot'])
	cleaner_display(mealy_machine, UCBWrapper.ucb)
	save_mealy_machile(mealy_machine, "static/temp_model_files/LearnedModel", ['svg', 'pdf'])
	print_data(target_machine, mealy_machine, num_premachine_nodes, traces, k, UCBWrapper)
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