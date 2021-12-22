import spot
import buddy
import subprocess
import math
import random

class LearnMealyMachine(object):
	"""docstring for LearnMealyMachine"""

	def __init__(self, k, psi, input_atomic_propositions, output_atomic_propositions):
		super(LearnMealyMachine, self).__init__()
		self.k = k

		self.compute_winning(psi, input_atomic_propositions, output_atomic_propositions)

		# universal co-buchi of formula
		self.ucb_num_states = self.ucb.num_states()
		
		# proposition list
		self.bdd_atomic_inputs = self.get_bdd_propositions(input_atomic_propositions)
		self.bdd_atomic_outputs = self.get_bdd_propositions(output_atomic_propositions)
		self.bdd_inputs = self.get_proposition_list(self.bdd_atomic_inputs)
		self.bdd_outputs = self.get_proposition_list(self.bdd_atomic_outputs)

		self.mealy_machine = spot.make_twa_graph(self.ucb.get_dict())
		self.register_ap(self.mealy_machine, input_atomic_propositions)
		self.register_ap(self.mealy_machine, output_atomic_propositions)
		self.state_counting_function_map = {}
		self.visited_states = []

	def compute_winning(self, psi, inputs, outputs):
		directory = "/Users/mrudula/Personal/code/acacia-bonsai/build/"
		file_name = "src/acacia-bonsai"
		antichain_lines = []
		automata_lines = []
		try:
			command = directory + file_name + " -f '" + psi + "' -i '" + ",".join(inputs)
			command = command + "' -o '" + ",".join(outputs) + "' --K=" + str(self.k)

			command = "multipass exec foobar -- " + command

			op = subprocess.run(command, shell=True, capture_output=True)
			captureAut = False

			for line in op.stdout.splitlines():
				l = line.decode()
				if l == "AUTOMATA":
					captureAut = True
				elif l == 'ANTICHAINHEADS':
					captureAut = False
				elif captureAut:
					automata_lines.append(l)
				else:
					antichain_lines.append(l)
			antichain_lines = antichain_lines[:-1]
			for a in spot.automata('\n'.join(automata_lines)):
				self.ucb = a
		
		except:
			antichain_lines.append('{ 1 0 0 1 }')
			antichain_lines.append('{ 0 1 0 1 }')
			print("Cannot execute file. Using default contents: '[" + ', '.join(antichain_lines) + "]'")
			self.ucb = self.build_UCB(psi)
			pass

		self.antichain_heads = []
		print("Maximal Elements of Antichain: " + ', '.join(antichain_lines));
		isCorrect = input("Modify? (y/n): ")
		
		if isCorrect in "yY":
			antichain_lines = []
			num_elements = int(input("Enter number of elements of antichain: "))
			for x in range(num_elements):
				antichain_lines.append(input("Enter maximal element as {x x x .. x}: ")[::-1])
		
		for line in antichain_lines:
			self.antichain_heads.append(list(map(lambda x: int(x), line.strip('{ }\n').split(" ")))[::-1])

	def build_UCB(self, psi):
		# Negating Formula
		psi = spot.formula.Not(psi)
		# Creating the automata
		automata = spot.translate(psi, 'Buchi', 'state-based', 'complete', 'small')
		print(automata.to_str('hoa'))
		
		return automata

	def register_ap(self, aut, atomic_propositions):
		for p in atomic_propositions:
			aut.register_ap(p)

	def get_bdd_propositions(self, atomic_propositions):
		# Creating BDD
		bdd_propositions = []

		for p in atomic_propositions:
			bdd_propositions.append(buddy.bdd_ithvar(self.ucb.register_ap(p)))

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

	def custom_print(self):
	    print("Number of states: ", self.mealy_machine.num_states())
	    print("Initial state: ", self.mealy_machine.get_init_state_number())
	    print("Atomic propositions:", end='')
	    for ap in self.mealy_machine.ap():
	        print(' ', ap, sep='', end='\n')

	    for s in range(0, self.mealy_machine.num_states()):
	        print("State {}:".format(self.get_state_label(s)))
	        for t in self.mealy_machine.out(s):
	            print("  edge({} -> {})".format(self.get_state_label(t.src), self.get_state_label(t.dst)))
	            print("    label =", spot.bdd_to_formula(t.cond))

	def build_mealy(self):
		k = 1
		waiting = []
		waiting.append([-1]*self.ucb_num_states)
		waiting[0][self.ucb.get_init_state_number()] = 0
		s = self.mealy_machine.new_state()
		self.mealy_machine.set_init_state(s)
		self.state_counting_function_map[str(waiting[0])] = s
		self.visited_states.append(waiting[0])
		while len(waiting) > 0:
			state = random.choice(waiting)
			waiting.remove(state)
			from_state = self.state_counting_function_map[str(state)]
			for i in self.bdd_inputs:
				transition_state_dict = self.query(state, i)
				if transition_state_dict["dst_state"] in self.visited_states:
					to_state = self.state_counting_function_map[str(transition_state_dict["dst_state"])]
				else:
					self.visited_states.append(transition_state_dict["dst_state"])
					waiting.append(transition_state_dict["dst_state"])
					to_state = self.mealy_machine.new_state()
					self.state_counting_function_map[str(transition_state_dict["dst_state"])] = to_state
				self.mealy_machine.new_edge(from_state, to_state, i & transition_state_dict["output"])
	
	def get_transition_state(self, state_vector, edge_formula):
		dst_state_vector = []
		# print("state vector: " + str(state_vector))
		# print("Checking with formula " +  str(spot.bdd_to_formula(edge_formula)))
		for state in range(self.ucb_num_states):
			dst_state_possibilities = []
			# dst_state_possibilities.append(state_vector[state])
			# print("For position: " + str(state))
			for from_state in range(self.ucb_num_states):
				# print("From state: " + str(from_state))
				if state_vector[from_state] == -1:
					# print("From state not active. Continuing...")
					continue
				for edge in self.ucb.out(from_state):
					# print("Edge from state " + str(from_state) + " to " 
					# 	+ str(edge.dst) + "with condition " + str(spot.bdd_to_formula(edge.cond)))
					if edge.dst != state:
						continue
					if edge.cond & edge_formula != buddy.bddfalse:
						dst_state_possibilities.append(min(self.k+1, 
						(state_vector[from_state] + 
							1 if self.ucb.state_is_accepting(edge.dst)
							else 0)
						))
						# print("Adding to DST vector: " + str(min(self.k+1, 
						# (state_vector[from_state] + 
						# 	1 if self.ucb.state_is_accepting(edge.dst)
						# 	else 0)
						# )))
				# print("DST possibilities " + str(dst_state_possibilities))
			# print("Choosing max " + str(max(dst_state_possibilities)))
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
		for i in range(self.ucb_num_states):
			if vector_1[i] < vector_2[i]:
				return False
		return True

	def query(self, state_vector, i):
		dst_state_vector = None
		print(spot.bdd_to_formula(i))
		output_choice = None
		for o in self.bdd_outputs:
		# 	print("Current value of dst: " + str(dst_state_vector))
		# 	print("Output formula: " + str(spot.bdd_to_formula(o)))
			current_state_vector = self.get_transition_state(state_vector, i & o)
			# print("Transition state: " + str(current_state_vector))
			if not self.is_safe(current_state_vector):
				# print("Unsafe choice. Continuing...")
				continue
			if dst_state_vector == None:
				dst_state_vector = current_state_vector
				output_choice = o
				continue
			if self.contains(current_state_vector, dst_state_vector):
				# print("Already the best")
				continue
			if self.contains(dst_state_vector, current_state_vector):
				# print("Strictly better")
				dst_state_vector = current_state_vector
				output_choice = o
				continue
			if current_state_vector in self.visited_states:
				# print("Visited once")
				dst_state_vector = current_state_vector
				output_choice = o
				continue
			
		# print(spot.bdd_to_formula(output_choice))
		print(output_choice)
		return {"dst_state": dst_state_vector, "output": output_choice}

def execute_main():
	formula = input("Enter LTL formula: ")

	input_atomic_propositions = input("Enter Input Atomic Prositions (space-separated): ")
	input_atomic_propositions = input_atomic_propositions.split(" ")

	output_atomic_propositions = input("Enter Output Atomic Prositions (space-separated): ")
	output_atomic_propositions = output_atomic_propositions.split(" ")

	m = LearnMealyMachine(1, formula, input_atomic_propositions, output_atomic_propositions)
	m.build_mealy()
	m.custom_print()

def test():
	m = LearnMealyMachine(1, 'G(p->Fgp) & G(q->Fgq) & G(!(gp & gq))', ['p', 'q'], ['gp', 'gq'])
	m.build_mealy()
	m.custom_print()
test()