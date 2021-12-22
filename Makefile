init:
	conda install -r requirements.txt

test:
	nosetests tests
