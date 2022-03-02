from aalpy.automata import MealyState, MealyMachine
import spot
from aalpy.utils import visualize_automaton

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

def lowestUpperBound(vector_1, vector_2):
	vector = []
	for i in range(len(vector_1)):
		if vector_1[i] > vector_2[i]:
			vector.append(vector_1[i])
		else:
			vector.append(vector_2[i])
	return vector

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
		for i in s1.transitions.keys():
			if i in s2.transitions.keys():
				transition_state_id = [s1.transitions[i], s2.transitions[i]]
				transition_state = get_state_from_id(transition_state_id, states)
				state.transitions[i] = transition_state
				if s1.output_fun[i] != s2.output_fun[i]:
					state.bad_state = True

	
	visited_states = []
	visited_states.append(root)
	if root.bad_state:
		return False
	stateAdded = True
	while stateAdded:
		stateAdded = False
		for state in visited_states:
			for i in state.transitions.keys():
				transition_state = state.transitions[i]
				if transition_state not in visited_states:
					stateAdded = True
					if transition_state.bad_state:
						return False
					visited_states.append(transition_state)
	return True

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
		transition_state = state.transitions[i]
		edges_to_visit = edges_to_visit[1:]
		f1 = state.counting_function
		f2 = transition_state.counting_function

		i_bdd = spot.formula_to_bdd(i, UCBWrapper.ucb.get_dict(), None)
		o_bdd = spot.formula_to_bdd(state.output_fun[i], 
				UCBWrapper.ucb.get_dict(), None)
		
		f_ = lowestUpperBound(UCBWrapper.get_transition_state(f1, 
			i_bdd & o_bdd), f2)
		if not UCBWrapper.is_safe(f_):
			return False
		if UCBWrapper.contains(f_, f2) and f_ != f2:
			transition_state.counting_function = f_;
			for j in transition_state.transitions.keys():
				edges_to_visit.append([transition_state, j])
	return True

def mergeAndPropogate(s1: MealyState, s2: MealyState, mealy_machine: MealyMachine):
	propogate_queue = [[s1, s2]]
	states = mealy_machine.states
	root = mealy_machine.initial_state
	while len(propogate_queue) > 0:
		s1, s2 = propogate_queue[0]
		if s1 not in states or s2 not in states:
			continue	
		propogate_queue = propogate_queue[1:]
		if s1 == s2:
			continue
		propogate_queue.extend(mergeOperation(s1, s2, mealy_machine))
		states.remove(s2)
		if s2 == root:
			root = s1
	return MealyMachine(root, states)


def mergeOperation(s1: MealyState, s2: MealyState, mealy_machine: MealyMachine):
	merge_next = []
	for state in mealy_machine.states:
		for i in state.transitions.keys():
			if state.transitions[i] == s2:
				state.transitions[i] = s1
			if i in s2.transitions.keys() and s2.transitions[i] == state:
				if i in s1.transitions.keys():
					merge_next.append([s1.transitions[i], state])
				else:
					s1.transitions[i] = state
					s1.output_fun[i] = s2.output_fun[i]
	return merge_next
