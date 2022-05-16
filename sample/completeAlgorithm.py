from aalpy.automata import MealyState, MealyMachine
from prefixTreeBuilder import *
from mealyMachineBuilder import checkCFSafety
import functools

def complete_mealy_machine(mealy_machine, UCBWrapper):
	counting_functions_in_use = []
	special_counting_functions_in_use = []
	
	for state in mealy_machine.states:
		if state.special_node:
			special_counting_functions_in_use.append(state.counting_function)
		else:
			counting_functions_in_use.append(state.counting_function)

	state_queue = [mealy_machine.initial_state]
	visited_states = [mealy_machine.initial_state]
	
	while len(state_queue) > 0:
		state = state_queue[0]
		print("Checking state " + state.state_id)
		state_queue = state_queue[1:]
		if state == None:
			continue
		for i_bdd in UCBWrapper.bdd_inputs:
			i_str = bdd_to_str(i_bdd)
			print("Checking for transition " + i_str)
			if i_str in state.transitions.keys():
				next_state = state.transitions[i_str]
				print(i_str + " is in transitions already.")
				print("{} , {} -> {}".format(state.state_id, i_str,
					next_state.state_id))
			else:
				next_counting_function, o_bdd = query(
					state.counting_function,
					i_bdd,
					UCBWrapper,
					state.state_id,
					counting_functions_in_use,
					special_counting_functions_in_use)

				print("Transition from {} with {}/{} gives CF:{}".format(
					state.state_id, i_str, bdd_to_str(o_bdd), 
					next_counting_function))

				state.output_fun[i_str] = bdd_to_str(o_bdd)
				next_state = get_state_from_counting_function(
						next_counting_function, mealy_machine.states, 
						UCBWrapper)

				if next_state is not None:
					state.transitions[i_str] = next_state
					initialize_counting_function(mealy_machine,
							UCBWrapper)
					if not checkCFSafety(mealy_machine, UCBWrapper):
						state.transitions[i_str] = None
						next_state = None
					else:
						print("Transition added to " + str(next_state.state_id))
				if next_state is None:
					transitionAdded = False
					for next_state in mealy_machine.states:
						state.transitions[i_str] = next_state
						initialize_counting_function(mealy_machine,
							UCBWrapper)
						if checkCFSafety(mealy_machine, UCBWrapper):
							transitionAdded = True
							print("Transition added to " + str(next_state.state_id))
							break
					if not transitionAdded:
						next_state = MealyState(state.state_id + \
							"({}.{})".format(i_str, bdd_to_str(o_bdd)))
						mealy_machine.states.append(next_state)
						next_state.counting_function = next_counting_function
						state.transitions[i_str] = next_state
						print("Creating new state " + next_state.state_id)
						print("Transition added to " + str(next_state.state_id))
					else:
						for s in mealy_machine.states:
							print("Counting function of {} is {}".format(
								s.state_id, s.counting_function))
					counting_functions_in_use = []
					for s in mealy_machine.states:
						counting_functions_in_use.append(s.counting_function)
				print("Creating new transition for: " + i_str)
				print("{} , {} -> {}".format(state.state_id, i_str,
					next_state.state_id))
			if next_state not in visited_states:
				if next_state is None:
					print("State is none")
				state_queue.append(next_state)
				visited_states.append(next_state)

def get_state_from_counting_function(counting_function, states, 
	machine):
	for state in states:
		if machine.contains(state.counting_function, counting_function):
			return state

def check_if_cf_in_list(current_state_vector, cf_list, machine):
	for cf in cf_list:
		if machine.contains(cf, current_state_vector):
			return True
	return False

def print_choice_list(choice_list, choice_name):
	print(choice_name + ', '.join(list(map(lambda x: bdd_to_str(x[1]) + ": " + str(x[0])
		, choice_list))))

def contains(vector_1, vector_2):
	for i in range(len(vector_1)):
		if vector_1[i] > vector_2[i]:
			return False
	return True

def sort_counting_functions(vector_1, vector_2):
	if contains(vector_1[0], vector_2[0]):
		return -1
	elif contains(vector_2[0], vector_1[0]):
		return 1
	elif max(vector_1[0]) < max(vector_2[0]):
		return -1
	elif max(vector_1[0]) > max(vector_2[0]):
		return 1
	elif (sum(vector_1[0])) < (sum(vector_2[0])):
		return -1
	elif (sum(vector_1[0])) > (sum(vector_2[0])):
		return 1
	else:
		return 0

def query(state_vector, i, machine, min_word, counting_functions_in_use, special_counting_functions_in_use):
		
	dst_state_vector = None
	output_choice = None
	
	unsafe_choice_list = []
	safe_choice_list = []
	best_choice_list = []
	preferred_visited_choice_list = []
	visited_choice_list = []
	
	for o in machine.bdd_outputs:
		current_state_vector = machine.get_transition_state(
			state_vector, i & o)
		if not machine.is_safe(current_state_vector):
			# print("Unsafe choice. Continuing...")
			unsafe_choice_list.append([current_state_vector, o])
			continue
		safe_choice_list.append([current_state_vector, o])
		
		if (len(special_counting_functions_in_use) > 0):
			if check_if_cf_in_list(current_state_vector, special_counting_functions_in_use, machine):
				preferred_visited_choice_list.append([current_state_vector, o])
		
		if (len(counting_functions_in_use) > 0):
			if check_if_cf_in_list(current_state_vector, counting_functions_in_use, machine):
				visited_choice_list.append([current_state_vector, o])


	preferred_visited_choice_list = sorted(preferred_visited_choice_list, key=functools.cmp_to_key(sort_counting_functions))
	visited_choice_list = sorted(visited_choice_list, key=functools.cmp_to_key(sort_counting_functions))
	safe_choice_list = sorted(safe_choice_list, key=functools.cmp_to_key(sort_counting_functions))
	
	if len(preferred_visited_choice_list) > 0:
		dst_state_vector, output_choice = preferred_visited_choice_list[0]
	elif len(visited_choice_list) > 0:
		dst_state_vector, output_choice = visited_choice_list[0]
	else:
		dst_state_vector, output_choice = safe_choice_list[0]
	print("".join(["-"]*100))
	print("Action after sequence " 
		+ min_word
		+ '.' + bdd_to_str(i)
		+ " is chosen as: " + bdd_to_str(output_choice))
	
	print_choice_list(safe_choice_list, "Safe actions: ")
	print_choice_list(preferred_visited_choice_list,
							"Actions that lead to a 'pre-machine' visited state: ")
	print_choice_list(visited_choice_list,
							"Actions that lead to a visited state: ")
	print_choice_list(unsafe_choice_list, "Unsafe actions: ")
	

	chooseToModify = "n"
		
	if chooseToModify in "yY":
		while True:
			output_choice = input("Enter preferred action: ")
			for o in machine.bdd_outputs:
				if output_choice == bdd_to_str(o):
					output_choice = o
					dst_state_vector = machine.get_transition_state(state_vector, i & o)
					return {"dst_state": dst_state_vector, "output": output_choice}
			print("Invalid action. Choose amongst: " \
				+ ", ".join(list(map(lambda x: bdd_to_str(x),
									machine.bdd_outputs))))
	return [dst_state_vector, output_choice]
