from aalpy.automata import MealyState, MealyMachine
from LTLsynthesis.utilities import *
from LTLsynthesis.prefixTreeBuilder import *
import copy, functools, logging

logger = logging.getLogger("algo-logger")

def isCrossProductCompatible(m1: MealyMachine, m2: MealyMachine):
	# Building Cross Product
	states = []
	for s1 in m1.states:
		for s2 in m2.states:
			states.append(MealyState([s1, s2]))
	root = get_state_from_id([m1.initial_state, m2.initial_state], states)
	for state in states:
		s1 = state.state_id[0]
		s2 = state.state_id[1]
		state.bad_state = False
		state.score = 0
		state.cex = []
		for i in s1.transitions.keys():
			if i in s2.transitions.keys():
				state.score += 1
				transition_state_id = [s1.transitions[i], s2.transitions[i]]
				transition_state = get_state_from_id(transition_state_id, states)
				state.transitions[i] = transition_state
				if s1.output_fun[i] != s2.output_fun[i]:
					state.bad_state = True
					state.expected_trace = [i, s1.output_fun[i]]
	
	state_queue = [root]
	visited_states = [root]
	if root.bad_state:
		return [False, root.expected_trace]
	while len(state_queue) > 0:
		state = state_queue[0]
		state_queue = state_queue[1:]
		for i in state.transitions.keys():
			s1 = state.state_id[0]
			s2 = state.state_id[1]
			transition_state = state.transitions[i]
			transition_state.cex = state.cex + [i, state.state_id[0].output_fun[i]]
			if transition_state not in visited_states:
				state_queue.append(transition_state)
				visited_states.append(transition_state)
				if transition_state.bad_state:
					return [False, transition_state.cex + transition_state.expected_trace]
	return [True, None]

def get_compatible_nodes(mealy_machine, exclude=[]):
	states = sorted(mealy_machine.states, key=functools.cmp_to_key(sort_nodes_by_traces))
	pair_nodes = []
	for s1 in states:
		for s2 in states:
			if s1 == s2:
				break
			if s1.state_id == s2.state_id:
				break
			if is_excluded([s1, s2], exclude):
				continue
			m1 = MealyMachine(s1, states)
			m2 = MealyMachine(s2, states)
			isComp, cex = isCrossProductCompatible(m1, m2)
			if isComp:
				pair_nodes.append([s1, s2])
	pair_nodes = sorted(pair_nodes, key=functools.cmp_to_key(sort_merge_cand_by_min_cf))
	logger.debug("Returning {} pairs of potentially mergeable nodes".format(len(pair_nodes)))
	# pair_nodes = sorted(pair_nodes, key=lambda x: sort_nodes_by_cf_diff(x[0], x[1]))
	return pair_nodes

def merge_compatible_nodes(pair, exclude_pairs, mealy_machine, 
	UCBWrapper):
	old_mealy_machine = copy.deepcopy(mealy_machine)
	merged = False
	mealy_machine = mergeAndPropogate(pair[0], pair[1], mealy_machine)
	if mealy_machine is None:
		mealy_machine = old_mealy_machine
		exclude_pairs.append(pair)
	else:
		initialize_counting_function(mealy_machine, UCBWrapper)
		if not checkCFSafety(mealy_machine):
			mealy_machine = old_mealy_machine
			exclude_pairs.append(pair)
		else:
			exclude_pairs = []
			merged = True
	return [mealy_machine, exclude_pairs, merged]

def mergeAndPropogate(s1: MealyState, s2: MealyState, mealy_machine: MealyMachine):
	propogate_queue = [[s1, s2]]
	while len(propogate_queue) > 0:
		s1, s2 = propogate_queue[0]
		logger.debug("Commence merge of {} and {}:".format(s1.state_id, s2.state_id))
		propogate_queue = propogate_queue[1:]
		if s1 == s2:
			continue
		while s1 not in mealy_machine.states:
			logger.debug(s1.state_id + " has been deleted.")
			s1 = s1.mergedFrom
		while s2 not in mealy_machine.states:
			logger.debug(s2.state_id + " has been deleted.")
			s2 = s2.mergedFrom
		mergedStuff = mergeOperation(s1, s2, mealy_machine)
		if mergedStuff is not None:
			logger.debug("Adding to queue:")
			for pair in mergedStuff:
				logger.debug("[{}, {}]".format(pair[0].state_id, pair[1].state_id))
			propogate_queue.extend(mergedStuff)
			s2.mergedFrom = s1
			mealy_machine.states.remove(s2)
		else:
			logger.debug("Merge failed! Exiting..")
			return None
		if s2 == mealy_machine.initial_state:
			mealy_machine.initial_state = s1
	return mealy_machine


def mergeOperation(s1: MealyState, s2: MealyState, mealy_machine: MealyMachine):
	merge_next = []
	for state in mealy_machine.states:
		for i in state.transitions.keys():
			if state.transitions[i] == s2:
				state.transitions[i] = s1
	for i in s2.transitions.keys():
		if i in s1.transitions.keys():
			if s1.output_fun[i] == s2.output_fun[i]:
				merge_next.append([s1.transitions[i], s2.transitions[i]])
			else:
				logger.debug("Output of transition differs here: {} ->{}/{} and {} ->{}/{}".format(
					s1.state_id, i, s1.output_fun[i], s2.state_id, i, s2.output_fun[i]))
				return None
		else:
			s1.transitions[i] = s2.transitions[i]
			s1.output_fun[i] = s2.output_fun[i]
	return merge_next
