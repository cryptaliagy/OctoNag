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

.PHONY: teardown
teardown:
	docker-compose \
		-f devstack/docker-compose.yml \
		down --rmi all

.PHONY: rebuild
rebuild:
	make teardown && make build

.PHONY: activate
activate:
	make teardown ; (make build && make run) ; make teardown