import spot
import buddy
import subprocess
import math
from LTLsynthesis.utilities import contains
import logging

logger = logging.getLogger('algo-logger')

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
		if not (self.compute_winning(psi, input_atomic_propositions, 
							 output_atomic_propositions)):
			return
		# universal co-buchi of formula
		self.num_states = self.ucb.num_states()
		
		# proposition list
		self.bdd_inputs = self.get_bdd_propositions(
			input_atomic_propositions)
		self.bdd_outputs = self.get_bdd_propositions(
			output_atomic_propositions)

	def compute_winning(self, psi, inputs, outputs):
		src_file = "/Users/mrudula/Personal/code/acacia-bonsai/build/src/acacia-bonsai"
		antichain_lines = []
		automata_lines = []
		state_reassignment = []
		init_state = 0
		try:
			command = "{} -f '{}' -i '{}' -o '{}' --K={}".format(
				src_file,
				psi, 
				",".join(inputs), 
				",".join(outputs), 
				self.k)

			command = "multipass exec foobar -- " + command
			logger.debug(command)
			op = subprocess.run(command, shell=True, capture_output=True)
			captureUCB = False
			captureStateReassignment = False
			captureAntichain = False
			
			for line in op.stdout.splitlines():
				l = line.decode()
				if l == "UNKNOWN" or l == "UNREALIZABLE":
					return False
				elif l == "AUTOMATA":
					captureUCB = True
				elif l =="REASSIGNINGSTATES":
					captureUCB = False
					captureStateReassignment = True
				elif l == "INITIALSTATE":
					captureStateReassignment = False
				elif l == "ANTICHAINHEADS":
					captureAntichain = True
				elif captureUCB:
					automata_lines.append(l)
				elif captureAntichain:
					antichain_lines.append(l)
				elif captureStateReassignment:
					state_reassignment.append(int(l))
				else:
					init_state = int(l)
			antichain_lines = antichain_lines[:-1]
			for a in spot.automata('\n'.join(automata_lines)):
				self.ucb = a
			self.ucb.set_init_state(state_reassignment.index(init_state))
		except Exception as e:
			print("Cannot execute command.")
			print(e)
			return False
		print("Maximal Elements of Antichain: ")
		for line in antichain_lines:
			list_item = list(map(lambda x: int(x), line.strip('{ }\n').split(" ")))
			antichain_vector = []
			for s in state_reassignment:
				antichain_vector.append(list_item[s])
			print(antichain_vector)
			self.antichain_heads.append(antichain_vector)
		return True

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
					if edge.dst == state and (edge.cond & edge_formula != buddy.bddfalse):
						dst_state_possibilities.append(min(self.k+1, 
						(state_vector[from_state] + 
							(1 if (self.ucb.state_is_accepting(state))
							else 0))
						))
			if len(dst_state_possibilities) == 0:
				dst_state_vector.append(-1)
				continue
			dst_state_vector.append(max(dst_state_possibilities))
		return dst_state_vector

	def is_safe(self, state_vector):
		safe = False
		for antichain_vector in self.antichain_heads:
			safe = safe or contains(state_vector, antichain_vector)
		return safe