from util import *
from word_defs import WordDefs

redis_db = get_redis()

wd = WordDefs(redis_db, 'АД')

print(wd.load_defs())