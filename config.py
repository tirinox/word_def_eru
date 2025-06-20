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

from sys import platform
if platform == "darwin":
    REDIS_HOST = '127.0.0.1'
else:
    REDIS_HOST = 'redis_word_def_instance'

REDIS_PORT = '6379'
REDIS_DB = 0

PERMUT_BATCH_SIZE = 200

DEBUG = False
PORT = 34001
