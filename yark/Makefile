all: fmt lint

install:
	poetry install

fmt: install
	poetry run black yark

lint: install
	poetry run mypy yark
	poetry run pylint yark
