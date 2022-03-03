import spot
import buddy
import subprocess
import math

class UCB(object):
	"""docstring for UCB"""

	def __init__(
			self, k, psi, input_atomic_propositions, 
			output_atomic_propositions):
		super(UCB, self).__init__()
		self.k = k

		# Compute the antichain
		self.ucb = None
		self.antichain_heads = []
		self.compute_winning(psi, input_atomic_propositions, 
							 output_atomic_propositions)

		# universal co-buchi of formula
		self.num_states = self.ucb.num_states()
		
		# proposition list
		self.bdd_inputs = self.get_bdd_propositions(
			input_atomic_propositions)
		self.bdd_outputs = self.get_bdd_propositions(
			output_atomic_propositions)

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
			print("Cannot execute command.")
			return
		
		for line in antichain_lines:
			list_item = list(map(lambda x: int(x), line.strip('{ }\n').split(" ")))
			list_item = list_item[len(list_item) - num_bool_states:] \
				+ list_item[:len(list_item) - num_bool_states]
			self.antichain_heads.append(list_item)

		print("Maximal Elements of Antichain: " + str(self.antichain_heads))

	def get_bdd_propositions(self, atomic_propositions):
		# Creating BDD
		bdd_propositions = []
		for p in atomic_propositions:
			bdd_propositions.append(
				buddy.bdd_ithvar(self.ucb.register_ap(p)))
		
		n = len(bdd_propositions)
		format_string = '{0:0' + str(n) +  'b}'
		bdd_list = []
		for num in range(int(math.pow(2, n))):
			arr_list = list(map(lambda x: int(x), format_string.format(num)))
			bdd = buddy.bddtrue
			for i in range(n):
				if arr_list[i] == 1:
					bdd &= bdd_propositions[i]
				else:
					bdd &= buddy.bdd_not(bdd_propositions[i])
			bdd_list.append(bdd)

		return bdd_list
	
	def get_transition_state(self, state_vector, edge_formula):
		dst_state_vector = []
		for state in range(self.num_states):
			dst_state_possibilities = []
			for from_state in range(self.num_states):
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
		for i in range(self.num_states):
			if vector_1[i] < vector_2[i]:
				return False
		return True