MAKEFLAGS += -j2

dev: dev_api dev_pages

dev_api:
	$(MAKE) -C yark-api dev

dev_pages:
	$(MAKE) -C yark-pages dev
