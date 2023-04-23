# the main test command to use when developing rapidly
.PHONY: test
test: test-mypy

.PHONY: dev
dev: clean setup
	python -m pip install --upgrade -e .[dev]
	pre-commit install -f --install-hooks
	coconut --site-install

.PHONY: dev-py2
dev-py2: clean setup-py2
	python2 -m pip install --upgrade -e .[dev]
	coconut --site-install

.PHONY: dev-py3
dev-py3: clean setup-py3
	python3 -m pip install --upgrade -e .[dev]
	pre-commit install -f --install-hooks
	coconut --site-install

.PHONY: setup
setup:
	python -m ensurepip
	python -m pip install --upgrade setuptools wheel pip pytest_remotedata

.PHONY: setup-py2
setup-py2:
	python2 -m ensurepip
	python2 -m pip install --upgrade "setuptools<58" wheel pip pytest_remotedata

.PHONY: setup-py3
setup-py3:
	python3 -m ensurepip
	python3 -m pip install --upgrade setuptools wheel pip pytest_remotedata

.PHONY: setup-pypy
setup-pypy:
	pypy -m ensurepip
	pypy -m pip install --upgrade "setuptools<58" wheel pip pytest_remotedata

.PHONY: setup-pypy3
setup-pypy3:
	pypy3 -m ensurepip
	pypy3 -m pip install --upgrade setuptools wheel pip pytest_remotedata

.PHONY: install
install: setup
	python -m pip install -e .[tests]

.PHONY: install-py2
install-py2: setup-py2
	python2 -m pip install -e .[tests]

.PHONY: install-py3
install-py3: setup-py3
	python3 -m pip install -e .[tests]

.PHONY: install-pypy
install-pypy:
	pypy -m pip install -e .[tests]

.PHONY: install-pypy3
install-pypy3:
	pypy3 -m pip install -e .[tests]

.PHONY: format
format: dev
	pre-commit autoupdate
	pre-commit run --all-files

# test-all takes a very long time and should usually only be run by CI
.PHONY: test-all
test-all: clean
	pytest --strict-markers -s ./coconut/tests

# basic testing for the universal target
.PHONY: test-univ
test-univ: export COCONUT_USE_COLOR=TRUE
test-univ: clean
	python ./coconut/tests --strict --line-numbers --keep-lines --force
	python ./coconut/tests/dest/runner.py
	python ./coconut/tests/dest/extras.py

# same as test-univ, but doesn't recompile unchanged test files;
# should only be used when testing the tests not the compiler
.PHONY: test-tests
test-tests: export COCONUT_USE_COLOR=TRUE
test-tests: clean
	python ./coconut/tests --strict --line-numbers --keep-lines
	python ./coconut/tests/dest/runner.py
	python ./coconut/tests/dest/extras.py

# same as test-univ but uses Python 2
.PHONY: test-py2
test-py2: export COCONUT_USE_COLOR=TRUE
test-py2: clean
	python2 ./coconut/tests --strict --line-numbers --keep-lines --force
	python2 ./coconut/tests/dest/runner.py
	python2 ./coconut/tests/dest/extras.py

# same as test-univ but uses Python 3 and --target 3
.PHONY: test-py3
test-py3: export COCONUT_USE_COLOR=TRUE
test-py3: clean
	python3 ./coconut/tests --strict --line-numbers --keep-lines --force --target 3
	python3 ./coconut/tests/dest/runner.py
	python3 ./coconut/tests/dest/extras.py

# same as test-univ but uses PyPy
.PHONY: test-pypy
test-pypy: export COCONUT_USE_COLOR=TRUE
test-pypy: clean
	pypy ./coconut/tests --strict --line-numbers --keep-lines --force
	pypy ./coconut/tests/dest/runner.py
	pypy ./coconut/tests/dest/extras.py

# same as test-univ but uses PyPy3
.PHONY: test-pypy3
test-pypy3: export COCONUT_USE_COLOR=TRUE
test-pypy3: clean
	pypy3 ./coconut/tests --strict --line-numbers --keep-lines --force
	pypy3 ./coconut/tests/dest/runner.py
	pypy3 ./coconut/tests/dest/extras.py

# same as test-pypy3 but includes verbose output for better debugging
.PHONY: test-pypy3-verbose
test-pypy3-verbose: export COCONUT_USE_COLOR=TRUE
test-pypy3-verbose: clean
	pypy3 ./coconut/tests --strict --line-numbers --keep-lines --force --verbose --jobs 0
	pypy3 ./coconut/tests/dest/runner.py
	pypy3 ./coconut/tests/dest/extras.py

# same as test-univ but also runs mypy
.PHONY: test-mypy
test-mypy: export COCONUT_USE_COLOR=TRUE
test-mypy: clean
	python ./coconut/tests --strict --force --target sys --keep-lines --mypy --follow-imports silent --ignore-missing-imports --allow-redefinition
	python ./coconut/tests/dest/runner.py
	python ./coconut/tests/dest/extras.py

# same as test-mypy but uses the universal target
.PHONY: test-mypy-univ
test-mypy-univ: export COCONUT_USE_COLOR=TRUE
test-mypy-univ: clean
	python ./coconut/tests --strict --force --keep-lines --mypy --follow-imports silent --ignore-missing-imports --allow-redefinition
	python ./coconut/tests/dest/runner.py
	python ./coconut/tests/dest/extras.py

