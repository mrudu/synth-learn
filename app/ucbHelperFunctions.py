import buddy
import math

def create_bdd_list(ucb, atomic_propositions):
	# Creating BDD
	bdd_propositions = []
	for p in atomic_propositions:
		bdd_propositions.append(
			buddy.bdd_ithvar(ucb.register_ap(p)))
	
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

def get_transition_counting_function(ucb, state_vector, edge_label):
	dst_state_vector = [-1]*ucb.num_states()
	for state in range(ucb.num_states()):
		if state_vector[state] == -1:
			continue
		for edge in ucb.out(state):
			if (edge.cond & edge_label != buddy.bddfalse):
				dst_state_vector[edge.dst] = max(
					dst_state_vector[edge.dst], 
					(state_vector[state] + 
						(1 if (ucb.state_is_accepting(edge.dst))
						else 0)))
	return dst_state_vector

def is_safe(antichain_vectors, state_vector):
	safe = False
	for ac_vc in antichain_vectors:
		safe = safe or contains(state_vector, ac_vc)
	return safe

def contains(v1, v2):
	if (v1 is None) or (v2 is None):
		return False
	for i in range(len(v1)):
		if v1[i] > v2[i]:
			return False
	return True
