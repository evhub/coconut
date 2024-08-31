# the main test command to use when developing rapidly
.PHONY: test
test: test-mypy

# same as test, but for testing only changes to the tests
.PHONY: test-tests
test-tests: test-mypy-tests

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
	-python -m ensurepip
	python -m pip install --upgrade setuptools wheel pip cython

.PHONY: setup-py2
setup-py2:
	-python2 -m ensurepip
	python2 -m pip install --upgrade "setuptools<58" wheel pip cython

.PHONY: setup-py3
setup-py3:
	-python3 -m ensurepip
	python3 -m pip install --upgrade setuptools wheel pip cython

.PHONY: setup-pypy
setup-pypy:
	-pypy -m ensurepip
	pypy -m pip install --upgrade "setuptools<58" wheel pip

.PHONY: setup-pypy3
setup-pypy3:
	-pypy3 -m ensurepip
	pypy3 -m pip install --upgrade setuptools wheel pip

.PHONY: install
install: setup
	python -m pip install -e .[tests]

.PHONY: install-purepy
install-purepy: setup
	python -m pip install --no-deps --upgrade -e . "pyparsing<3"

.PHONY: install-py2
install-py2: setup-py2
	python2 -m pip install -e .[tests]

.PHONY: install-py3
install-py3: setup-py3
	python3 -m pip install -e .[tests]

.PHONY: install-pypy
install-pypy: setup-pypy
	pypy -m pip install -e .[tests]

.PHONY: install-pypy3
install-pypy3: setup-pypy3
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
	python ./coconut/tests --strict --keep-lines --force
	python ./coconut/tests/dest/runner.py
	python ./coconut/tests/dest/extras.py

# same as test-univ, but doesn't recompile unchanged test files;
# should only be used when testing the tests not the compiler
.PHONY: test-univ-tests
test-univ-tests: export COCONUT_USE_COLOR=TRUE
test-univ-tests: clean-no-tests
	python ./coconut/tests --strict --keep-lines
	python ./coconut/tests/dest/runner.py
	python ./coconut/tests/dest/extras.py

# same as test-univ but uses Python 2
.PHONY: test-py2
test-py2: export COCONUT_USE_COLOR=TRUE
test-py2: clean
	python2 ./coconut/tests --strict --keep-lines --force
	python2 ./coconut/tests/dest/runner.py
	python2 ./coconut/tests/dest/extras.py

# same as test-univ but uses Python 3 and --target 3
.PHONY: test-py3
test-py3: export COCONUT_USE_COLOR=TRUE
test-py3: clean
	python3 ./coconut/tests --strict --keep-lines --force --target 3
	python3 ./coconut/tests/dest/runner.py
	python3 ./coconut/tests/dest/extras.py

# same as test-univ but uses PyPy
.PHONY: test-pypy
test-pypy: export COCONUT_USE_COLOR=TRUE
test-pypy: clean
	pypy ./coconut/tests --strict --keep-lines --force
	pypy ./coconut/tests/dest/runner.py
	pypy ./coconut/tests/dest/extras.py

# same as test-univ but uses PyPy3
.PHONY: test-pypy3
test-pypy3: export COCONUT_USE_COLOR=TRUE
test-pypy3: clean
	pypy3 ./coconut/tests --strict --keep-lines --force
	pypy3 ./coconut/tests/dest/runner.py
	pypy3 ./coconut/tests/dest/extras.py

# same as test-univ but reverses any ofs
.PHONY: test-any-of
test-any-of: export COCONUT_ADAPTIVE_ANY_OF=TRUE
test-any-of: export COCONUT_REVERSE_ANY_OF=TRUE
test-any-of: test-univ

# same as test-univ but also runs mypy
.PHONY: test-mypy-univ
test-mypy-univ: export COCONUT_USE_COLOR=TRUE
test-mypy-univ: clean
	python ./coconut/tests --strict --keep-lines --force --no-cache --mypy --follow-imports silent --ignore-missing-imports --allow-redefinition
	python ./coconut/tests/dest/runner.py
	python ./coconut/tests/dest/extras.py

