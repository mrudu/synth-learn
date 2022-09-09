from aalpy.automata import MealyState, MealyMachine
from LTLsynthesis.utilities import *
import LTLsynthesis.algorithm
import re

logger = logging.getLogger("algo-logger")

def trace_to_int_function(trace):
	logger.debug("Trace to int function: " + str(trace))
	ordered_inputs = LTLsynthesis.algorithm.ordered_inputs
	input_filtered_trace = list(filter(
		lambda proposition: proposition in ordered_inputs, trace))

	if len(input_filtered_trace) == 0:
		return 0
	return int(''.join(map(lambda input_proposition: str(
		ordered_inputs.index(input_proposition)+1),input_filtered_trace)))


def expand_traces(traces):
	new_traces = []
	for trace in traces:
		new_traces.extend(expand_trace(trace))
	return new_traces

def expand_trace(trace):
	bdd_inputs = LTLsynthesis.algorithm.bdd_inputs
	ucb = LTLsynthesis.algorithm.ucb
	expanded_traces = []
	for i in range(len(trace)-2, -1, -2):
		bdd_i = str_to_bdd(trace[i], ucb)
		new_traces = []
		for inp in bdd_inputs:
			if bdd_i & inp != buddy.bddfalse:
				str_i = bdd_to_str(inp)
				if len(expanded_traces) > 0:
					for t in expanded_traces:
						new_traces.append([str_i, trace[i+1]] + t)
				else:
					new_traces.append([str_i, trace[i+1]])
		expanded_traces = new_traces
	return expanded_traces

def build_prefix_tree(words):
	root = MealyState('()')
	root.level = 0
	list_nodes = [root]
	for word in words:
		current_node = root
		for i in range(0, len(word)-1, 2):
			if word[i] in current_node.transitions.keys():
				current_node = current_node.transitions[word[i]]
			else:
				new_node = MealyState(current_node.state_id + \
					"({}.{})".format(word[i],word[i+1]))
				current_node.transitions[word[i]] = new_node
				current_node.output_fun[word[i]] = word[i+1]
				current_node = new_node
				new_node.level = len(list_nodes)
				list_nodes.append(new_node)
		current_node.isEndOfWord = True
	mealyTree = MealyMachine(root, list_nodes)
	return mealyTree

def sort_nodes_by_cf_diff(node_1, node_2):
	return sum(list(abs(node_1.counting_function[i] - node_2.counting_function[i]) \
		for i in range(len(node_1.counting_function))))*-1

def sort_merge_cand_by_min_cf(node_pair_1, node_pair_2):
	node_1, node_2 = node_pair_1
	node_3, node_4 = node_pair_2

	logger.debug("Traces coming from sort merge cand: {} and {} where {} and {} are original".format(
		re.sub('[^A-Za-z0-9\.\&\!\ ]+', '.', node_1.state_id).split('.'),
		re.sub('[^A-Za-z0-9\.\&\!\ ]+', '.', node_3.state_id).split('.'),
		node_1.state_id, node_3.state_id))
	node_1_id = trace_to_int_function(filter(lambda x: len(x) > 0, 
		re.sub('[^A-Za-z0-9\.\&\!\ ]+', '.', node_1.state_id).split('.')))
	node_3_id = trace_to_int_function(filter(lambda x: len(x) > 0,
		re.sub('[^A-Za-z0-9\.\&\!\ ]+', '.', node_3.state_id).split('.')))
	if node_1_id == node_3_id:
		return sort_counting_functions(node_2.counting_function, node_4.counting_function)
	elif node_1_id < node_3_id:
		return -1
	else:
		return 1

def sort_nodes_by_traces(node_1, node_2):
	logger.debug("Traces coming from sort nodes by traces: {} and {} where {} and {} are original".format(
		re.sub('[^A-Za-z0-9\.\&\!\ ]+', '', node_1.state_id).split('.'),
		re.sub('[^A-Za-z0-9\.\&\!\ ]+', '', node_2.state_id).split('.'),
		node_1.state_id, node_2.state_id))
	node_1_id = trace_to_int_function(re.sub('[^A-Za-z0-9\.\&\!\ ]+', '.', node_1.state_id).split('.'))
	node_2_id = trace_to_int_function(re.sub('[^A-Za-z0-9\.\&\!\ ]+', '.', node_2.state_id).split('.'))

	if node_1_id < node_2_id:
		return -1
	elif node_1_id == node_2_id:
		return 0
	else:
		return 1
