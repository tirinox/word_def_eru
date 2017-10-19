WORD_LIST_TEXT_FILE = 'data/raw/final.txt'
OUTPUT_DIR = 'data/out/articles'
THREADS = 1
PROXIES = [
    "http://107.172.4.200:1080",
    "http://185.174.63.188:3128",
    None
]

# REDIS_HOST = 'redis_word_def_instance'  # FOR LIVE SERVER
REDIS_HOST = 'localhost' # for developement (local)

REDIS_PORT = '6379'
REDIS_DB = 0