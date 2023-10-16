from aalpy.automata import MealyState, MealyMachine
from app.synthlearn.utils import checkCFSafety, sort_nodes, reinitialize_index, pretty_print, get_prefix_states
import copy, logging

logger = logging.getLogger("mergePhaseLogger")

# Merge step of red and blue state
def merge(mealy_machine: MealyMachine, red: MealyState, blue: MealyState):
	logger.debug("Merge {}:{} and {}:{}".format(red.index, 
		red.state_id, blue.index, blue.state_id))
	for state in mealy_machine.states:  # O(n)
		for i in state.transitions.keys(): # O(|I|)
			if state.transitions[i] == blue:
				state.transitions[i] = red
				logger.debug("Adding transition: {} -{}/{}-> {}".format(
					state.index, i, state.output_fun[i], red.index))
	return fold(mealy_machine, red, blue)

# Folding red and blue states together (propogating merge)
def fold(mealy_machine: MealyMachine, red: MealyState, blue: MealyState): # O(n*(d^2))
	logger.debug("Fold {} and {}".format(red.index, blue.index))
	for i in blue.transitions.keys(): # O(|I|)
		if i in red.transitions.keys(): # O(|I|)
			# Note: Mealy Machine! Merge failed as input/output don't match! 
			if blue.output_fun[i] != red.output_fun[i]:
				logger.debug("Output dont match: {} -{}/{}-> , {}-{}/{}->".format(
					red.index, i, red.output_fun[i], 
					blue.index, i, blue.output_fun[i]))
				return False
			if not fold(mealy_machine, red.transitions[i], 
				blue.transitions[i]): # O(*)
				return False
		else:
			logger.debug("Adding transition: {} -{}/{}-> {}".format(
				red.index, i, blue.output_fun[i],
				blue.transitions[i].index))
			red.transitions[i] = blue.transitions[i]
			red.output_fun[i] = blue.output_fun[i]
	return True

def generalize(mealy_machine: MealyMachine, ucb, antichain_vectors, merging_strategy):
	prefix_state = get_prefix_states(mealy_machine)
	prefixes = list(prefix_state.keys())
	logger.debug("Presorted prefixes: {}".format(prefixes))
	prefixes.sort()
	logger.debug("Postsorted prefixes: {}".format(prefixes))

	for i in range(1, len(prefixes)):
		e = prefixes[i]
		e_state = prefix_state[e]
		logger.debug("Merging prefix: {} ({})".format(e, e_state))
		merge_candidates = list(set([prefix_state[p] for p in prefixes[:i]]))
		logger.debug("Presorted candidates: {}".format(merge_candidates))
		safety, count_funcs = checkCFSafety(mealy_machine, ucb, antichain_vectors)
		merge_candidates = sort_nodes(mealy_machine, merge_candidates, 
			count_funcs, merging_strategy)
		logger.debug("Post-sorted candidates: {}".format(merge_candidates))

		old_mealy_machine = copy.deepcopy(mealy_machine)
		pretty_print(mealy_machine)
		for cand in merge_candidates:
			logger.debug("Attempt merge: {} and {}".format(e_state, cand))
			mergeStatus = merge(mealy_machine, mealy_machine.states[cand], 
				mealy_machine.states[e_state])
			safetyStatus = checkCFSafety(mealy_machine, ucb, 
				antichain_vectors)[0]

			if (mergeStatus and safetyStatus):
				logger.debug("Successful merge")
				prefix_state[e] = cand
				break
			else:
				mealy_machine = copy.deepcopy(old_mealy_machine)

	reinitialize_index(mealy_machine)
	logger.debug("Phase 1 done.")
	pretty_print(mealy_machine)
	return mealy_machine

# Building the prefix tree automata
def build_PTA(examples):
	logger.debug(examples)
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
	reinitialize_index(mealyTree)
	return mealyTree
