MAKEFLAGS += -j2

.PHONY:
dev: dev_api dev_pages

.PHONY:
dev_api:
	$(MAKE) -C yark-api dev

.PHONY:
dev_pages:
	$(MAKE) -C yark-pages dev

.PHONY:
fmt:
	$(MAKE) -C yark fmt
	$(MAKE) -C yark-api fmt
	$(MAKE) -C yark-pages fmt
