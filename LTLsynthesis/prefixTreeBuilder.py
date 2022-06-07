from aalpy.automata import MealyState, MealyMachine
from LTLsynthesis.utilities import *
import functools

def sort_trace_function(trace, ordered_inputs):
	input_filtered_trace = list(filter(
		lambda proposition: proposition in ordered_inputs, trace))
	return int(''.join(map(lambda input_proposition: str(
		ordered_inputs.index(input_proposition)+1),input_filtered_trace)))

def build_prefix_tree(words):
	root = MealyState('() LEVEL:0')
	root.level = 0
	list_nodes = [root]
	for word in words:
		current_node = root
		for i in range(0, len(word)-1, 2):
			if word[i] in current_node.transitions.keys():
				current_node = current_node.transitions[word[i]]
			else:
				new_node = MealyState(current_node.state_id + \
					"({}.{}) LEVEL:{}".format(word[i],word[i+1], len(list_nodes)))
				current_node.transitions[word[i]] = new_node
				current_node.output_fun[word[i]] = word[i+1]
				current_node = new_node
				new_node.level = len(list_nodes)
				list_nodes.append(new_node)
		current_node.isEndOfWord = True
	mealyTree = MealyMachine(root, list_nodes)
	return mealyTree

def sort_distance_nodes(node_1, node_2):
	return sum(list(abs(node_1.counting_function[i] - node_2.counting_function[i]) \
		for i in range(len(node_1.counting_function))))*-1

def sort_min_cf(node_pair_1, node_pair_2):
	node_1, node_2 = node_pair_1
	node_3, node_4 = node_pair_2
	if node_1.level == node_3.level:
		return sort_counting_functions(node_2.counting_function, node_4.counting_function)
	elif node_1.level < node_3.level:
		return -1
	else:
		return 1

def checkCFSafety(mealy: MealyMachine, UCBWrapper):
	# Checking CF Safety of the new Mealy Machine
	if not UCBWrapper.is_safe(mealy.initial_state.counting_function):
		return False
	
	edges_to_visit = []

	for i in mealy.initial_state.transitions.keys():
		edges_to_visit.append([mealy.initial_state, i])
	
	count = 0
	while len(edges_to_visit) > 0:
		state, i = edges_to_visit[0]
		target_state = state.transitions[i]
		edges_to_visit = edges_to_visit[1:]
		f1 = state.counting_function
		f2 = target_state.counting_function

		i_bdd = str_to_bdd(i, UCBWrapper.ucb)
		o_bdd = str_to_bdd(state.output_fun[i], UCBWrapper.ucb)
		
		f_ = lowestUpperBound(UCBWrapper.get_transition_state(f1, 
			i_bdd & o_bdd), f2)
		if not UCBWrapper.is_safe(f_):
			return False
		if contains(f2, f_) and f_ != f2:
			target_state.counting_function = f_;
			for j in target_state.transitions.keys():
				edges_to_visit.append([target_state, j])
	return True

def initialize_counting_function(mealy, UCBWrapper):
	for state in mealy.states:
		state.counting_function = [-1]*UCBWrapper.num_states;
	mealy.initial_state.counting_function[UCBWrapper.ucb.get_init_state_number()] = 0



