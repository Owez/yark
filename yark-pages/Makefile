all: fmt lint dev

install:
	npm install

fmt: install
	npm run fmt

lint: install
	npm run lint

api_build:
	$(MAKE) -C ../yark-api build

dev: install api_build
	echo "Starting yark-pages development server.."
	npm run tauri dev

build: install api_build
	echo "Building production version of yark-api.."
