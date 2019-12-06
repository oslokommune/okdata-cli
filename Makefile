.PHONY: init
init:
	python3 -m pip install tox black pip-tools
	pip-compile
	pip3 install -rrequirements.txt

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
	if test "$${status}" != "## master...origin/master"; then \
		echo; \
		echo Git working directory is dirty, aborting >&2; \
		false; \
	fi
