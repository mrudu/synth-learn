# SynthLearn: User-Guided Reactive Synthesis

This tool is an implementation of example-guided LTL reactive synthesis for which the theory is described in the following TACAS'23 paper:
[LTL Reactive Synthesis with a Few Hints](https://link.springer.com/chapter/10.1007/978-3-031-30820-8_20)

The tool can also be accessed through a user-friendly web interface provided [here](http://ec2-54-159-1-97.compute-1.amazonaws.com).

## TACAS'24 Paper abstract:
In this work, we introduce the SynthLearn tool. It implements an algorithm for reactive synthesis using LTL specifications, supplemented with examples of desired execution prefixes. Using automata learning techniques and zero-sum two player games, the synthesis procedure produces a Mealy machine that realizes the LTL specification and matches the given examples, whenever possible. By providing desired execution prefixes, users can guide the synthesis towards interesting solutions without having to specify low-level properties in LTL. We demonstrate the tool’s ability to produce effective solutions with a series of examples.

## Dependencies

The tool SynthLearn depends on:
- [Acacia-Bonsai](https://github.com/gaperez64/acacia-bonsai): See github readme page for installation instructions
- [The Spot Library](https://spot.lrde.epita.fr/): Spot is to be installed as a conda package
- [AALPy Library](https://github.com/DES-Lab/AALpy/)
- [PyDot](https://pypi.org/project/pydot/)

<!-- The webserver version of the program depends on:
- [Flask](https://flask.palletsprojects.com/)-->



## Description of the setup and shell scripts:
The setup is split into three shell scripts:
- ```acacia-bonsai-setup.sh```: This is the first shell script that must be run and it must be run with *superuser* privilegdes. Our tool is dependent on [Acacia-Bonsai](https://github.com/gaperez64/acacia-bonsai). This shell script sets up Acacia-Bonsai (including its dependencies).
- ```conda-setup.sh```: This is the second shell script that must be run. Our tool runs in a anaconda environment, which is setup through this script. At this point, there have modifications that have been made to ".bashrc"
- ```tool-setup.sh```: This script activates the conda environment and runs the *basic tests* suite to ensure good function of the tool.
You may see the details in the corresponding log files.

## Instructions for setup:
To install this tool, you may open the terminal and follow the instructions in order:
1. The first step is to navigate to current directory and run ```sudo ./acacia-bonsai-setup.sh```
2. The second step is to run ```./conda-setup.sh```. Once this script is done executing, it is recommended to exit and reopen the terminal.
3. The third and final step is to run ```./tool-setup.sh```

## How to use:
The algorithm takes as input from the user the LTL specification, the system and environment variables, and examples if there are any.

For an interactive experience, you may run:
```
$ python synthlearn.py
```
Here, you will be prompted to enter the required information in an interactive fashion.

There is also an option to provide a [JSON](https://www.json.org/json-en.html) file containing the specification details, whose format is described further below in this document.
For this option, you may run:
```
$ python -src <specification-file.json> synthlearn.py
```
If the specification is realizable, the tool generates a Mealy machine that realizes it, available in a PDF file.

## Formats

### Specification File

The specification file must be in JSON format containing the following parameters, for which the formats are described later in this text:
- **formula:** here, you must provide the LTL specification[^1] (see the syntax [below]). For example[^2]:
`G (r0 -> F g0) & G (r1 -> F g1) & G (!g0 | !g1)`
- **inputs:** here, you must provide comma-separated atomic propositions of the environment. For example: `r0,r1`
- **outputs:** here, you must provide comma-separated atomic propositions of the system. For example: `g0,g1`
- **traces:** here, you must provide comma-separated examples of executions, also called traces (see the syntax [below](#Format-of-Traces)). For example:
`p.gp & !gq, p & q.gp & !gq#true.!gp & gq` [^4]
- **destination:** here, you must provide the name of the output file which contains the generated Mealy Machine in a PDF format.
- **k-value:** also known as the co-Büchi parameter, is a numeric value, intuitively talks about the flexibility of the algorithm to synthesize a machine _(the higher the value, the more the flexibility, the smaller the machines)_

Example file 
```
    {
        "formula": "G (r0 -> F g0) & G (r1 -> F g1) & G (!g0 | !g1)",
        "inputs": "r0,r1",
        "outputs": "g0,g1",
        "traces": "p.gp & !gq, p & q.gp & !gq#true.!gp & gq",
        "destination": "MutexModel"
    }
```
### <a name="LTL" /> Linear Temporal Logic (LTL)

The grammar for LTL aims to support *Spot-style* LTL.
For further details on temporal logic, e.g., semantics, see [here](https://spot.lrde.epita.fr/tl.pdf).

The following constructs are supported:

#### Propositional Operators

  * True: `tt`, `true`, `1`
  * False: `ff`, `false`, `0`
  * Atom: `[a-zA-Z_][a-zA-Z_0-9]*` or quoted `"[^"]+"`
  * Negation: `!`, `NOT`
  * Implication: `->`, `=>`, `IMP`
  * Bi-implication: `<->`, `<=>`, `BIIMP`
  * Exclusive Disjunction: `^`, `XOR`
  * Conjunction: `&&`, `&`, `AND`
  * Disjunction: `||`, `|`, `OR`
  * Parenthesis: `(`, `)`

####  Temporal Operators

  * Finally: `F`
  * Globally: `G`
  * Next: `X`
  * (Strong) Until: `U`
  * Weak Until: `W`
  * (Weak) Release: `R`
  * Strong Release: `M`

#### Precedence Rules

The parser uses the following precedence:

`OR` < `AND` < Binary Expressions < Unary Expressions < Literals, Constants, Parentheses

For chained binary expressions (without parentheses), the rightmost binary operator takes precedence.
For example, `a -> b U c` is parsed as `a -> (b U c)`.

### Format of Traces

Traces have the following format: 

$i_0.o_0\#i_1.o_1\#i_2.o_2\#...i_k.o_k$ 

where each $i_j$ and  $o_j$ are conjunctions (use `&`) of literals over input and output atomic propositions respectively.
While the conjunctions $i_j$ are not necessarily _complete_ (some input atomic propositions do not necessarily appear in $i_j$), the conjunctions $o_j$ must always be complete, so that traces have a deterministic output-behaviour. Traces with non-complete inputs are called _symbolic_, and are expanded into a set of input-complete traces automatically by the tool. 

[^1]: _The web-interface splits specification as assumptions and guarantees which is then processed as _`assumptions => guarantees`_, and in contrast, here, you are expected to provide the LTL specification directly_
[^2]: The running example provided throughout this text is the one of the Mutual Exclusion arbiter (check Introduction of the tool paper)
[^3]: The first example specifies priority of process `p` over process `q`; the second example is to ensure no unsolicited grants.