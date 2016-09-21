.PHONY: install dev clean docs build

install:
	pip install --upgrade .[all]

dev:
	pip install --upgrade -e .[dev]

clean:
	rm -rf ./_docs
	rm -rf ./dist
	rm -rf ./build
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

docs: clean
	sphinx-build -b html . ./_docs
	pushd ./_docs
	cp ./README.html ./index.html
	zip -r ./_docs.zip ./*
	popd

build: clean
	python setup.py sdist bdist_wheel
