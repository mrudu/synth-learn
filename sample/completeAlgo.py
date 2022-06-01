from aalpy.automata import MealyState, MealyMachine
from prefixTreeBuilder import *
from mealyMachineBuilder import checkCFSafety
import functools

import logging

logger = logging.getLogger('algo-logger')
def v_print(message):
	logger.info(message)

def checkIfSubsumed(cf, cf_list):
	for cf_ in cf_list:
		if contains(cf, cf_[0]):
			return cf_
	return None

def contains(vector_1, vector_2):
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

def check_state_subsumed(state, current_state, i_bdd, UCBWrapper):
	i_str = bdd_to_str(i_bdd)
	for o_bdd in UCBWrapper.bdd_outputs:
		cf = UCBWrapper.get_transition_state(current_state.counting_function, i_bdd & o_bdd)
		o_str = bdd_to_str(o_bdd)
		if contains(cf, state.counting_function):
			current_state.transitions[i_str] = state
			current_state.output_fun[i_str] = o_str
			return True
	return False

def check_state_mergeable(state, current_state, i_bdd, mealy_machine, UCBWrapper):
	i_str = bdd_to_str(i_bdd)
	for o_bdd in UCBWrapper.bdd_outputs:
		current_state.transitions[i_str] = state
		current_state.output_fun[i_str] = bdd_to_str(o_bdd)
		initialize_counting_function(mealy_machine, UCBWrapper)
		if checkCFSafety(mealy_machine, UCBWrapper):
			return True
	return False

def sort_list(item_1, item_2):
	return sort_counting_functions(item_1[1], item_2[1])

def sort_nodes(node_1, node_2):
	return sort_counting_functions(node_1.counting_function, node_2.counting_function)

def complete_mealy_machine(mealy_machine, UCBWrapper):
	newly_created_nodes = []
	premachine_nodes = []
	
	for state in mealy_machine.states:
		if state.special_node:
			premachine_nodes.append(state)
		else:
			newly_created_nodes.append(state)

	state_queue = [mealy_machine.initial_state]
	visited_states = [mealy_machine.initial_state]
	premachine_nodes = sorted(premachine_nodes, key=functools.cmp_to_key(sort_nodes))

	while len(state_queue) > 0:
		current_state = state_queue[0]
		state_queue = state_queue[1:]
		next_state = None

		v_print("Checking state: " + str(current_state.state_id))

		if current_state == None:
			continue
		for i_bdd in UCBWrapper.bdd_inputs:
			i_str = bdd_to_str(i_bdd)
			
			v_print("Checking transition {}, {}".format(current_state.state_id, i_str))
			
			# Checking if transition already exists
			if i_str in current_state.transitions.keys():
				next_state = current_state.transitions[i_str]
				v_print("Transition already exists: {} , {} -> {}".format(
					current_state.state_id, i_str, next_state))
				if next_state not in visited_states:
					state_queue.append(next_state)
					visited_states.append(next_state)
				continue
			
			mergeComplete = False

			# Checking if there exists output where cf is subsumed by premachine state
			v_print("Checking if there exists output where cf is subsumed by premachine state")
			for state in (premachine_nodes + newly_created_nodes):
				if check_state_subsumed(state, current_state, i_bdd, UCBWrapper):
					next_state = state
					mergeComplete = True
					break

			if mergeComplete:
				if next_state not in visited_states:
					state_queue.append(next_state)
					visited_states.append(next_state)
				continue

			# Checking if spurious edge to premachine state is possible
			v_print("Checking if spurious edge to premachine state is possible")
			for state in (premachine_nodes + newly_created_nodes):
				if check_state_mergeable(state, current_state, i_bdd, mealy_machine, UCBWrapper):
					next_state = state
					mergeComplete = True
					break

			if mergeComplete and (next_state not in visited_states):
				state_queue.append(next_state)
				visited_states.append(next_state)
				continue

			v_print("Will have to create a new state")
			cf_o_list = []
			for o_bdd in UCBWrapper.bdd_outputs:
				cf = UCBWrapper.get_transition_state(current_state.counting_function, i_bdd & o_bdd)
				cf_o_list.append([o_bdd, cf])

			cf_o_list = sorted(cf_o_list, key=functools.cmp_to_key(sort_list))
			for item in cf_o_list:
				o_bdd, cf = item
				if not UCBWrapper.is_safe(cf):
					continue
				next_state = MealyState("{}({}.{})".format(current_state.state_id, i_str, bdd_to_str(o_bdd)))
				next_state.counting_function = cf
				next_state.special_node = False
				mealy_machine.states.append(next_state)
				newly_created_nodes.append(next_state)
				current_state.transitions[i_str] = next_state
				current_state.output_fun[i_str] = bdd_to_str(o_bdd)
				state_queue.append(next_state)
				visited_states.append(next_state)
				v_print("Creating new state " + next_state.state_id)

