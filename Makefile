.PHONY: install
install:
	pip install "setuptools>=18.8.1"
	pip install "pip>=7.1.2"
	pip install .[tests]

.PHONY: dev
dev:
	pip3 install --upgrade setuptools pip
	pip3 install --upgrade -e .[dev]
	pre-commit install -f --install-hooks

.PHONY: format
format:
	pre-commit autoupdate
	pre-commit run --allow-unstaged-config --all-files

.PHONY: test
test:
	pytest --strict -s tests

.PHONY: docs
docs: clean
	sphinx-build -b html . ./docs
	cp ./docs/README.html ./docs/index.html
	pushd ./docs; zip -r ./docs.zip ./*; popd

.PHONY: clean
clean:
	rm -rf ./docs ./dist ./build ./tests/dest
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
	python3 setup.py sdist bdist_wheel

.PHONY: upload
upload: build
	pip3 install --upgrade twine
	twine upload dist/*

.PHONY: check
check:
	python ./coconut/requirements.py
