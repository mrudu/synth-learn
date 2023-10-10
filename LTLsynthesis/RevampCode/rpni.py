from aalpy.automata import MealyState, MealyMachine
from LTLsynthesis.RevampCode.utils import checkCFSafety, sort_nodes
import copy

# Merge step of red and blue state
def merge(mealy_machine: MealyMachine, q_red: MealyState, q_blue: MealyState):
	for state in mealy_machine.states:  # O(n)
		for i in state.transitions.keys(): # O(|I|)
			if state.transitions[i] == q_blue:
				state.transitions[i] = q_red
	return fold(mealy_machine, q_red, q_blue)

# Folding red and blue states together (propogating merge)
def fold(mealy_machine: MealyMachine, q_red: MealyState, q_blue: MealyState): # O(n*(d^2))
	for i in q_blue.transitions.keys(): # O(|I|)
		if i in q_red.transitions.keys(): # O(|I|)
			# Note: Mealy Machine! Merge failed as input/output don't match! 
			if q_blue.output_fun[i] != q_red.output_fun[i]:
				return False
			mealy_machine = fold(mealy_machine, q_red.transitions[i], q_blue.transitions[i]) # O(*)
		else:
			q_red.transitions[i] = q_blue.transitions[i]
			q_red.output_fun[i] = q_blue.output_fun[i]
	return True

# rpni
'''Note, here, we store indices of states in red and blue sets to account for
deep copy of mealy machine in case of failed merges.'''
def rpni_mealy(mealy_machine: MealyMachine, ucb, antichain_vectors):
	red = [mealy_machine.initial_state.index] # O(1)
	blue = set([s.index for s in mealy_machine.initial_state.transitions.values()]) # O(n)
	while len(blue) > 0: # O(n^4)
		# Storing copy of old machine in case of failed merges
		old_mealy_machine = copy.deepcopy(mealy_machine) # O(n^2)?
		q_blue = min(blue) # O(n)
		blue.remove(q_blue) # O(1)
		canBeMerged = False # O(1)
		safety, cfs = checkCFSafety(mealy_machine, ucb, antichain_vectors) 
		red = sort_nodes(mealy_machine, red, cfs)
		# Finding a red state to merge blue state
		for q_red in red: # O(n^3)
			# Checking if red state is a prefix of blue state
			# Required for completeness
			if len(mealy_machine.states[q_red].state_id) > len(
				mealy_machine.states[q_blue].state_id):
				continue
			# Testing if merge with q_red state is sucessful
			if merge(mealy_machine, mealy_machine.states[q_red], 
				mealy_machine.states[q_blue]) and checkCFSafety(
				mealy_machine, ucb, antichain_vectors)[0]: # O(n)
				canBeMerged = True # O(1)
				# Merge successful. Add new red state neighbours to
				# blue (resulting from merge)
				for qr in red: # O(n^2)
					for q in mealy_machine.states[qr].transitions.values(): # O(d)
						if q.index not in red: # O(n)
							blue.add(q.index)
				break
			# Handling failed merges and restoring unmerged state
			else:
				mealy_machine = copy.deepcopy(old_mealy_machine)
		
		# If cant be merged with any red, make blue as red
		if not canBeMerged:
			if q_blue not in red:
				red.append(q_blue)
				blue.update([q.index for q in mealy_machine.states[q_blue
					].transitions.values()])
	prune_machine(mealy_machine)
	return mealy_machine

# Prune Unreachable Nodes
def prune_machine(mealy_machine: MealyMachine):
	state_queue = [mealy_machine.initial_state]
	state_visited_bool = [False]*len(mealy_machine.states)
	reachable_states = []
	while len(state_queue) > 0:
		state = state_queue.pop(0)
		if state_visited_bool[state.index]:
			continue
		state_visited_bool[state.index] = True
		state_queue.extend(state.transitions.values())
		reachable_states.append(state)

	# Reinintialising indices
	for i in range(len(reachable_states)):
		reachable_states[i].index = i
	mealy_machine.states = reachable_states

# Pretty Print Mealy Machine
def pretty_print(mealy_machine):
	state_queue = [mealy_machine.initial_state]
	j = 0
	while j < len(mealy_machine.states):
		state = mealy_machine.states[j]
		j += 1
		print(state.state_id)
		for i in state.transitions.keys():
			print("{} -({}/{})-> {}".format(state.state_id, i, 
				state.output_fun[i], state.transitions[i].state_id))

# Building the prefix tree automata
def build_PTA(examples):
	root = MealyState('e')
	root.index = 0
	list_states = [root]
	for example in examples:
		state = root
		# iterate through inputs of example
		for i in range(0, len(example), 2):
			# propogate example down PTA
			if example[i] in state.transitions.keys():
				if example[i+1] != state.output_fun[example[i]]:
					return None
				state = state.transitions[example[i]] 
			# reached leaf
			else:
				# create new state
				new_state = MealyState(state.state_id + \
					"#{}.{}".format(example[i],example[i+1]))
				new_state.index = len(list_states)
				# link state to new state
				state.transitions[example[i]] = new_state
				# assign output to input
				state.output_fun[example[i]] = example[i+1]
				# add new state to list of nodes
				list_states.append(new_state)
				state = new_state
	mealyTree = MealyMachine(root, list_states)
	return mealyTree
