MAKEFLAGS += -j2

dev: dev_api dev_pages

dev_api:
	$(MAKE) -C yark-api dev

dev_pages:
	$(MAKE) -C yark-pages dev

fmt:
	$(MAKE) -C yark fmt
	$(MAKE) -C yark-api fmt
	$(MAKE) -C yark-pages fmt

clean:
	$(MAKE) -C yark-api clean
	$(MAKE) -C yark-pages clean
