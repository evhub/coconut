.PHONY: install
install:
	pip install "pip>=7.1.2"
	pip install .[tests]

.PHONY: dev
dev:
	pip3 install --upgrade pip
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

.PHONY: build
build: clean
	pip3 install --upgrade setuptools
	python3 setup.py sdist bdist_wheel

.PHONY: upload
upload: build
	pip3 install --upgrade twine
	twine upload dist/*

.PHONY: check
check:
	python ./coconut/requirements.py
