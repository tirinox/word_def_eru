import hashlib
from config import *
import redis
import json
import codecs
import requests


def get_redis():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)


def word_def_key(word):
    return 'word_def_' + hashlib.sha1(word.encode('utf-8')).hexdigest()


def is_there_definition(r, word):
    entry = r.get(word_def_key(word))
    return entry is not None # and entry != '[]'


def get_word_def_dic_from_redis(r, word):
    text = r.get(word_def_key(word))
    return json.loads(text)


def read_all_words_from_dictionary(dictionary_filename):
    with codecs.open(dictionary_filename, 'r', encoding='utf-8') as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    return [x.strip() for x in content]


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
    '''Split the list, xs, into n chunks'''
    L = len(xs)
    assert 0 < n <= L
    s = L // n
    return [xs[p:p + s] for p in range(0, L, s)]
