init:
	conda install -c conda-forge spot
	pip install -r requirements.txt

test:
	nosetests tests
