PROJECT = yzcache

PYTHON_VERSION = 2.7
REQUIREMENTS = requirements.txt
REQUIREMENTS_TEST = requirements-test.txt
VIRTUAL_ENV := .venv$(PYTHON_VERSION)
PYTHON := $(VIRTUAL_ENV)/bin/python
PIP_CONF = pip.conf
PYPI = dev
PYTEST = $(VIRTUAL_ENV)/bin/py.test

test: venv
	$(VIRTUAL_ENV)/bin/pip install -r $(REQUIREMENTS_TEST)
	$(VIRTUAL_ENV)/bin/python -m unittest $(PROJECT).tests
	#$(PYTEST)

test_coverage: test
	$(info No no coverage yet)


venv_init:
	if [ ! -d $(VIRTUAL_ENV) ]; then \
		virtualenv -p python$(PYTHON_VERSION) --prompt="($(PROJECT)) " $(VIRTUAL_ENV); \
	fi

venv:  venv_init
	cp $(PIP_CONF) $(VIRTUAL_ENV)/
	$(VIRTUAL_ENV)/bin/pip install -r $(REQUIREMENTS)


clean_venv:
	rm -rf $(VIRTUAL_ENV)

clean_pyc:
	find . -name \*.pyc -delete

clean: clean_venv clean_pyc

package:
	$(PYTHON) setup.py sdist

pkg_upload:
	$(PYTHON) setup.py sdist upload -r $(PYPI)

pkg_register:
	$(PYTHON) setup.py sdist register -r $(PYPI)

