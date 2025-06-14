default: help

.PHONY: help
help: # Show help for each of the Makefile recipes.
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done


.PHONY: run
run: # Reindex the database.
	- docker network create word_def_network

	- docker stop redis_word_def_instance
	- docker rm redis_word_def_instance
	- docker run -p 6379:6379 -d -v "`pwd`/data/redisdata:/data" --name redis_word_def_instance --net=word_def_network --restart="always" redis:latest

	- docker stop word_def_instance
	- docker rm word_def_instance
	docker build -t word-def-local .
	docker run -p 34001:34001 -d --name word_def_instance --net=word_def_network --restart="always" word-def-local
