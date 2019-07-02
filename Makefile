.PHONY: build
build:
	docker-compose \
		-f devstack/docker-compose.yml \
		build --force-rm octonag

.PHONY: run
run:
	docker-compose \
		-f devstack/docker-compose.yml \
		run --rm octonag

.PHONY: break
break:
	docker-compose \
		-f devstack/docker-compose.yml \
		down --rmi all