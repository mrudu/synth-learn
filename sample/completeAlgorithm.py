from aalpy.automata import MealyState, MealyMachine
from prefixTreeBuilder import *

def complete_mealy_machine(mealy_machine, UCBWrapper):
	counting_functions_in_use = []
	
	for state in mealy_machine.states:
		counting_functions_in_use.append(state.counting_function)

	state_queue = [mealy_machine.initial_state]
	visited_states = [mealy_machine.initial_state]
	
	while len(state_queue) > 0:
		state = state_queue[0]
		if state == None:
			pass
		state_queue = state_queue[1:]	
		for i_bdd in UCBWrapper.bdd_inputs:
			i_str = bdd_to_str(i_bdd)
			if i_str in state.transitions.keys():
				next_state = state.transitions[i_str]
			else:
				next_counting_function, o_bdd = query(
					state.counting_function,
					i_bdd,
					UCBWrapper,
					state.state_id,
					counting_functions_in_use)
				if next_counting_function in counting_functions_in_use:
					next_state = get_state_from_counting_function(
						next_counting_function, mealy_machine.states)
				else:
					next_state = MealyState(state.state_id + \
						"({}.{})".format(i_str, bdd_to_str(o_bdd)))
					next_state.counting_function = next_counting_function
					counting_functions_in_use.append(next_counting_function)
					mealy_machine.states.append(next_state)
				state.transitions[i_str] = next_state
				state.output_fun[i_str] = bdd_to_str(o_bdd)
			if next_state not in visited_states:
				state_queue.append(next_state)
				visited_states.append(next_state)

def get_state_from_counting_function(counting_function, states):
	for state in states:
		if state.counting_function == counting_function:
			return state

def print_choice_list(choice_list, choice_name):
		if len(choice_list) > 0:
			print(choice_name + 
				', '.join(list(map(lambda x: bdd_to_str(x[1]), choice_list))))

def query(state_vector, i, machine, min_word, counting_functions_in_use):
		
	dst_state_vector = None
	output_choice = None
	
	unsafe_choice_list = []
	safe_choice_list = []
	best_choice_list = []
	visited_choice_list = []
	
	for o in machine.bdd_outputs:
		current_state_vector = machine.get_transition_state(
			state_vector, i & o)
		if not machine.is_safe(current_state_vector):
			# print("Unsafe choice. Continuing...")
			unsafe_choice_list.append([current_state_vector, o])
			continue
		safe_choice_list.append([current_state_vector, o])
		
		if str(current_state_vector) in counting_functions_in_use:
			visited_choice_list.append([current_state_vector, o])
		
		if current_state_vector == dst_state_vector:
			best_choice_list.append([current_state_vector, o])
			continue
		
		if machine.contains(current_state_vector, dst_state_vector):
			continue
		if (dst_state_vector == None \
		  or machine.contains(dst_state_vector, current_state_vector) \
		  or str(current_state_vector) in counting_functions_in_use):
			dst_state_vector = current_state_vector
			output_choice = o
			best_choice_list = [[current_state_vector, o]]
			continue
		
		best_choice_list.append([current_state_vector, o])
	
	print("".join(["-"]*100))
	print("Action after sequence " 
		+ min_word
		+ '.' + bdd_to_str(i)
		+ " is chosen as: " + bdd_to_str(output_choice))
	
	print_choice_list(best_choice_list, "Best actions: ")
	print_choice_list(safe_choice_list, "Safe actions: ")
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
