SHELL=/bin/bash

.DEFAULT_GOAL := _help

# NOTE: must put a <TAB> character and two pound "\t##" to show up in this list.  Keep it brief! IGNORE_ME
.PHONY: _help
_help:
	@grep -h "##" $(MAKEFILE_LIST) | grep -v IGNORE_ME | sed -e 's/##//' | column -t -s $$'\t'

.PHONY: init
init:	## Set up a Python virtual environment
	git submodule update --init
	@if [ ! -d .venv ]; then \
		python3 -m venv .venv; \
	fi
	@echo -e "\r\nNOTE: activate venv, and run 'make deps'\r\n"
	@echo -e "HINT: run 'source .venv/bin/activate'"

PYTHON ?= $(shell which python)
PWD ?= $(shell pwd)
.PHONY: _venv
_venv:
	# Test to enforce venv usage across important make targets
	[ "$(PYTHON)" = "$(PWD)/.venv/bin/python" ] || [ "$(PYTHON)" = "$(PWD)/.venv/Scripts/python" ]

PIP := python -m pip
REQS := requirements.txt
REQS_DEV := requirements-dev.txt
.PHONY: _deps
_deps:
	- $(PIP) install wheel
	$(PIP) install -r $(REQS)
	$(PIP) install -r $(REQS_DEV)

.PHONY: deps
deps: _venv _deps	## Install requirements

LINT_LOCS := ntserv/ server.py
YAML_LOCS := .*.yml
# NOTE: yamllint 	ntclient/ntsqlite/.travis.yml ? (submodule)
# NOTE: doc8 		ntclient/ntsqlite/README.rst  ? (submodule)
.PHONY: _lint
_lint:
	# check formatting: Python
	pycodestyle --max-line-length=88 --statistics $(LINT_LOCS)
	autopep8 --recursive --diff --max-line-length 88 --exit-code $(LINT_LOCS)
	isort --diff --check $(LINT_LOCS)
	black --check $(LINT_LOCS)
	# lint RST (last param is search term, NOT ignore)
	doc8 --ignore-path *venv .mypy* *.rst
	# lint YAML
	yamllint $(YAML_LOCS)
	# lint Python
	bandit -q -c .banditrc -r $(LINT_LOCS)
	mypy $(LINT_LOCS)
	# failing lints, ignore errors for now
	flake8 --statistics --doctests $(LINT_LOCS)
	pylint $(LINT_LOCS)

.PHONY: lint
lint: _venv _lint	## Lint code and documentation

.PHONY: format
format:
	isort $(LINT_LOCS)
	autopep8 --recursive --in-place --max-line-length 88 $(LINT_LOCS)
	black $(LINT_LOCS)


# ---------------------------------------
# Test
# ---------------------------------------

APP_HOME := ntserv/
TEST_HOME := test_ntserv.py
MIN_COV := 80
.PHONY: _test
_test:
	- coverage run --source=$(APP_HOME) -m pytest -v -s -p no:cacheprovider -o log_cli=true $(TEST_HOME)
	- coverage report --fail-under=$(MIN_COV) --show-missing --skip-empty --skip-covered

.PHONY: test
test: _venv _test   ## Run CLI unittests


.PHONY: clean
clean:	## Clean up __pycache__ and leftover bits
	rm -f .coverage
	rm -rf .mypy_cache/ .pytest_cache/
	find ntserv/ -name __pycache__ .pytest_cache | xargs rm -rf