# same as test-univ but includes verbose output for better debugging
.PHONY: test-verbose
test-verbose: export COCONUT_USE_COLOR=TRUE
test-verbose: clean
	python ./coconut/tests --strict --line-numbers --keep-lines --force --verbose --jobs 0
	python ./coconut/tests/dest/runner.py
	python ./coconut/tests/dest/extras.py

# same as test-mypy but uses --verbose
.PHONY: test-mypy-verbose
test-mypy-verbose: export COCONUT_USE_COLOR=TRUE
test-mypy-verbose: clean
	python ./coconut/tests --strict --force --target sys --verbose --jobs 0 --keep-lines --mypy --follow-imports silent --ignore-missing-imports --allow-redefinition
	python ./coconut/tests/dest/runner.py
	python ./coconut/tests/dest/extras.py

# same as test-mypy but uses --check-untyped-defs
.PHONY: test-mypy-all
test-mypy-all: export COCONUT_USE_COLOR=TRUE
test-mypy-all: clean
	python ./coconut/tests --strict --force --target sys --keep-lines --mypy --follow-imports silent --ignore-missing-imports --allow-redefinition --check-untyped-defs
	python ./coconut/tests/dest/runner.py
	python ./coconut/tests/dest/extras.py

# same as test-univ but also tests easter eggs
.PHONY: test-easter-eggs
test-easter-eggs: export COCONUT_USE_COLOR=TRUE
test-easter-eggs: clean
	python ./coconut/tests --strict --line-numbers --keep-lines --force
	python ./coconut/tests/dest/runner.py --test-easter-eggs
	python ./coconut/tests/dest/extras.py

# same as test-univ but uses python pyparsing
.PHONY: test-pyparsing
test-pyparsing: export COCONUT_PURE_PYTHON=TRUE
test-pyparsing: test-univ

# same as test-univ but uses --minify
.PHONY: test-minify
test-minify: export COCONUT_USE_COLOR=TRUE
test-minify: clean
	python ./coconut/tests --strict --line-numbers --keep-lines --force --minify
	python ./coconut/tests/dest/runner.py
	python ./coconut/tests/dest/extras.py

# same as test-univ but watches tests before running them
.PHONY: test-watch
test-watch: export COCONUT_USE_COLOR=TRUE
test-watch: clean
	python ./coconut/tests --strict --line-numbers --keep-lines --force
	coconut ./coconut/tests/src/cocotest/agnostic ./coconut/tests/dest/cocotest --watch --strict --line-numbers --keep-lines
	python ./coconut/tests/dest/runner.py
	python ./coconut/tests/dest/extras.py

# mini test that just compiles agnostic tests with fully synchronous output
.PHONY: test-mini
test-mini:
	coconut ./coconut/tests/src/cocotest/agnostic ./coconut/tests/dest/cocotest --force --jobs 0

.PHONY: debug-test-crash
debug-test-crash:
	python -X dev ./coconut/tests/dest/runner.py

.PHONY: diff
diff:
	git diff origin/develop

.PHONY: fix-develop
fix-develop:
	git merge master -s ours

.PHONY: docs
docs: clean
	sphinx-build -b html . ./docs
	rm -f index.rst

.PHONY: clean
clean:
	rm -rf ./docs ./dist ./build ./coconut/tests/dest ./bbopt ./pyprover ./pyston ./coconut-prelude index.rst ./.mypy_cache

.PHONY: wipe
wipe: clean
	rm -rf vprof.json profile.log *.egg-info
	-find . -name "__pycache__" -delete
	-C:/GnuWin32/bin/find.exe . -name "__pycache__" -delete
	-find . -name "*.pyc" -delete
	-C:/GnuWin32/bin/find.exe . -name "*.pyc" -delete
	-python -m coconut --site-uninstall
	-python3 -m coconut --site-uninstall
	-python2 -m coconut --site-uninstall
	-pip uninstall coconut
	-pip uninstall coconut-develop
	-pip3 uninstall coconut
	-pip3 uninstall coconut-develop
	-pip2 uninstall coconut
	-pip2 uninstall coconut-develop

.PHONY: build
build:
	python setup.py sdist bdist_wheel

.PHONY: just-upload
just-upload: build
	pip install --upgrade --ignore-installed twine
	twine upload dist/*

.PHONY: upload
upload: wipe dev just-upload

.PHONY: check-reqs
check-reqs:
	python ./coconut/requirements.py

.PHONY: profile-parser
profile-parser: export COCONUT_PURE_PYTHON=TRUE
profile-parser:
	coconut ./coconut/tests/src/cocotest/agnostic ./coconut/tests/dest/cocotest --force --profile --verbose --recursion-limit 4096 2>&1 | tee ./profile.log

.PHONY: profile-time
profile-time:
	vprof -c h "./coconut ./coconut/tests/src/cocotest/agnostic ./coconut/tests/dest/cocotest --force" --output-file ./vprof.json

.PHONY: profile-memory
profile-memory:
	vprof -c m "./coconut ./coconut/tests/src/cocotest/agnostic ./coconut/tests/dest/cocotest --force" --output-file ./vprof.json

.PHONY: view-profile
view-profile:
	vprof --input-file ./vprof.json
