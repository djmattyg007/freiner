SHELL = bash

# HOST_OS = $(shell uname -s)
# ifeq ("$(HOST_OS)", "Darwin")
# HOST_IP = $(shell ipconfig getifaddr en0)
# else
# HOST_IP = $(shell hostname -I | awk '{print $$1}')
# endif

docker-down:
	docker-compose down --remove-orphans

docker-up: docker-down
# 	HOST_OS=$(HOST_OS) HOST_IP=$(HOST_IP) docker-compose up -d
	docker-compose up -d
	#docker exec -i limits_redis-cluster-5_1 bash -c "echo yes | redis-cli --cluster create --cluster-replicas 1 $(HOST_IP):{7000..7005}"

setup-test-backends: docker-up

tests: setup-test-backends
	pytest -m unit --durations=10

integration-tests: setup-test-backends
	pytest -m integration

all-tests: setup-test-backends
	pytest -m unit,integration --durations=10

.PHONY: test
