import os
from sys import platform


WORD_LIST_TEXT_FILE = 'data/wordlist/final.txt'

OUTPUT_DIR = 'data/out/articles'

THREADS = 4
PROXIES = [
    "http://107.172.4.200:1080",
    "http://185.174.63.188:3128",
    "http://116.58.227.199:53005",
    "http://193.37.152.6:3128",
    None
]


if platform == "darwin":
    default_redis_host = '127.0.0.1'
else:
    default_redis_host = 'redis_word_def_instance'

REDIS_HOST = os.environ.get('REDIS_HOST', default_redis_host)
REDIS_PORT = int(os.environ.get('REDIS_PORT', '6379'))
REDIS_DB = int(os.environ.get('REDIS_DB', '0'))

PERMUT_BATCH_SIZE = int(os.environ.get('PERMUT_BATCH_SIZE', '200'))

DEBUG = os.environ.get('DEBUG', '').lower() in {'1', 'true', 'yes'}
PORT = int(os.environ.get('PORT', '34001'))
