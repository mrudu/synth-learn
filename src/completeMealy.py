from aalpy.automata import MealyMachine, MealyState
from src.utils import checkCFSafety, bdd_to_str, compare_cfs
from src.ucbHelperFunctions import get_transition_counting_function, contains
import spot, operator, functools
from src.rpni import pretty_print

def complete_mealy_machine(mealy_machine: MealyMachine, ucb,
	antichain_vectors):
	x = 0
	safe, cfs = checkCFSafety(mealy_machine, ucb, antichain_vectors)
	while x < len(mealy_machine.states):
		state = mealy_machine.states[x]
		x += 1
		for bdd_i in ucb.bdd_inputs:
			i = bdd_to_str(bdd_i)
			if state.transitions.get(i) is None:
				ucb.bdd_outputs = rank_outputs(cfs[state.index], 
					bdd_i, ucb)
				edgeAdded, cfs = connect_to_state(state, i, mealy_machine, ucb, 
					antichain_vectors)
				if not edgeAdded:
					new_state = MealyState(state.state_id)
					new_state.index = len(mealy_machine.states)
					state.transitions[i] = new_state
					mealy_machine.states.append(new_state)
					for bdd_o in ucb.bdd_outputs:
						o = bdd_to_str(bdd_o)
						state.output_fun[i] = o
						safe, cfs = checkCFSafety(mealy_machine, ucb, 
							antichain_vectors)
						if safe:
							new_state.state_id += "#{}.{}".format(i,o)
							break

def rank_outputs(state_vector, bdd_i, ucb):
	cfs_bdds= []
	for bdd_o in ucb.bdd_outputs:
		cf = get_transition_counting_function(ucb, state_vector, 
			bdd_i & bdd_o)
		cfs_bdds.append([cf, bdd_o])
	cfs_bdds = sorted(cfs_bdds, key=functools.cmp_to_key(lambda x,y:
		compare_cfs(x[0], y[0])))
	return [c_b[1] for c_b in cfs_bdds]

# Find target state to add edge (state,i)
# We check for safety here and return True if successful
def connect_to_state(state, i, mealy_machine, ucb, ac_vecs):
	for target_state in mealy_machine.states:
		state.transitions[i] = target_state
		for bdd_o in ucb.bdd_outputs:
			state.output_fun[i] = bdd_to_str(bdd_o)
			safe, cfs = checkCFSafety(mealy_machine, ucb, 
				ac_vecs)
			if safe:
				return True, cfs
			del state.output_fun[i]
		del state.transitions[i]
	return False, cfs
