.PHONY: dev
dev: clean
	python -m pip install --upgrade setuptools wheel pip pytest_remotedata
	python -m pip install --upgrade -e .[dev]
	pre-commit install -f --install-hooks

.PHONY: install
install:
	pip install --upgrade setuptools wheel pip
	pip install .[tests]

.PHONY: install-py2
install-py2:
	python2 -m pip install --upgrade setuptools wheel pip
	python2 -m pip install .[tests]

.PHONY: install-py3
install-py3:
	python3 -m pip install --upgrade setuptools wheel pip
	python3 -m pip install .[tests]

.PHONY: install-pypy
install-pypy:
	pypy -m pip install --upgrade setuptools wheel pip
	pypy -m pip install .[tests]

.PHONY: install-pypy3
install-pypy3:
	pypy3 -m pip install --upgrade setuptools wheel pip
	pypy3 -m pip install .[tests]

.PHONY: format
format: dev
	pre-commit autoupdate
	pre-commit run --all-files

# test-all takes a very long time and should usually only be run by Travis
.PHONY: test-all
test-all: clean
	pytest --strict -s ./tests

# for quickly testing nearly everything locally, just use test-basic
.PHONY: test-basic
test-basic:
	python ./tests --strict --line-numbers --force
	python ./tests/dest/runner.py
	python ./tests/dest/extras.py

# same as test-basic, but doesn't recompile unchanged test files;
# should only be used when testing the tests not the compiler
.PHONY: test-tests
test-tests:
	python ./tests --strict --line-numbers
	python ./tests/dest/runner.py
	python ./tests/dest/extras.py

# same as test-basic but uses Python 2
.PHONY: test-py2
test-py2:
	python2 ./tests --strict --line-numbers --force
	python2 ./tests/dest/runner.py
	python2 ./tests/dest/extras.py

# same as test-basic but uses Python 3
.PHONY: test-py3
test-py3:
	python3 ./tests --strict --line-numbers --force
	python3 ./tests/dest/runner.py
	python3 ./tests/dest/extras.py

# same as test-basic but uses PyPy
.PHONY: test-pypy
test-pypy:
	pypy ./tests --strict --line-numbers --force
	pypy ./tests/dest/runner.py
	pypy ./tests/dest/extras.py

# same as test-basic but uses PyPy3
.PHONY: test-pypy3
test-pypy3:
	pypy3 ./tests --strict --line-numbers --force
	pypy3 ./tests/dest/runner.py
	pypy3 ./tests/dest/extras.py

# same as test-basic but also runs mypy
.PHONY: test-mypy
test-mypy:
	python ./tests --strict --line-numbers --force --target sys --mypy --follow-imports silent --ignore-missing-imports
	python ./tests/dest/runner.py
	python ./tests/dest/extras.py

# same as test-mypy but uses the universal target
.PHONY: test-mypy-univ
test-mypy-univ:
	python ./tests --strict --line-numbers --force --mypy --follow-imports silent --ignore-missing-imports
	python ./tests/dest/runner.py
	python ./tests/dest/extras.py

# same as test-basic but includes verbose output for better debugging
.PHONY: test-verbose
test-verbose:
	python ./tests --strict --line-numbers --force --verbose --jobs 0
	python ./tests/dest/runner.py
	python ./tests/dest/extras.py

# same as test-basic but also tests easter eggs
.PHONY: test-easter-eggs
test-easter-eggs:
	python ./tests --strict --line-numbers --force
	python ./tests/dest/runner.py --test-easter-eggs
	python ./tests/dest/extras.py

# same as test-basic but uses python pyparsing
.PHONY: test-pyparsing
test-pyparsing: COCONUT_PURE_PYTHON=TRUE
test-pyparsing: test-basic

# same as test-basic but uses --minify
.PHONY: test-minify
test-minify:
	python ./tests --strict --line-numbers --force --minify --jobs 0
	python ./tests/dest/runner.py
	python ./tests/dest/extras.py

# same as test-basic but watches tests before running them
.PHONY: test-watch
test-watch:
	python ./tests --strict --line-numbers --force
	coconut ./tests/src/cocotest/agnostic ./tests/dest/cocotest --watch --strict --line-numbers
	python ./tests/dest/runner.py
	python ./tests/dest/extras.py

.PHONY: diff
diff:
	git diff origin/develop

.PHONY: docs
docs: clean
	sphinx-build -b html . ./docs
	rm -f index.rst

.PHONY: clean
clean:
	rm -rf ./docs ./dist ./build ./tests/dest ./pyprover ./pyston ./coconut-prelude index.rst profile.json
	-find . -name '*.pyc' -delete
	-C:/GnuWin32/bin/find.exe . -name '*.pyc' -delete
	-find . -name '__pycache__' -delete
	-C:/GnuWin32/bin/find.exe . -name '__pycache__' -delete

.PHONY: wipe
wipe: clean
	-pip uninstall coconut
	-pip uninstall coconut-develop
	-pip3 uninstall coconut
	-pip3 uninstall coconut-develop
	-pip2 uninstall coconut
	-pip2 uninstall coconut-develop
	rm -rf *.egg-info

.PHONY: just-upload
just-upload:
	python setup.py sdist bdist_wheel
	pip install --upgrade --ignore-installed twine
	twine upload dist/*

.PHONY: upload
upload: clean dev just-upload

.PHONY: check-reqs
check-reqs:
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
