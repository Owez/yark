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

clean:
	echo "Removing cache and all npm modules.."
	rm -rf .svelte-kit
	rm -rf node_modules

build: install api_build
	echo "Building production version of yark-api.."
