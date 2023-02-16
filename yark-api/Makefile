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

clean:
	echo "Removing old build/distribution files.."
	rm -rf build/
	rm -rf dist/

build: install
ifeq (,$(wildcard ./dist))
	echo "Building yark-api into a prepacked executable.."
	poetry run pyinstaller launcher.py -F --name yark-api
	echo "You can find the executable at the dist/yark-api file!"
else
	echo "Skipping building yark-api because dist exists!"
	echo "Tip: use `make clean` if and try again to fix this"
endif

flask_shell: install
	echo "Booting into the Flask interactive shell.."
	poetry run flask --app yark_api shell
	echo "Exited the Flask interactive shell!"
