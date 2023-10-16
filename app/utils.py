from aalpy.utils.FileHandler import save_automaton_to_file
def process_data(data, strix=False):
	# parsing inputs and outputs
	inputs = data['inputs']
	inputs = list(map(str.strip, inputs.split(',')))
	outputs = data['outputs']
	outputs = list(map(str.strip, outputs.split(',')))
	formula = data['formula']
	
	if not strix:
		# parsing traces
		traces = data['traces']
		if len(traces) > 0:
			traces = traces.split('\n')
			traces = list(map(lambda x: x.replace('\r', '').split('.'), traces))
		else:
			traces = []

		# k
		k = int(data['k'])
		strategy = data['radioStrategy']
		return inputs, outputs, formula, traces, k, strategy
	return inputs, outputs, formula

def save_mealy_machile(mealy_machine, file_name, file_type = ['dot']):
	for type in file_type:
		save_automaton_to_file(mealy_machine, file_type=type,
			path=file_name)