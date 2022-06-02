from UCBBuilder import UCB
from aalpy.automata import MealyState, MealyMachine
import spot
import buddy
from mealyMachineBuilder import isCrossProductCompatible
from functools import cmp_to_key

def bdd_to_str(bdd_arg):
	return str(spot.bdd_to_formula(bdd_arg))

def str_to_bdd(bdd_str, ucb):
	return spot.formula_to_bdd(bdd_str, ucb.get_dict(), None)

def sort_trace_function(trace, ordered_inputs):
	input_filtered_trace = list(filter(
		lambda proposition: proposition in ordered_inputs, trace))
	return ''.join(map(lambda input_proposition: str(
		ordered_inputs.index(input_proposition)),input_filtered_trace))

def build_prefix_tree(words):
	root = MealyState('()')
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
				list_nodes.append(new_node)
		current_node.isEndOfWord = True
	mealyTree = MealyMachine(root, list_nodes)
	return mealyTree

def distance_nodes(node_1, node_2):
	return sum(list(abs(node_1.counting_function[i] - node_2.counting_function[i]) \
		for i in range(len(node_1.counting_function))))*-1

def get_compatible_node(mealy_machine, exclude=[]):
	states = mealy_machine.states
	pair_nodes = []
	for s1 in states:
		for s2 in states:
			if s1 == s2:
				continue
			if s1.state_id == s2.state_id:
				continue
			if is_excluded([s1, s2], exclude):
				continue
			if [s2, s1] in pair_nodes:
				continue
			m1 = MealyMachine(s1, states)
			m2 = MealyMachine(s2, states)
			isComp, cex = isCrossProductCompatible(m1, m2)
			if isComp:
				pair_nodes.append([s1, s2])
	pair_nodes = sorted(pair_nodes, key=lambda x: distance_nodes(x[0], x[1]))
	return pair_nodes

def is_excluded(pair, exclude_pairs):
	pair1 = '{}.{}'.format(pair[0].state_id, pair[1].state_id)
	pair2 = '{}.{}'.format(pair[1].state_id, pair[0].state_id)
	exclude_pairs = list(map(lambda x: '{}.{}'.format(x[0].state_id, x[1].state_id), exclude_pairs))
	return pair1 in exclude_pairs or pair2 in exclude_pairs

def initialize_counting_function(mealy, UCBWrapper):
	for state in mealy.states:
		state.counting_function = [-1]*UCBWrapper.num_states;
	mealy.initial_state.counting_function[UCBWrapper.ucb.get_init_state_number()] = 0



