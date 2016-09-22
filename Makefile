.PHONY: install dev format docs clean build

install:
	pip install --upgrade .[all]

dev:
	pip install --upgrade -e .[dev]
	pre-commit install

format:
	pre-commit autoupdate
	pre-commit run --allow-unstaged-config --all-files

docs:
	sphinx-build -b html . ./docs
	pushd ./docs
	cp ./README.html ./index.html
	zip -r ./docs.zip ./*
	popd

clean:
	rm -rf ./docs
	rm -rf ./dist
	rm -rf ./build
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

build: clean
	python setup.py sdist bdist_wheel