# same as test-mypy-univ but uses --target sys
.PHONY: test-mypy
test-mypy: export COCONUT_USE_COLOR=TRUE
test-mypy: clean
	python ./coconut/tests --strict --keep-lines --force --target sys --no-cache --mypy --follow-imports silent --ignore-missing-imports --allow-redefinition
	python ./coconut/tests/dest/runner.py
	python ./coconut/tests/dest/extras.py

# same as test-mypy but doesn't use --force
.PHONY: test-mypy-tests
test-mypy-tests: export COCONUT_USE_COLOR=TRUE
test-mypy-tests: clean-no-tests
	python ./coconut/tests --strict --keep-lines --target sys --mypy --follow-imports silent --ignore-missing-imports --allow-redefinition
	python ./coconut/tests/dest/runner.py
	python ./coconut/tests/dest/extras.py

# same as test-mypy but uses pyright instead
.PHONY: test-pyright
test-pyright: export COCONUT_USE_COLOR=TRUE
test-pyright: clean
	python ./coconut/tests --strict --keep-lines --force --target sys --no-cache --pyright
	python ./coconut/tests/dest/runner.py
	python ./coconut/tests/dest/extras.py

# same as test-univ but includes verbose output for better debugging
#  regex for getting non-timing lines: ^(?!'|\s*(Time|Packrat|Loaded|Saving|Adaptive|Errorless|Grammar|Failed|Incremental|Pruned|Compiled)\s)[^\n]*\n*
.PHONY: test-verbose
test-verbose: export COCONUT_USE_COLOR=TRUE
test-verbose: clean
	python ./coconut/tests --strict --keep-lines --force --verbose
	python ./coconut/tests/dest/runner.py
	python ./coconut/tests/dest/extras.py

# same as test-verbose but reuses the incremental cache
.PHONY: test-verbose-cache
test-verbose-cache: export COCONUT_USE_COLOR=TRUE
test-verbose-cache: clean-no-tests
	python ./coconut/tests --strict --keep-lines --force --verbose
	python ./coconut/tests/dest/runner.py
	python ./coconut/tests/dest/extras.py

# same as test-verbose but doesn't use the incremental cache
.PHONY: test-verbose-no-cache
test-verbose-no-cache: export COCONUT_USE_COLOR=TRUE
test-verbose-no-cache: clean
	python ./coconut/tests --strict --keep-lines --force --verbose --no-cache
	python ./coconut/tests/dest/runner.py
	python ./coconut/tests/dest/extras.py

# same as test-verbose but is fully synchronous
.PHONY: test-verbose-sync
test-verbose-sync: export COCONUT_USE_COLOR=TRUE
test-verbose-sync: clean
	python ./coconut/tests --strict --keep-lines --force --verbose --jobs 0
	python ./coconut/tests/dest/runner.py
	python ./coconut/tests/dest/extras.py

# same as test-mypy but uses --verbose
.PHONY: test-mypy-verbose
test-mypy-verbose: export COCONUT_USE_COLOR=TRUE
test-mypy-verbose: clean
	python ./coconut/tests --strict --keep-lines --force --target sys --verbose --mypy --follow-imports silent --ignore-missing-imports --allow-redefinition
	python ./coconut/tests/dest/runner.py
	python ./coconut/tests/dest/extras.py

# same as test-mypy but uses --check-untyped-defs
.PHONY: test-mypy-all
test-mypy-all: export COCONUT_USE_COLOR=TRUE
test-mypy-all: clean
	python ./coconut/tests --strict --keep-lines --force --target sys --no-cache --mypy --follow-imports silent --ignore-missing-imports --allow-redefinition --check-untyped-defs
	python ./coconut/tests/dest/runner.py
	python ./coconut/tests/dest/extras.py

