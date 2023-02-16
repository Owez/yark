.PHONY:
all: fmt lint dev

.PHONY:
install:
	poetry install

.PHONY:
fmt: install
	poetry run black yark_api

.PHONY:
lint: install
	poetry run mypy yark_api
	poetry run pylint yark_api

.PHONY:
dev: install
	echo "Starting yark-api development server.."
	poetry run flask --app yark_api --debug run --port=7666

.PHONY:
build: install
	echo "Building yark-api into a prepacked executable.."
	poetry run pyinstaller launcher.py --name yark-api
	echo "You can find the executable resources at the dist/yark-api directory!"

.PHONY:
flask_shell: install
	echo "Booting into the Flask interactive shell.."
	poetry run flask --app yark_api shell
	echo "Exited the Flask interactive shell!"
