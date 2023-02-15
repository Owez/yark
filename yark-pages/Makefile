all: fmt lint dev

install:
	npm install

fmt: install
	npm run fmt

lint: install
	npm run lint

dev: install
	echo "Starting yark-pages development server.."
	npm run tauri dev