import hashlib
from config import *
from redis import Redis
import json
import codecs
import requests
from flask import Response
from functools import wraps


def get_redis():
    print('Connecting to Redis: {}:{}/{}'.format(REDIS_HOST, REDIS_PORT, REDIS_DB))
    return Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)


def fail_safe_json_responder(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            j = func(*args, **kwargs)
            j['result'] = 'ok'
            return respond_json(j)
        except Exception as e:
            return respond_error(e)
    return inner


def respond_json(json_data, status_code=200):
    response = Response(
        response=json.dumps(json_data, ensure_ascii=False),
        status=status_code,
        mimetype='application/json'
    )
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response


def respond_error(e):
    return respond_json({
        'result': 'error',
        'message': str(e)
    }, status_code=500)


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


def get_word_from_request(content):
    word = content if type(content) is str else content['word']
    word_len = len(word)
    if not isinstance(word, str) or word_len < 2 or word_len > 30:
        raise Exception('invalid word')

    word = word.upper()
    return word


def move_element_in_list(l: list, ident, direction):
    n = len(l)
    if ident < 0 or ident >= n:
        raise IndexError

    el = l.pop(ident)
    n -= 1

    if direction == 'up':
        ins_pt = max(0, ident - 1)
    elif direction == 'down':
        ins_pt = min(n, ident + 1)
    elif direction == 'top':
        ins_pt = 0
    elif direction == 'bottom':
        ins_pt = n
    else:
        raise ValueError('direction must be either [up, down, top, bottom]')

    l.insert(ins_pt, el)

    return l


def sep():
    print('-' * 100)
