default: help

.PHONY: help
help: # Show help for each of the Makefile recipes.
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done


.PHONY: run
run: # Reindex the database.
	# Create network if it doesn't exist
	- docker network create word_def_network

	# Stop & remove old Redis instance
	- docker stop redis_word_def_instance
	- docker rm redis_word_def_instance

	# Start Redis with correct permissions
	docker run -d \
		--name redis_word_def_instance \
		--net=word_def_network \
		--restart="always" \
		-p 127.0.0.1:6379:6379 \
		-v "$(PWD)/data/redisdata:/data" \
		--user $(shell id -u):$(shell id -g) \
		redis:latest \
		redis-server --save 60 1 --dir /data

	# Stop & remove app instance
	- docker stop word_def_instance
	- docker rm word_def_instance

	# Rebuild and run app
	docker build -t word-def-local .
	docker run -d \
		--name word_def_instance \
		--net=word_def_network \
		--restart="always" \
		word-def-local


.PHONY: stop
stop: # Stop and delete Docker container if it exists
	docker stop push_eru_service_i || true
	docker rm push_eru_service_i || true


.PHONY: redeploy
redeploy:  # Git pull and redeploy the service.
	git pull
	# stop
	$(MAKE) stop
	$(MAKE) build
	$(MAKE) run

