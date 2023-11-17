.PHONY: init
init:
	pip3 install tox black pip-tools
	pip-compile
	pip3 install -e .

.PHONY: format
format:
	python3 -m black .

.PHONY: clean
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *egg-info/

.PHONY: build
build:
	python setup.py sdist

.PHONY: test
test:
	python3 -m tox -p auto

.PHONY: bump-version
bump-version: is-git-clean
	bump2version patch

.PHONY: is-git-clean
is-git-clean:
	@status=$$(git fetch origin && git status -s -b) ;\
	if test "$${status}" != "## main...origin/main"; then \
		echo; \
		echo Git working directory is dirty, aborting >&2; \
		false; \
	fi

.PHONY: publish
publish:
	username=$$(op read op://Dataspeilet/pypi-upload-token/username) &&\
	password=$$(op read op://Dataspeilet/pypi-upload-token/credential) &&\
	python -m twine upload -u $$username -p $$password dist/*
