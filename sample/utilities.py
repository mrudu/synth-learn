import spot

def bdd_to_str(bdd_arg):
	return str(spot.bdd_to_formula(bdd_arg))

def str_to_bdd(bdd_str, ucb):
	return spot.formula_to_bdd(bdd_str, ucb.get_dict(), None)

def contains(vector_1, vector_2):
	if vector_1 == None or vector_2 == None:
		return False
	for i in range(len(vector_1)):
		if vector_1[i] > vector_2[i]:
			return False
	return True

def sort_counting_functions(cf_1, cf_2):
	if contains(cf_1, cf_2):
		return -1
	elif contains(cf_2, cf_1):
		return 1
	elif max(cf_1) < max(cf_2):
		return -1
	elif max(cf_1) > max(cf_2):
		return 1
	elif (sum(cf_1)) < (sum(cf_2)):
		return -1
	elif (sum(cf_1)) > (sum(cf_2)):
		return 1
	else:
		return 0

def lowestUpperBound(vector_1, vector_2):
	vector = []
	for i in range(len(vector_1)):
		if vector_1[i] > vector_2[i]:
			vector.append(vector_1[i])
		else:
			vector.append(vector_2[i])
	return vector

def is_excluded(pair, exclude_pairs):
	pair1 = '{}.{}'.format(pair[0].state_id, pair[1].state_id)
	pair2 = '{}.{}'.format(pair[1].state_id, pair[0].state_id)
	exclude_pairs = list(map(lambda x: '{}.{}'.format(x[0].state_id, x[1].state_id), exclude_pairs))
	return pair1 in exclude_pairs or pair2 in exclude_pairs