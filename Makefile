PROJECT = yzcache
VIRTUAL_ENV = .venv_master
REQUIREMENTS = requirements.txt
PATH := "$(VIRTUAL_ENV)/bin:$(PATH)"

venv:
	if [ ! -d "$(VIRTUAL_ENV)" ]; then \
		virtualenv --prompt='($(PROJECT)) ' $(VIRTUAL_ENV); \
	fi
	"$(VIRTUAL_ENV)/bin/pip" install -r "$(REQUIREMENTS)"

test:
	$(VIRTUAL_ENV)/bin/python -m unittest $(PROJECT).tests
