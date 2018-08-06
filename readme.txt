1. Run Redis locally

redis-server /usr/local/etc/redis.conf

------------------------------------------------------------------------------------------------------------------------

2. Copy Redis DB from Hetzner to local db dir (macbook air)

scp hetzner:/var/lib/redis/dump.rdb /usr/local/var/db/redis

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

