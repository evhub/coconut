.PHONY: install dev pip format docs test clean build

install: pip
	pip install .[all]

dev: pip
	pip install --upgrade -e .[dev]
	pre-commit install -f --install-hooks

pip:
	pip install "pip>=7.1.2"

format:
	pre-commit autoupdate
	pre-commit run --allow-unstaged-config --all-files

docs:
	sphinx-build -b html . ./docs
	pushd ./docs
	cp ./README.html ./index.html
	zip -r ./docs.zip ./*
	popd

test:
	pytest --strict -s tests

clean:
	rm -rf ./docs
	rm -rf ./dist
	rm -rf ./build
	rm -rf ./tests/dest
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

build: clean
	python setup.py sdist bdist_wheel
