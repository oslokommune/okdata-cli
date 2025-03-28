GLOBAL_PY := python3
BUILD_VENV ?= .build_venv
BUILD_PY := $(BUILD_VENV)/bin/python

.PHONY: init
init: $(BUILD_VENV)

$(BUILD_VENV):
	$(GLOBAL_PY) -m venv $(BUILD_VENV)
	$(BUILD_PY) -m pip install -U pip

###
# Development
##

.PHONY: format
format: $(BUILD_VENV)/bin/black
	$(BUILD_PY) -m black .

.PHONY: test
test: $(BUILD_VENV)/bin/tox
	$(BUILD_PY) -m tox -p auto -o

.PHONY: upgrade-deps
upgrade-deps: $(BUILD_VENV)/bin/pip-compile
	$(BUILD_VENV)/bin/pip-compile -U

###
# Releases
##

.PHONY: bump-version-patch
bump-version-patch: $(BUILD_VENV)/bin/bump2version is-git-clean
	$(BUILD_VENV)/bin/bump2version patch

.PHONY: bump-version-minor
bump-version-minor: $(BUILD_VENV)/bin/bump2version is-git-clean
	$(BUILD_VENV)/bin/bump2version minor

.PHONY: bump-version-major
bump-version-major: $(BUILD_VENV)/bin/bump2version is-git-clean
	$(BUILD_VENV)/bin/bump2version major

.PHONY: build
build: $(BUILD_VENV)/bin/setuptools $(BUILD_VENV)/bin/twine $(BUILD_VENV)/bin/wheel is-git-clean format test
	$(BUILD_PY) setup.py sdist bdist_wheel

.PHONY: publish
publish: $(BUILD_VENV)/bin/twine
	username=$$(op read op://Dataspeilet/pypi-upload-token/username) &&\
	password=$$(op read op://Dataspeilet/pypi-upload-token/credential) &&\
	$(BUILD_PY) -m twine upload -u $$username -p $$password dist/*

.PHONY: is-git-clean
is-git-clean:
	@status=$$(git fetch origin && git status -s -b) ;\
	if test "$${status}" != "## main...origin/main"; then \
		echo; \
		echo Git working directory is dirty, aborting >&2; \
		false; \
	fi

.PHONY: clean
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *egg-info/

###
# Python build dependencies
##

$(BUILD_VENV)/bin/pip-compile: $(BUILD_VENV)
	$(BUILD_PY) -m pip install -U pip-tools

$(BUILD_VENV)/bin/%: $(BUILD_VENV)
	$(BUILD_PY) -m pip install -U $*
