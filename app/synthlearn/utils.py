from aalpy.automata import MealyState, MealyMachine
from app.synthlearn.ucbHelperFunctions import is_safe, contains, get_transition_counting_function
import spot
import buddy
from flask import session
import functools, time, logging

logger = logging.getLogger('miscLogger')

def reinitialize_index(mealy_machine):
	# Reindexing based on length of prefixes
	root = mealy_machine.initial_state
	count = 0
	visited_states = []
	state_queue = [root]
	root.state_id = "e"
	while len(state_queue) > 0:
		curr = state_queue.pop(0)
		visited_states.append(curr)
		curr.index = count
		count += 1
		for i in curr.transitions.keys():
			if curr.transitions[i] not in visited_states + state_queue:
				state_queue.append(curr.transitions[i])
				curr.transitions[i].state_id = curr.state_id + "#{}.{}".format(i, curr.output_fun[i])
	mealy_machine.states = visited_states

def expand_symbolic_trace(trace, ucb):
	bdd_inputs = ucb.bdd_inputs
	expanded_traces = [[]]
	for i in range(0, len(trace), 2):
		bdd_i = str_to_bdd(trace[i], ucb)
		update_traces_set = []
		for inp in bdd_inputs:
			if bdd_i & inp != buddy.bddfalse:
				for t in expanded_traces:
					update_traces_set.append(t + [bdd_to_str(inp), trace[i+1]])
		expanded_traces = update_traces_set
	return expanded_traces

def lowestUpperBound(v1, v2):
	v = []
	for i in range(len(v1)):
		if v1[i] > v2[i]:
			v.append(v1[i])
		else:
			v.append(v2[i])
	return v

def str_to_bdd(bdd_str, ucb):
	return spot.formula_to_bdd(bdd_str, ucb.get_dict(), None)

def bdd_to_str(bdd_input):
	return str(spot.bdd_to_formula(bdd_input))

def initialize_cf(mealy_machine, num_states, ucb_init):
	cfs = []
	for c in range(len(mealy_machine.states)):
		cfs.append([-1]*num_states)
	x = cfs[mealy_machine.initial_state.index]
	x[ucb_init] = 0
	return cfs

def compare_cfs(cf_1, cf_2):
	if contains(cf_1, cf_2):
		return -1
	elif contains(cf_2, cf_1):
		return 1
	elif max(cf_1) < max(cf_2):
		return -1
	elif max(cf_1) > max(cf_2):
		return 1
	else:
		return 0

def mergeEdges(mealy_machine: MealyMachine, ucb):
	for state in mealy_machine.states:
		state.state_id = str(state.index)
		common_outputs = set(["{}#{}".format(state.transitions[i].index, 
			state.output_fun[i]) for i in state.transitions.keys()])
		merge_transitions = dict()
		merge_outputs = dict()
		for state_output in common_outputs:
			state_index, output = state_output.split('#')
			state_index = int(state_index)
			inputs = [str_to_bdd(i, ucb) for i,o in 
				state.output_fun.items() if o == output and 
				state.transitions[i].index == state_index]
			merged_input = bdd_to_str(functools.reduce(
				lambda a,b: a | b, inputs))
			merge_transitions[merged_input] = mealy_machine.states[
				state_index]
			merge_outputs[merged_input] = output
		state.transitions = merge_transitions
		state.output_fun = merge_outputs

def cfThenPrefix(np_1, np_2):
	s1, cf_1 = np_1
	s2, cf_2 = np_2
	score = compare_cfs(cf_1, cf_2)
	if score != 0:
		return score
	if len(s1.state_id) > len(s2.state_id):
		return 1
	else:
		return -1

def prefixThenCF(np_1, np_2):
	s1, cf_1 = np_1
	s2, cf_2 = np_2
	score = compare_cfs(cf_1, cf_2)
	if len(s1.state_id) > len(s2.state_id):
		return 1
	elif len(s1.state_id) < len(s2.state_id):
		return -1
	else:
		return compare_cfs(cf_1, cf_2)

def sort_nodes(mealy_machine: MealyMachine, nodes, cfs, merging_strategy):
	node_cf_pair = []
	for node in nodes:
		node_cf_pair.append([mealy_machine.states[node], cfs[node]])
	node_cf_pair = sorted(node_cf_pair, key=functools.cmp_to_key(merging_strategy))
	return [np[0].index for np in node_cf_pair]

def checkCFSafety(mealy_machine: MealyMachine, ucb, antichain_vectors, cfs = None):
	
	cfs = initialize_cf(mealy_machine, ucb.num_states(), 
	ucb.get_init_state_number())
	
	# Checking safety of initial state
	mm_init = mealy_machine.initial_state
	if not is_safe(antichain_vectors, cfs[mm_init.index]):
		return False, cfs
	
	edges_to_visit = []

	for i in mm_init.transitions.keys():
		edges_to_visit.append([mm_init, mm_init.transitions[i], 
			str_to_bdd(i, ucb) & str_to_bdd(mm_init.output_fun[i], ucb)])

	while len(edges_to_visit) > 0:
		state, target_state, edge_label = edges_to_visit.pop(0)
		f1 = cfs[state.index]
		f2 = cfs[target_state.index]
		logger.debug("Source State : {}, CF: {}".format(state.state_id, f1))
		logger.debug("Target State : {}, CF: {}".format(target_state.state_id, f2))
		logger.debug("Edge: {}".format(edge_label))
		
		f_ = lowestUpperBound(get_transition_counting_function(ucb, f1,
			edge_label), f2)
		logger.debug("Transition CF: {}, LUB: {}".format(
			get_transition_counting_function(ucb, f1,
			edge_label), f_))
		if not is_safe(antichain_vectors, f_):
			logger.debug("Unsafe")
			return False, cfs
		if contains(f2, f_) and f_ != f2:
			cfs[target_state.index] = f_;
			for j in target_state.transitions.keys():
				edges_to_visit.append([target_state, 
					target_state.transitions[j], str_to_bdd(j, ucb) & 
					str_to_bdd(target_state.output_fun[j], ucb)])
				logger.debug("Adding edge: {}, {}".format(target_state.state_id, j))
	return True, cfs