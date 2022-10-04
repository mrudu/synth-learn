import spot
import buddy
import subprocess
import math
from LTLsynthesis.utilities import contains, check_to_continue
import logging

logger = logging.getLogger('algo-logger')

def build_strix(LTL_formula, I, O):
	src_file = "/Users/mrudula/Downloads/strix"
	command = "{} -f '{}' --ins=\"{}\" --outs=\"{}\" --minimize".format(
			src_file,
			LTL_formula, 
			",".join(I), 
			",".join(O)) 
	print(command)
	try:
		op = subprocess.run(command, shell=True, capture_output=True)
		automata_lines = []
		ucb = None
		
		for line in op.stdout.splitlines():
			l = line.decode()
			automata_lines.append(l)

		for a in spot.automata('\n'.join(automata_lines[1:])):
			ucb = a
		return a.show().data
	except Exception as e:
		print(e)

	return ""

def build_UCB(LTL_formula, I, O, k=2, limit=10):
	global UCBWrapper
	UCBWrapper = UCB(k, LTL_formula, I, O)
	if UCBWrapper.ucb is None:
		if (k+1 > limit):
			if check_to_continue():
				limit = limit*1.5
			else:
				return None
		return build_UCB(LTL_formula, I, O, k+1, limit)
	logger.info("LTL Specification is safe for k=" + str(k))
	return UCBWrapper, k

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
		command = "{} -f '{}' -i '{}' -o '{}' --K={}".format(
			src_file,
			psi, 
			",".join(inputs), 
			",".join(outputs), 
			self.k)
		command = "multipass exec foobar -- " + command
		logger.debug(command)
		try:
			op = subprocess.run(command, shell=True, capture_output=True)
			captureUCB = False
			captureStateReassignment = False
			captureAntichain = False
			captureInitialState = False
			
			for line in op.stdout.splitlines():
				l = line.decode()
				if l == "UNKNOWN" or l == "UNREALIZABLE":
					return False
				elif l == "REALIZABLE":
					break
				elif l == "AUTOMATA":
					captureUCB = True
				elif l =="REASSIGNINGSTATES":
					captureUCB = False
					captureStateReassignment = True
				elif l == "INITIALSTATE":
					captureStateReassignment = False
					captureInitialState = True
				elif l == "ANTICHAINHEADS":
					captureInitialState = False
					captureAntichain = True
				elif captureUCB:
					automata_lines.append(l)
				elif captureAntichain:
					antichain_lines.append(l)
				elif captureStateReassignment:
					state_reassignment.append(int(l))
				elif captureInitialState:
					init_state = int(l)
			antichain_lines = antichain_lines[:-1]
			for a in spot.automata('\n'.join(automata_lines)):
				self.ucb = a
			self.ucb.set_init_state(state_reassignment.index(init_state))
		except Exception as e:
			print(command)
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
		if len(antichain_lines) == 0:
			self.antichain_heads.append([0]*self.ucb.num_states())
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
	
	def get_transition_state(self, state_vector, edge_label):
		dst_state_vector = [-1]*self.num_states
		for state in range(self.num_states):
			if state_vector[state] == -1:
				continue
			for edge in self.ucb.out(state):
				if (edge.cond & edge_label != buddy.bddfalse):
					dst_state_vector[edge.dst] = max(
						dst_state_vector[edge.dst], 
						(state_vector[state] + 
							(1 if (self.ucb.state_is_accepting(edge.dst))
							else 0)))
		return dst_state_vector

	def is_safe(self, state_vector):
		safe = False
		for antichain_vector in self.antichain_heads:
			safe = safe or contains(state_vector, antichain_vector)
		return safe