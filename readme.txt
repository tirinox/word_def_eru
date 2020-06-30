1. Run Redis locally

redis-server /usr/local/etc/redis.conf

------------------------------------------------------------------------------------------------------------------------

2. Copy Redis DB from Hetzner to local db dir (macbook air)
(not docker)

scp hetzner:/var/lib/redis/dump.rdb /usr/local/var/db/redis

for docker:

1) stop redis in docker
2) replace dump.rdb in compose_erudite/redisdata

------------------------------------------------------------------------------------------------------------------------

3. Erudite admin: add word defs from MySQL to Redis:

{
  "method": "temporaryWordDefsProcessing"
}

------------------------------------------------------------------------------------------------------------------------

4. Redis get dir

redis-cli
config get dir

------------------------------------------------------------------------------------------------------------------------


~~~~~~

How to run purify_defs.py

docker ps | grep word_def
docker exec -it 0711 /bin/sh
cd tools && PYTHONPATH=.. python3 purify_defs.py
