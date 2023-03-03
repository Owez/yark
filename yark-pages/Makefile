all: fmt lint dev

install:
	npm install

fmt: install
	npm run fmt

lint: install
	npm run lint

api_clean:
	$(MAKE) -C ../yark-api clean

api_build:
	$(MAKE) -C ../yark-api build

dev: install api_build
	echo "Starting yark-pages development server.."
	echo "Tip: You don't need to restart this if you make changes to the API, the built-in API isn't used for development!"
	npm run tauri dev

build: install api_clean api_build
	echo "Building production version of yark-api.."
	npm run tauri build