# same as test-univ but also tests easter eggs
.PHONY: test-easter-eggs
test-easter-eggs: export COCONUT_USE_COLOR=TRUE
test-easter-eggs: clean
	python ./coconut/tests --strict --keep-lines --force
	python ./coconut/tests/dest/runner.py --test-easter-eggs
	python ./coconut/tests/dest/extras.py

# same as test-univ but uses python pyparsing
.PHONY: test-purepy
test-purepy: export COCONUT_PURE_PYTHON=TRUE
test-purepy: test-univ

# same as test-univ but disables the computation graph
.PHONY: test-no-computation-graph
test-no-computation-graph: export COCONUT_USE_COMPUTATION_GRAPH=FALSE
test-no-computation-graph: test-univ

# same as test-univ but uses --minify
.PHONY: test-minify
test-minify: export COCONUT_USE_COLOR=TRUE
test-minify: clean
	python ./coconut/tests --strict --keep-lines --force --minify
	python ./coconut/tests/dest/runner.py
	python ./coconut/tests/dest/extras.py

# same as test-univ but uses --no-wrap
.PHONY: test-no-wrap
test-no-wrap: export COCONUT_USE_COLOR=TRUE
test-no-wrap: clean
	python ./coconut/tests --strict --keep-lines --force --no-wrap
	python ./coconut/tests/dest/runner.py
	python ./coconut/tests/dest/extras.py

# same as test-univ but watches tests before running them
.PHONY: test-watch
test-watch: export COCONUT_USE_COLOR=TRUE
test-watch: clean
	python ./coconut/tests --strict --keep-lines --force
	make just-watch
	python ./coconut/tests/dest/runner.py
	python ./coconut/tests/dest/extras.py

# just watches tests
.PHONY: just-watch
just-watch: export COCONUT_USE_COLOR=TRUE
just-watch:
	coconut ./coconut/tests/src/cocotest/agnostic ./coconut/tests/dest/cocotest --watch --strict --keep-lines --stack-size 4096 --recursion-limit 4096

# same as just-watch but uses verbose output and is fully sychronous and doesn't use the cache
.PHONY: just-watch-verbose
just-watch-verbose: export COCONUT_USE_COLOR=TRUE
just-watch-verbose:
	coconut ./coconut/tests/src/cocotest/agnostic ./coconut/tests/dest/cocotest --watch --strict --keep-lines --stack-size 4096 --recursion-limit 4096 --verbose --jobs 0 --no-cache

# mini test that just compiles agnostic tests
.PHONY: test-mini
test-mini: export COCONUT_USE_COLOR=TRUE
test-mini:
	coconut ./coconut/tests/src/cocotest/agnostic ./coconut/tests/dest/cocotest --force --stack-size 4096 --recursion-limit 4096

# same as test-mini but with verbose output
.PHONY: test-mini-verbose
test-mini-verbose: export COCONUT_USE_COLOR=TRUE
test-mini-verbose:
	coconut ./coconut/tests/src/cocotest/agnostic ./coconut/tests/dest/cocotest --force --verbose --stack-size 4096 --recursion-limit 4096

# same as test-mini-verbose but doesn't overwrite the cache
.PHONY: test-mini-cache
test-mini-cache: export COCONUT_ALLOW_SAVE_TO_CACHE=FALSE
test-mini-cache: test-mini-verbose

# same as test-mini-verbose but with fully synchronous output and fast failing
.PHONY: test-mini-sync
test-mini-sync: export COCONUT_USE_COLOR=TRUE
test-mini-sync:
	coconut ./coconut/tests/src/cocotest/agnostic ./coconut/tests/dest/cocotest --force --verbose --jobs 0 --fail-fast --stack-size 4096 --recursion-limit 4096

# same as test-univ but debugs crashes
.PHONY: test-univ-debug
test-univ-debug: export COCONUT_TEST_DEBUG_PYTHON=TRUE
test-univ-debug: test-univ

