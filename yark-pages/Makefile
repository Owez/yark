.PHONY:
all: fmt lint dev

.PHONY:
install:
	npm install

.PHONY:
fmt: install
	npm run fmt

.PHONY:
lint: install
	npm run lint

.PHONY:
dev: install
	echo "Starting yark-pages development server.."
	npm run tauri dev