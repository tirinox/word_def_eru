from util import get_redis

redis_db = get_redis()

all_chars = {}

i = 0

for key in redis_db.scan_iter("word_def_*"):
    data = redis_db.get(key)
    for c in list(data):
        if not c in all_chars:
            all_chars[c] = 1
        else:
            all_chars[c] += 1

    i += 1
    if i % 100 == 0:
        print(i)



print(all_chars)
