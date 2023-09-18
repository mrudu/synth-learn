from aalpy.utils.FileHandler import visualize_automaton, \
save_automaton_to_file, load_automaton_from_file
from aalpy.automata import MealyState, MealyMachine
from LTLsynthesis.RevampCode.ucbHelperFunctions import is_safe,\
contains, get_transition_counting_function
import spot
import buddy
from flask import session

def save_mealy_machile(mealy_machine, file_name, file_type = ['dot']):
	for type in file_type:
		save_automaton_to_file(mealy_machine, file_type=type,
			path=file_name)

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
	cfs = [[-1]*num_states]*len(mealy_machine.states)
	cfs[mealy_machine.initial_state.index][ucb_init] = 0
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
	elif (sum(cf_1)) < (sum(cf_2)):
		return -1
	elif (sum(cf_1)) > (sum(cf_2)):
		return 1
	else:
		return 0

def checkCFSafety(mealy_machine: MealyMachine, ucb, antichain_vectors,
	cfs = None):
	if cfs is None:
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
		
		f_ = lowestUpperBound(get_transition_counting_function(ucb, f1,
			edge_label), f2)
		if not is_safe(antichain_vectors, f_):
			return False, cfs
		if contains(f2, f_) and f_ != f2:
			cfs[target_state.index] = f_;
			for j in target_state.transitions.keys():
				edges_to_visit.append([target_state, 
					target_state.transitions[j], str_to_bdd(j, ucb) & 
					str_to_bdd(target_state.output_fun[j], ucb)])
	return True, cfs