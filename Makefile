venv:
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

test: venv
	. venv/bin/activate && python3 unit_tests.py
.PHONY: test

client: venv
	. venv/bin/activate && python3 client.py
.PHONY: client			

server: venv
	. venv/bin/activate && python3 server.py
.PHONY: server

clean:
	-rm -r venv
.PHONY: clean

lab0-ag:
	ag0/ag0.py
.PHONY: lab0-ag
