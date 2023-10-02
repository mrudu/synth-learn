from aalpy.automata import MealyState, MealyMachine
from LTLsynthesis.RevampCode.utils import checkCFSafety
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
		print("________________OLDCOPY________________")
		pretty_print(old_mealy_machine)
		print("________________OLDCOPY________________")
		q_blue = blue.pop() # O(1)
		canBeMerged = False # O(1)

		# Finding a red state to merge blue state
		for q_red in red: # O(n^3)
			# Testing if merge with q_red state is sucessful
			print("testing merge {} and {}".format(q_red, q_blue))
			if merge(mealy_machine, mealy_machine.states[q_red], 
				mealy_machine.states[q_blue]) and checkCFSafety(
				mealy_machine, ucb, antichain_vectors)[0]: # O(n)
				canBeMerged = True # O(1)
				print("Merge successful. Add new {} state neighbours to blue (resulting from merge)".format(q_red))
				for qr in red: # O(n^2)
					for q in mealy_machine.states[qr].transitions.values(): # O(d)
						if q.index not in red: # O(n)
							blue.add(q.index)
				pretty_print(mealy_machine)
				print("________________OLDCOPY________________")
				pretty_print(old_mealy_machine)
				print("________________OLDCOPY________________")
				print("red: {}".format(red))
				print("blue: {}".format(blue))
				break
			# Handling failed merges and restoring unmerged state
			else:
				print("Failed merge: reverting")
				print("________________OLDCOPY________________")
				pretty_print(old_mealy_machine)
				print("________________OLDCOPY________________")
				print("________________NEWCOPY________________")
				pretty_print(mealy_machine)
				print("________________NEWCOPY________________")
				mealy_machine = copy.deepcopy(old_mealy_machine)
				print("________________RESETCOPY________________")
				pretty_print(mealy_machine)
				print("________________RESETCOPY________________")
				print("red: {}".format(red))
				print("blue: {}".format(blue))
		
		# If cant be merged with any red, make blue as red
		if not canBeMerged:
			if q_blue not in red:
				red.append(q_blue)
				blue.update([q.index for q in mealy_machine.states[q_blue
					].transitions.values() if q not in red])
			print("Merge of {} not possible. Making red".format(q_blue))
			pretty_print(mealy_machine)
			print("red: {}".format(red))
			print("blue: {}".format(blue))
	prune_machine(mealy_machine)
	print("rpni done")
	print(checkCFSafety(mealy_machine, ucb, antichain_vectors)[0])
	pretty_print(mealy_machine)
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
		state.index = len(reachable_states)
		reachable_states.append(state)
	mealy_machine.states = reachable_states

# Pretty Print Mealy Machine
def pretty_print(mealy_machine):
	state_queue = [mealy_machine.initial_state]
	j = 0
	while j < len(mealy_machine.states):
		state = mealy_machine.states[j]
		j += 1
		print("{}: {}".format(state.index, state.state_id))
		for i in state.transitions.keys():
			print("{} -({}/{})-> {}".format(state.index, i, 
				state.output_fun[i], state.transitions[i].index))


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
	pretty_print(mealyTree)
	return mealyTree
