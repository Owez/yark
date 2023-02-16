all: fmt lint dev

install:
	npm install

fmt: install
	npm run fmt

lint: install
	npm run lint

dev: install
	echo "Starting yark-pages development server.."
	$(MAKE) -C ../yark-api build
	npm run tauri dev

build: install
	echo "Building production version of yark-api.."
	$(MAKE) -C ../yark-api build
