from app.synthlearn.algorithm import build_mealy
import json, random
from app.utils import save_mealy_machile
import argparse

config = {
	"STRIX_TOOL": "/Users/mrudu/Downloads/strix",
	"ACACIA_BONSAI_TOOL": "acacia-bonsai",
	"STRIX_COMMAND": '{} -f "{}" --ins="{}" --outs="{}" -m both',
	"ACACIA_BONSAI_COMMAND": "{} -f '{}' -i '{}' -o '{}' --K={}",
}
 
parser = argparse.ArgumentParser(description="Just an example",
	formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-i", "--inputs", help="Enter comma-separated \
	input propositions. For example: p,q")
parser.add_argument("-o", "--outputs", help="Enter comma-separated \
	output propositions. For example: gp,gq")
parser.add_argument("-f", "--formula", help="Enter LTL formula. For \
	example: G (p -> F gp) & G (q -> F gq) & G (!gp | !gq)")
parser.add_argument("-t", "--traces", help="Enter comma-separated \
	traces. For example: p & q.gp & !gq, !p & !q.!gp & !gq",
	action='store_const', const=" ")
parser.add_argument("-dest", "--destination", help="Target PDF file name")
parser.add_argument("-src", "--source", help="Source JSON file name")
args = vars(parser.parse_args())

if args['source'] is not None:
	with open(args['source'], 'r') as src_file:
		args = json.load(src_file)

try:
	inputs = args['inputs']
except:
	inputs = ""

try:
	outputs = args['outputs']
except:
	outputs = ""

try:
	formula = args['formula']
except:
	formula = ""

try:
	traces = args['traces']
	if len(traces) > 0:
		traces = list(map(str.strip, traces.split(',')))
		traces = list(map(lambda x: x.replace('\r',
			'').replace('#', '.').split('.'), traces))
except:
	traces = []
try:
	k = args['k']
except:
	k = 6
try:
	file_name = args['destination']
except:
	file_name = 'LearnedModel'


while ((inputs is None) or (len(inputs) == 0)):
	inputs = input("No input propositions entered."
		"Enter comma-separated input propositions: ")

while ((outputs is None) or (len(outputs) == 0)):
	outputs = input("No output propositions entered."
		"Enter comma-separated output propositions: ")

while ((formula is None) or (len(formula) == 0)):
	formula = input("No LTL formula entered. Enter LTL formula: ")

inputs = list(map(str.strip, inputs.split(',')))
outputs = list(map(str.strip, outputs.split(',')))

m, stats = build_mealy(traces, formula, inputs, outputs,
	config, k, 'prefix')
if m is None:
	print("Unable to generate model.")
	print(stats['message'])
else:
	print("REALIZABLE! Model generated.")
	save_mealy_machile(m, file_name, ['pdf'])
	print("Traces used are:")
	print('\n'.join(map(lambda t: '#'.join([t[i] + '.' + t[i + 1] 
       for i in range(0, len(t), 2)]), stats['traces'])))