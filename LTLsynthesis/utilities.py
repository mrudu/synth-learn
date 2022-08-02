import spot, logging
from aalpy.automata import MealyState, MealyMachine
import buddy

logger = logging.getLogger('algo-logger')

def initialize_counting_function(mealy, UCBWrapper):
	for state in mealy.states:
		state.counting_function = [-1]*UCBWrapper.num_states;
	mealy.initial_state.counting_function[UCBWrapper.ucb.get_init_state_number()] = 0

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
		logger.debug("Exploring edge: {} + {}/{} -> {}".format(state.state_id, i, state.output_fun[i], target_state.state_id))
		f1 = state.counting_function
		f2 = target_state.counting_function


		# logger.debug("Origin state CF: " + str(f1))
		# logger.debug("Transition state CF: " + str(f2))

		i_bdd = str_to_bdd(i, UCBWrapper.ucb)
		o_bdd = str_to_bdd(state.output_fun[i], UCBWrapper.ucb)
		
		f_ = lowestUpperBound(UCBWrapper.get_transition_state(f1, 
			i_bdd & o_bdd), f2)
		# logger.debug("Lowest Upper Bound: " + str(f_))
		if not UCBWrapper.is_safe(f_):
			return False
		if contains(f2, f_) and f_ != f2:
			# logger.debug("Target state reset")
			target_state.counting_function = f_;
			for j in target_state.transitions.keys():
				edges_to_visit.append([target_state, j])
		# else:
			# logger.debug("Target state remains")
	return True

def get_state_from_id(state_id, state_list):
	for state in state_list:
		stateMatches = True
		for i in range(len(state_id)):
			if state.state_id[i] != state_id[i]:
				stateMatches = False
				break
		if stateMatches:
			return state
	return None

def bdd_to_str(bdd_arg):
	return str(spot.bdd_to_formula(bdd_arg))

def str_to_bdd(bdd_str, ucb):
	return spot.formula_to_bdd(bdd_str, ucb.get_dict(), None)

def contains(vector_1, vector_2):
	if vector_1 == None or vector_2 == None:
		return False
	for i in range(len(vector_1)):
		if vector_1[i] > vector_2[i]:
			return False
	return True

def sort_counting_functions(cf_1, cf_2):
	if contains(cf_1, cf_2):
		return -1
	elif contains(cf_2, cf_1):
		return 1
	elif max(cf_1) < max(cf_2):
		return -1
	elif max(cf_1) > max(cf_2):
		return 1
	elif (sum(cf_1)) < (sum(cf_2)):
		return -1
	elif (sum(cf_1)) > (sum(cf_2)):
		return 1
	else:
		return 0

def lowestUpperBound(vector_1, vector_2):
	vector = []
	for i in range(len(vector_1)):
		if vector_1[i] > vector_2[i]:
			vector.append(vector_1[i])
		else:
			vector.append(vector_2[i])
	return vector

def cleaner_display(mealy_machine, ucb):
	for state in mealy_machine.states:
		grouped_transitions = {}
		for i, output_state in state.transitions.items():
			grouped_transitions[output_state] = [i] if output_state not in grouped_transitions.keys() else grouped_transitions[output_state] + [i]

		to_remove = []
		for output_state, input_set in grouped_transitions.items():
			for o in set(state.output_fun.values()):
				bdd_max = buddy.bddfalse
				str_inp = ""
				common_inp = []
				for i in input_set:
					if state.output_fun[i] == o:
						bdd_max = bdd_max | str_to_bdd(i, ucb)
						str_inp = str_inp + i + " + "
						common_inp.append(i)
				i_max = bdd_to_str(bdd_max)
				if i_max != "0" and len(common_inp) > 1:
					print("For the state, output {} {}: {} gives {}".format(
						state.state_id, o, str_inp, i_max))
					to_remove.extend(common_inp)
					state.transitions[i_max] = output_state
					state.output_fun[i_max] = o
		for i in to_remove:
			if i in state.transitions.keys():
				del state.transitions[i]


def is_excluded(pair, exclude_pairs):
	pair1 = '{}.{}'.format(pair[0].state_id, pair[1].state_id)
	pair2 = '{}.{}'.format(pair[1].state_id, pair[0].state_id)
	exclude_pairs = list(map(lambda x: '{}.{}'.format(x[0].state_id, x[1].state_id), exclude_pairs))
	return pair1 in exclude_pairs or pair2 in exclude_pairs