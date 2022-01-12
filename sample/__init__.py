import spot
import buddy
import subprocess
import math
import random
from aalpy.automata import MealyState, MealyMachine
from aalpy.utils import visualize_automaton
from aalpy.SULs import MealySUL

class LearnMealyMachine(object):
	"""docstring for LearnMealyMachine"""

	def __init__(
			self, k, psi, input_atomic_propositions, 
			output_atomic_propositions, user_modifications=False):
		super(LearnMealyMachine, self).__init__()
		self.k = k
		self.compute_winning(psi, input_atomic_propositions, 
							 output_atomic_propositions)

		# universal co-buchi of formula
		self.ucb_num_states = self.ucb.num_states()
		
		# proposition list
		self.bdd_inputs = self.get_proposition_list(
			self.get_bdd_propositions(input_atomic_propositions))
		self.bdd_outputs = self.get_proposition_list(
			self.get_bdd_propositions(output_atomic_propositions))

		self.mealy_machine = spot.make_twa_graph(self.ucb.get_dict())
		self.mealy_machine_aalpy = None
		self.register_ap(self.mealy_machine, input_atomic_propositions)
		self.register_ap(self.mealy_machine, output_atomic_propositions)
		self.state_counting_function_map = {}
		self.visited_states = []

		self.queries = 0
		self.userQueries = 0
		self.user_modifications = user_modifications

	def compute_winning(self, psi, inputs, outputs):
		src_file = "~/Personal/code/acacia-bonsai/build/src/acacia-bonsai"
		antichain_lines = []
		automata_lines = []
		num_bool_states = 0
		try:
			command = "{} -f '{}' -i '{}' -o '{}' --K={}".format(
				src_file,
				psi, 
				",".join(inputs), 
				",".join(outputs), 
				self.k)

			command = "multipass exec foobar -- " + command

			op = subprocess.run(command, shell=True, capture_output=True)
			captureAut = False
			captureAntichain = False
			
			for line in op.stdout.splitlines():
				l = line.decode()
				if l == "AUTOMATA":
					captureAut = True
				elif l =="BOOLEANSTATES":
					captureAut = False
				elif l == 'ANTICHAINHEADS':
					captureAntichain = True
				elif captureAut:
					automata_lines.append(l)
				elif captureAntichain:
					antichain_lines.append(l)
				else:
					num_bool_states = int(l)
			antichain_lines = antichain_lines[:-1]
			for a in spot.automata('\n'.join(automata_lines)):
				self.ucb = a
		
		except:
			print("Cannot execute file.")
			self.ucb = self.build_UCB(psi)
			pass

		self.antichain_heads = []
		
		for line in antichain_lines:
			list_item = list(map(lambda x: int(x), line.strip('{ }\n').split(" ")))
			list_item = list_item[len(list_item) - num_bool_states:] \
				+ list_item[:len(list_item) - num_bool_states]
			self.antichain_heads.append(list_item)

		print("Maximal Elements of Antichain: " + str(self.antichain_heads))

	def build_UCB(self, psi):
		# Negating Formula
		psi = spot.formula.Not(psi)
		# Creating the automata
		automata = spot.translate(psi, 'Buchi', 'state-based', 'complete', 'small')
		
		return automata

	def register_ap(self, aut, atomic_propositions):
		for p in atomic_propositions:
			aut.register_ap(p)

	def get_bdd_propositions(self, atomic_propositions):
		# Creating BDD
		bdd_propositions = []

		for p in atomic_propositions:
			bdd_propositions.append(
				buddy.bdd_ithvar(self.ucb.register_ap(p)))

		return bdd_propositions

	def get_proposition_list(self, atomic_propositions):
		n = len(atomic_propositions)
		format_string = '{0:0' + str(n) +  'b}'
		bdd_list = []
		for num in range(int(math.pow(2, n))):
			arr_list = list(map(lambda x: int(x), format_string.format(num)))
			bdd = buddy.bddtrue
			for i in range(n):
				if arr_list[i] == 1:
					bdd &= atomic_propositions[i]
				else:
					bdd &= buddy.bdd_not(atomic_propositions[i])
			bdd_list.append(bdd)
		return bdd_list

	def get_state_label(self, val):
		for key, value in self.state_counting_function_map.items():
			 if val == value:
				 return key
	 
		return val
	
	def build_mealy(self):
		k = 1
		waiting = []
		waiting.append([-1]*self.ucb_num_states)
		waiting[0][self.ucb.get_init_state_number()] = 0

		num_states = 0
		node_label_dict = dict()
		node_label_dict[num_states] = MealyState("[]")
		initial_node = node_label_dict[0]

		self.state_counting_function_map[str(waiting[0])] = initial_node
		self.visited_states.append(waiting[0])
		
		while len(waiting) > 0:
			from_count_fn = random.choice(waiting)
			waiting.remove(from_count_fn)
			
			from_state = self.state_counting_function_map[str(from_count_fn)]
			
			for i in self.bdd_inputs:
				dst_count_fn, o = self.query(from_count_fn, i)
				input_formula = str(spot.bdd_to_formula(i))
				output_formula = str(spot.bdd_to_formula(o))
				
				if dst_count_fn in self.visited_states:
					to_state = self.state_counting_function_map[str(dst_count_fn)]
				else:
					self.visited_states.append(dst_count_fn)
					waiting.append(dst_count_fn)
					
					num_states += 1
					node_label_dict[num_states] = MealyState( 
						from_state.state_id \
						+ ".[{}][{}]".format(input_formula, output_formula))

					to_state = node_label_dict[num_states]
					self.state_counting_function_map[str(dst_count_fn)] = to_state
				
				from_state.transitions[input_formula] = to_state
				from_state.output_fun[input_formula] = output_formula
		
		self.mealy_machine_aalpy = MealyMachine(initial_node, list(node_label_dict.values()))
	
	def get_transition_state(self, state_vector, edge_formula):
		dst_state_vector = []
		for state in range(self.ucb_num_states):
			dst_state_possibilities = []
			for from_state in range(self.ucb_num_states):
				if state_vector[from_state] == -1:
					continue
				for edge in self.ucb.out(from_state):
					if edge.dst != state:
						continue
					if edge.cond & edge_formula != buddy.bddfalse:
						dst_state_possibilities.append(min(self.k+1, 
						(state_vector[from_state] + 
							1 if self.ucb.state_is_accepting(edge.dst)
							else 0)
						))
			if len(dst_state_possibilities) == 0:
				dst_state_vector.append(-1)
				continue
			dst_state_vector.append(max(dst_state_possibilities))
		return dst_state_vector

	def is_safe(self, state_vector):
		safe = False
		for antichain_vector in self.antichain_heads:
			safe = safe or self.contains(antichain_vector, state_vector)
		return safe

	def contains(self, vector_1, vector_2):
		if vector_1 == None or vector_2 == None:
			return False
		for i in range(self.ucb_num_states):
			if vector_1[i] < vector_2[i]:
				return False
		return True

	@staticmethod
	def print_choice_list(choice_list, choice_name):
		if len(choice_list) > 0:
			print(choice_name + 
				', '.join(list(map(lambda x: str(spot.bdd_to_formula(x[1])), choice_list))))

	def query(self, state_vector, i):
		self.queries += 1
		
		dst_state_vector = None
		output_choice = None
		
		unsafe_choice_list = []
		safe_choice_list = []
		best_choice_list = []
		visited_choice_list = []
		
		for o in self.bdd_outputs:
			current_state_vector = self.get_transition_state(state_vector, i & o)
			if not self.is_safe(current_state_vector):
				# print("Unsafe choice. Continuing...")
				unsafe_choice_list.append([current_state_vector, o])
				continue
			safe_choice_list.append([current_state_vector, o])
			
			if current_state_vector in self.visited_states:
				visited_choice_list.append([current_state_vector, o])
			
			if current_state_vector == dst_state_vector:
				best_choice_list.append([current_state_vector, o])
				continue
			
			if self.contains(current_state_vector, dst_state_vector):
				continue
			if (dst_state_vector == None \
			  or self.contains(dst_state_vector, current_state_vector) \
			  or current_state_vector in self.visited_states):
				dst_state_vector = current_state_vector
				output_choice = o
				best_choice_list = [[current_state_vector, o]]
				continue
			
			best_choice_list.append([current_state_vector, o])
			

		print("Action after sequence " 
			+ self.state_minimal_word_map[self.state_counting_function_map[str(state_vector)]]
			+ '.' + str(spot.bdd_to_formula(i))
			+ " is chosen as: " + str(spot.bdd_to_formula(output_choice)))
		
		self.print_choice_list(best_choice_list, "Best actions: ")
		self.print_choice_list(safe_choice_list, "Safe actions: ")
		self.print_choice_list(visited_choice_list,
								"Actions that lead to a visited state: ")
		self.print_choice_list(unsafe_choice_list, "Unsafe actions: ")
		
		if self.user_modifications:
			chooseToModify = input("Modify? (y/n): ")
			
			if chooseToModify in "yY":
				self.userQueries += 1
				while True:
					for o in self.bdd_outputs:
						output_choice = input("Enter preferred action: ")
						if output_choice == str(spot.bdd_to_formula(o)):
							output_choice = o
							dst_state_vector = self.get_transition_state(state_vector, i & o)
							return {"dst_state": dst_state_vector, "output": output_choice}
					print("Invalid action. Choose amongst: " + ", ".join(list(map(lambda x: str(spot.bdd_to_formula(x)), self.bdd_outputs))))
		return [dst_state_vector, output_choice]

def execute_main():
	formula = input("Enter LTL formula: ")

	input_atomic_propositions = input("Enter Input Atomic Prositions (space-separated): ")
	input_atomic_propositions = input_atomic_propositions.split(" ")

	output_atomic_propositions = input("Enter Output Atomic Prositions (space-separated): ")
	output_atomic_propositions = output_atomic_propositions.split(" ")

	m = LearnMealyMachine(2, str(formula), input_atomic_propositions, output_atomic_propositions)
	m.build_mealy()
	visualize_automaton(
		self.mealy_machine_aalpy,
		file_type="svg"
	)

def test():
	m = LearnMealyMachine(2, 'G(p->Fgp) & G(q->Fgq) & G(!(gp & gq))', ['p', 'q'], ['gp', 'gq'])
	m.build_mealy()
	m.custom_print()
execute_main()