# same as test-mini but debugs crashes, is fully synchronous, and doesn't use verbose output
.PHONY: test-mini-debug
test-mini-debug: export COCONUT_USE_COLOR=TRUE
test-mini-debug:
	python -X dev -m coconut ./coconut/tests/src/cocotest/agnostic ./coconut/tests/dest/cocotest --strict --keep-lines --force --jobs 0 --stack-size 4096 --recursion-limit 4096

# same as test-mini-debug but uses vanilla pyparsing
.PHONY: test-mini-debug-purepy
test-mini-debug-purepy: export COCONUT_PURE_PYTHON=TRUE
test-mini-debug-purepy: test-mini-debug

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

.PHONY: clean-no-tests
clean-no-tests:
	rm -rf ./docs ./dist ./build ./bbopt ./pyprover ./pyston ./coconut-prelude index.rst ./.mypy_cache

.PHONY: clean
clean: clean-no-tests
	rm -rf ./coconut/tests/dest
	-find . -name "__coconut_cache__" -type d -prune -exec rm -rf '{}' +
	-powershell -Command "get-childitem -Include __coconut_cache__ -Recurse -force | Remove-Item -Force -Recurse"

.PHONY: wipe
wipe: clean
	rm -rf ./coconut/tests/dest vprof.json profile.log *.egg-info
	-find . -name "__pycache__" -type d -prune -exec rm -rf '{}' +
	-powershell -Command "get-childitem -Include __pycache__ -Recurse -force | Remove-Item -Force -Recurse"
	-find . -name "*.pyc" -delete
	-powershell -Command "get-childitem -Include *.pyc -Recurse -force | Remove-Item -Force -Recurse"
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
	twine upload dist/* -u __token__

.PHONY: upload
upload: wipe dev just-upload

.PHONY: check-reqs
check-reqs:
	python ./coconut/requirements.py

.PHONY: profile
profile: export COCONUT_USE_COLOR=TRUE
profile:
	coconut ./coconut/tests/src/cocotest/agnostic/util.coco ./coconut/tests/dest/cocotest --force --verbose --profile --stack-size 4096 --recursion-limit 4096 2>&1 | tee ./profile.log

.PHONY: open-speedscope
open-speedscope:
	npm install -g speedscope
	speedscope ./profile.speedscope

.PHONY: pyspy
pyspy:
	py-spy record -o profile.speedscope --format speedscope --subprocesses --rate 75 -- python -m coconut ./coconut/tests/src/cocotest/agnostic ./coconut/tests/dest/cocotest --force
	make open-speedscope

.PHONY: pyspy-purepy
pyspy-purepy: export COCONUT_PURE_PYTHON=TRUE
pyspy-purepy: pyspy

.PHONY: pyspy-native
pyspy-native:
	py-spy record -o profile.speedscope --format speedscope --native --rate 75 -- python -m coconut ./coconut/tests/src/cocotest/agnostic ./coconut/tests/dest/cocotest --force --jobs 0
	make open-speedscope

.PHONY: pyspy-runtime
pyspy-runtime:
	py-spy record -o runtime_profile.speedscope --format speedscope -- python ./coconut/tests/dest/runner.py
	speedscope ./runtime_profile.speedscope

.PHONY: vprof-time
vprof-time:
	vprof -c h "./coconut ./coconut/tests/src/cocotest/agnostic ./coconut/tests/dest/cocotest --force --jobs 0 --stack-size 4096 --recursion-limit 4096" --output-file ./vprof.json
	make view-vprof

.PHONY: vprof-memory
vprof-memory:
	vprof -c m "./coconut ./coconut/tests/src/cocotest/agnostic ./coconut/tests/dest/cocotest --force --jobs 0 --stack-size 4096 --recursion-limit 4096" --output-file ./vprof.json
	make view-vprof

.PHONY: view-vprof
view-vprof:
	vprof --input-file ./vprof.json
