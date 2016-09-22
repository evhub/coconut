.PHONY: install dev format clean docs build

install:
	pip install --upgrade .[all]

dev:
	pip install --upgrade -e .[dev]
	pre-commit install

format:
	pre-commit autoupdate
	pre-commit run

clean:
	pre-commit clean
	rm -rf ./docs
	rm -rf ./dist
	rm -rf ./build
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

docs: clean
	sphinx-build -b html . ./docs
	pushd ./docs
	cp ./README.html ./index.html
	zip -r ./docs.zip ./*
	popd

build: clean
	python setup.py sdist bdist_wheel
