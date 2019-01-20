import hashlib
from config import *
from redis import Redis
import json
import codecs
import requests


def get_redis():
    print('Connecting to Redis: {}:{}/{}'.format(REDIS_HOST, REDIS_PORT, REDIS_DB))
    return Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)


def word_hash(word):
    return hashlib.sha1(word.encode('utf-8')).hexdigest()


def int_or_default(v, default=0):
    return int(v) if v is not None else default


def read_all_words_from_dictionary(dictionary_filename, max_num=None):
    with codecs.open(dictionary_filename, 'r', encoding='utf-8') as f:
        content = f.readlines()

    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    content.sort(key=len)

    if max_num is not None:
        content = content[:max_num]

    return content


def create_new_session(user_agent_generator, proxy=None):
    s = requests.Session()
    s.headers.update({
        'User-Agent': user_agent_generator.random
    })
    if proxy is not None:
        s.proxies = {
            "http": proxy
        }
    return s


def chunk_them(xs, n):
    l = len(xs)
    assert 0 < n <= l
    s = l // n
    return [xs[p:p + s] for p in range(0, l, s)]


def json_pp(json_data):
    print(json.dumps(json_data, indent=4, ensure_ascii=False))
