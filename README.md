# SynthLearn

This is a modern implementation of example-guided reactive synthesis.
The theory is described in:
[LTL Reactive Synthesis with a Few Hints](https://link.springer.com/chapter/10.1007/978-3-031-30820-8_20)
   
# Dependencies

This program depends on:
- [Acacia-Bonsai](https://github.com/gaperez64/acacia-bonsai): See github readme page for installation instructions
- [The Spot Library](https://spot.lrde.epita.fr/): Spot is to be installed as a conda package
- [AALPy Library](https://github.com/DES-Lab/AALpy/)
- [PyDot](https://pypi.org/project/pydot/)

The webserver version of the program depends on:
- [Flask](https://flask.palletsprojects.com/)

# How to use:
The algorithm takes as input from the user the LTL specification, the system and environment variables, and examples if there are any.

For an interactive experience, you may run:
```
$ python command-line-interface.py
```
Here, you will be prompted to enter the required information in an interactive fashion.

There is also an option to provide a [JSON](https://www.json.org/json-en.html) file containing the specification details, whose format is described further below in this document.
For this option, you may run:
```
$ python -src <specification-file.json> command-line-interface.py
```

## Description of Specification File

The specification file must be in JSON format containing the following parameters:
- **formula:** here, you must provide the LTL specification
- **inputs:** here, you must provide comma-separated atomic propositions of the environment
- **outputs:** here, you must provide comma-separated atomic propositions of the system
- **traces:** here, you must provide comma-separated example 
- **destination:** here, you must provide the name of the output file

REMARk: Formula separated into assumptions and guarantees. 
Describe the format of the traces
Describe the format of LTL (check Strix?)
PROVIDE an example
ADD K-CO-BUCHI PARAMETER!
