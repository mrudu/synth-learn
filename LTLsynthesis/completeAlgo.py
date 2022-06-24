from aalpy.automata import MealyState, MealyMachine
import functools
from LTLsynthesis.utilities import *
import logging

logger = logging.getLogger('algo-logger')

def check_state_subsumed(state, current_state, i_bdd, UCBWrapper):
	i_str = bdd_to_str(i_bdd)
	for o_bdd in UCBWrapper.bdd_outputs:
		cf = UCBWrapper.get_transition_state(current_state.counting_function, i_bdd & o_bdd)
		o_str = bdd_to_str(o_bdd)
		if contains(cf, state.counting_function):
			logger.debug("CF subsumed by node..")
			logger.debug("Counting function of transition: " + str(cf))
			logger.debug("Counting function of next state: " + str(state.counting_function))
			logger.info("Creating edge: {} + {}/{} -> {}".format(
				current_state.state_id,
				i_str,
				o_str,
				state.state_id))
			current_state.transitions[i_str] = state
			current_state.output_fun[i_str] = o_str
			return True
	return False

def check_state_mergeable(state, current_state, i_bdd, mealy_machine, UCBWrapper):
	i_str = bdd_to_str(i_bdd)
	for o_bdd in UCBWrapper.bdd_outputs:
		o_str = bdd_to_str(o_bdd)
		current_state.transitions[i_str] = state
		current_state.output_fun[i_str] = o_str
		initialize_counting_function(mealy_machine, UCBWrapper)
		if checkCFSafety(mealy_machine, UCBWrapper):
			cf = UCBWrapper.get_transition_state(current_state.counting_function, i_bdd & o_bdd)
			logger.debug("Merging with node..")
			logger.debug("Counting function of transition: " + str(cf))
			logger.debug("Counting function of next state: " + str(state.counting_function))
			logger.info("Creating edge: {} + {}/{} -> {}".format(
				current_state.state_id,
				i_str,
				o_str,
				state.state_id))
			return True
		del current_state.transitions[i_str]
		del current_state.output_fun[i_str]
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

		logger.info("Checking state: " + str(current_state.state_id))

		if current_state == None:
			continue
		for i_bdd in UCBWrapper.bdd_inputs:
			i_str = bdd_to_str(i_bdd)
			
			logger.info("Checking transition {}, {}".format(current_state.state_id, i_str))
			
			# Checking if transition already exists
			if i_str in current_state.transitions.keys():
				next_state = current_state.transitions[i_str]
				logger.info("Transition already exists: {} , {} -> {}".format(
					current_state.state_id, i_str, next_state))
				if next_state not in visited_states:
					state_queue.append(next_state)
					visited_states.append(next_state)
				continue
			
			mergeComplete = False
			logger.debug("Counting function of origin state: " + str(current_state.counting_function))
			newly_created_nodes = sorted(newly_created_nodes, key=functools.cmp_to_key(sort_nodes))

			# Checking if there exists output where cf is subsumed by premachine state
			logger.info("Checking if there exists output where cf is subsumed by premachine/newly created state state")
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
			logger.info("Checking if spurious edge to premachine state is possible")
			for state in (premachine_nodes + newly_created_nodes):
				if check_state_mergeable(state, current_state, i_bdd, mealy_machine, UCBWrapper):
					next_state = state
					mergeComplete = True
					break

			if mergeComplete:
				if (next_state not in visited_states):
					state_queue.append(next_state)
					visited_states.append(next_state)
				continue

			initialize_counting_function(mealy_machine, UCBWrapper)
			if not checkCFSafety(mealy_machine, UCBWrapper):
				logger.warning("This mealy machine is unsuitable")
				return None

			logger.info("Will have to create a new state")
			cf_o_list = []
			for o_bdd in UCBWrapper.bdd_outputs:
				cf = UCBWrapper.get_transition_state(current_state.counting_function, i_bdd & o_bdd)
				cf_o_list.append([o_bdd, cf])

			cf_o_list = sorted(cf_o_list, key=functools.cmp_to_key(sort_list))
			for item in cf_o_list:
				o_bdd, cf = item
				if not UCBWrapper.is_safe(cf):
					continue
				o_str = bdd_to_str(o_bdd)
				next_state = MealyState("{}({}.{})".format(current_state.state_id, i_str, o_str))
				next_state.counting_function = cf
				next_state.special_node = False
				mealy_machine.states.append(next_state)
				newly_created_nodes.append(next_state)
				logger.info("Creating new state " + next_state.state_id)
				logger.debug("Counting function of transition: " + str(cf))
				logger.info("Creating edge: {} + {}/{} -> {}".format(
					current_state.state_id,
					i_str,
					o_str,
					next_state.state_id))
				current_state.transitions[i_str] = next_state
				current_state.output_fun[i_str] = o_str
				state_queue.append(next_state)
				visited_states.append(next_state)
				break

