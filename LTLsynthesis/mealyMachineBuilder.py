from aalpy.automata import MealyState, MealyMachine
from LTLsynthesis.utilities import *
from LTLsynthesis.prefixTreeBuilder import *
import copy, functools, logging

logger = logging.getLogger("misc-logger")

def isCrossProductCompatible(m1: MealyMachine, m2: MealyMachine):
	# Building Cross Product
	ts = time.time()

	root = (m1.initial_state, m2.initial_state)
	state_queue = [(root, [])]
	visited_states = set()
	while len(state_queue) > 0:
		state, trace = state_queue[0]
		state_queue = state_queue[1:]
		s1, s2 = state
		visited_states.add(s1.state_id + " & " + s2.state_id)
		for i in s1.transitions.keys():
			if i in s2.transitions.keys():
				trace_ = trace + [i, s1.output_fun[i]]
				transition_state = (s1.transitions[i], s2.transitions[i])
				s3, s4 = transition_state
				if s3.state_id + " & " + s4.state_id not in visited_states:
					if s1.output_fun[i] != s2.output_fun[i]:
						logger.debug("Checking compatibilty takes: " + str(time.time() - ts))
						logger.debug("Obtained counter-example: ", str(trace_))
						return [False, trace_]
				state_queue.append((transition_state, trace_))
	logger.debug("Checking compatibilty takes : " + str(time.time() - ts))
	return [True, []]

def generalization_algorithm(premealy_machine, merging_strategy, UCBWrapper):
	states = sorted(premealy_machine.states, 
		key=functools.cmp_to_key(sort_nodes_by_traces))
	exclude_pairs = []
	i = 0
	while i < len(states):
		s = states[i]
		logger.debug("Checking state {}".format(s.state_id))
		
		merge_pairs = get_compatible_nodes(states, s, exclude_pairs)
		merge_pairs = sorted(merge_pairs, key=functools.cmp_to_key(merging_strategy))
		
		while (len(merge_pairs) > 0):
			merge_pair = merge_pairs[0]
			merge_pairs = merge_pairs[1:]
			if is_excluded(merge_pair, exclude_pairs):
				continue
			ts = time.time()
			premealy_machine, exclude_pairs, isMerged = merge_compatible_nodes(
			merge_pair, exclude_pairs, premealy_machine, UCBWrapper)
			logger.debug("Merge took {} time".format(time.time()-ts))
			if isMerged:
				logger.debug("Merged {} into {}".format(merge_pair[0].state_id, 
					merge_pair[1].state_id))
				states = sorted(premealy_machine.states,
					key=functools.cmp_to_key(sort_nodes_by_traces))
				logger.debug("# of states: {}".format(len(states)))
				break
			logger.debug("Merge {} and {} failed".format(merge_pair[0].state_id,
				merge_pair[1].state_id))
		if get_index_from_id(s.state_id, states) is None:
			print('error')
			i = i + 1
		else:
			i = get_index_from_id(s.state_id, states) + 1
	return premealy_machine

def get_compatible_nodes(states, s, exclude=[]):
	pair_nodes = []
	for s_ in states:
		if s == s_:
			break
		if s.state_id == s_.state_id:
			break
		if is_excluded([s, s_], exclude):
			logger.debug("Excluding {} and {}".format(s, s_))
			continue
		m1 = MealyMachine(s, states)
		m2 = MealyMachine(s_, states)
		isComp, cex = isCrossProductCompatible(m1, m2)
		if isComp:
			pair_nodes.append([s, s_])
		else:
			logger.info("Counter example for merge: " + ".".join(cex))
	logger.debug("Returning {} pairs of potentially mergeable nodes".format(len(pair_nodes)))
	# pair_nodes = sorted(pair_nodes, key=lambda x: sort_nodes_by_cf_diff(x[0], x[1]))
	return pair_nodes

def merge_compatible_nodes(pair, exclude_pairs, mealy_machine, 
	UCBWrapper):
	old_mealy_machine = copy.deepcopy(mealy_machine)
	merged = False
	pair[0] = get_state_from_id(pair[0].state_id, mealy_machine.states)
	pair[1] = get_state_from_id(pair[1].state_id, mealy_machine.states)
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
