from app.synthlearn.algorithm import build_mealy
import json, random
from app.utils import save_mealy_machile
import configparser
from logging.config import fileConfig
import argparse

fileConfig('app/logging_conf.ini')
config = configparser.ConfigParser()
config.read('config.ini')
 
parser = argparse.ArgumentParser(description="SynthLearn:User-Guided LTL Synthesis",
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

inputs = args['inputs']
outputs = args['outputs']
formula = args['formula']
traces = args['traces']
file_name = args['destination']

while ((inputs is None) or (len(inputs) == 0)):
	inputs = input("No input propositions entered."
		" Enter comma-separated input propositions: ")
while ((outputs is None) or (len(outputs) == 0)):
	outputs = input("No output propositions entered."
		" Enter comma-separated output propositions: ")
while ((formula is None) or (len(formula) == 0)):
	formula = input("No LTL formula entered. Enter LTL formula: ")

inputs = list(map(str.strip, inputs.split(',')))
outputs = list(map(str.strip, outputs.split(',')))
if traces is not None:
	traces = list(map(str.strip, traces.split(',')))
	traces = list(map(lambda x: x.replace('\r', '').replace('#', '.').split('.'), traces))
else:
	traces = []

if file_name is None:
	file_name = 'LearnedModel'

m, stats = build_mealy(traces, formula, inputs, outputs,
	config['DEFAULT'], 6, 'prefix')
if m is None:
	print(stats)
	print(m)
else:
	save_mealy_machile(m, file_name, ['pdf'])
	print({ 
		'traces': stats['traces'],
		'realizable': stats['realizable'],
		'message': stats['message']
	})