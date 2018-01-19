.PHONY: install
install:
	pip install "pip>=7.1.2"
	pip install .[tests]

.PHONY: dev
dev:
	pip install --upgrade setuptools pip
	pip install --upgrade -e .[dev]
	pre-commit install -f --install-hooks

.PHONY: format
format: dev
	pre-commit autoupdate
	pre-commit run --all-files

# test-all takes a very long time and should usually only be run by Travis
.PHONY: test-all
test-all:
	pytest --strict -s tests

# for quickly testing nearly everything locally, just use test-basic
.PHONY: test-basic
test-basic:
	python ./tests --force
	python ./tests/dest/runner.py
	python ./tests/dest/extras.py

# same as test-basic but also runs mypy
.PHONY: test-mypy
test-mypy:
	python ./tests --force --mypy --follow-imports silent --ignore-missing-imports
	python ./tests/dest/runner.py
	python ./tests/dest/extras.py

# same as test-basic but includes verbose output for better debugging
.PHONY: test-verbose
test-verbose:
	python ./tests --force --verbose --jobs 0
	python ./tests/dest/runner.py
	python ./tests/dest/extras.py

.PHONY: docs
docs: clean
	sphinx-build -b html . ./docs
	rm -f index.rst

.PHONY: clean
clean:
	rm -rf ./docs ./dist ./build ./tests/dest index.rst profile.json
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

.PHONY: wipe
wipe: clean
	-pip uninstall coconut
	-pip uninstall coconut-develop
	-pip3 uninstall coconut
	-pip3 uninstall coconut-develop
	-pip2 uninstall coconut
	-pip2 uninstall coconut-develop
	rm -rf *.egg-info

.PHONY: build
build: clean dev
	python setup.py sdist bdist_wheel

.PHONY: upload
upload: build
	pip install --upgrade twine
	twine upload dist/*

.PHONY: check
check:
	python ./coconut/requirements.py

.PHONY: profile-code
profile-code:
	vprof -c h "coconut tests/src/cocotest/agnostic tests/dest/cocotest --force" --output-file ./profile.json

.PHONY: profile-memory
profile-memory:
	vprof -c m "coconut tests/src/cocotest/agnostic tests/dest/cocotest --force" --output-file ./profile.json

.PHONY: view-profile
view-profile:
	vprof --input-file ./profile.json
