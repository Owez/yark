.PHONY:
all: fmt lint

.PHONY:
install:
	poetry install

.PHONY:
fmt: install
	poetry run black yark

.PHONY:
lint: install
	poetry run mypy yark
	poetry run pylint yark
