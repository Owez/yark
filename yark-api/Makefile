all: fmt lint dev

install:
	poetry install

fmt: install
	poetry run black yark_api

lint: install
	poetry run mypy yark_api
	poetry run pylint yark_api

dev: install
	echo "Starting yark-api development server.."
	poetry run flask --app yark_api --debug run --port=7666
