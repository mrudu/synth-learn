from UCBBuilder import UCB
from aalpy.automata import MealyState, MealyMachine
import spot
import buddy
from mealyMachineBuilder import isCrossProductCompatible

def bdd_to_str(bdd_arg):
	return str(spot.bdd_to_formula(bdd_arg))

def str_to_bdd(bdd_str, ucb):
	return spot.formula_to_bdd(bdd_str, ucb.get_dict(), None)

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

def get_compatible_node(mealy_machine, exclude=[]):
	states = mealy_machine.states
	for s1 in states:
		for s2 in states:
			if s1 == s2:
				continue
			if is_excluded([s1, s2], exclude):
				continue
			m1 = MealyMachine(s1, states)
			m2 = MealyMachine(s2, states)
			isComp, cex = isCrossProductCompatible(m1, m2)
			if isComp:
				return [s1, s2]
	return None

def is_excluded(pair, exclude_pairs):
	pair1 = '{}.{}'.format(pair[0].state_id, pair[1].state_id)
	pair2 = '{}.{}'.format(pair[1].state_id, pair[0].state_id)
	exclude_pairs = list(map(lambda x: '{}.{}'.format(x[0].state_id, x[1].state_id), exclude_pairs))
	return pair1 in exclude_pairs or pair2 in exclude_pairs

def initialize_counting_function(mealy, n):
	for state in mealy.states:
		state.counting_function = [-1]*n;
	mealy.initial_state.counting_function[0] = 0



