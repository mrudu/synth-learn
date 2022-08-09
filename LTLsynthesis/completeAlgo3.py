from aalpy.automata import MealyState, MealyMachine
import functools
from LTLsynthesis.utilities import *
from LTLsynthesis.completionUtilities import check_state_subsumed, subsume_to_antichain_head, sort_list, sort_nodes
import logging

logger = logging.getLogger('algo-logger')

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

			# Checking if there exists output where cf is subsumed by premachine state
			logger.info("Checking if there exists output where cf is subsumed by a newly created state")
			for state in (newly_created_nodes):
				if check_state_subsumed(state, current_state, i_bdd, UCBWrapper):
					next_state = state
					mergeComplete = True
					break

			if mergeComplete:
				if next_state not in visited_states:
					state_queue.append(next_state)
					visited_states.append(next_state)
				continue

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
				subsume_to_antichain_head(next_state, UCBWrapper)
				break

