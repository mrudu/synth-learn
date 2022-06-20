from LTLsynthesis.algorithm import build_mealy
from LTLsynthesis.LStarLearning import learning
import logging
import json

logger = logging.getLogger("algo-logger")
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)
file_name = input("Enter name of json_file:")

def parse_json(file_name, new_traces = [], k=1):
	with open('examples/' + file_name + ".json", "r") as read_file:
	    data = json.load(read_file)
	LTL_formula = "((" + ') & ('.join(data['assumptions']) + "))->((" + ') & ('.join(data['guarantees']) + "))"
	if len(new_traces) == 0:
		traces = data['traces']
		traces = list(map(lambda x: x.split('.'), traces))
	else:
		traces = copy.deepcopy(new_traces)
	m = build_mealy(LTL_formula, data['input_atomic_propositions'], data['output_atomic_propositions'], traces, file_name, data['target'], k)
	learning(m)

parse_json(file_name)