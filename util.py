import hashlib
from config import *
from redis import Redis
import json
import codecs
import requests


def get_redis():
    print('Connecting to Redis: {}:{}/{}'.format(REDIS_HOST, REDIS_PORT, REDIS_DB))
    return Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)


def word_def_key(word):
    return 'word_def_' + hashlib.sha1(word.encode('utf-8')).hexdigest()


def save_to_redis(r: Redis, word, defs):
    key = word_def_key(word)
    def_json = json.dumps(defs, ensure_ascii=False)
    r.set(key, def_json)



MAX_DEF_LEN = 320


def _find_definition(current_defs, def_text):
    for current_def in current_defs:
        if 'text' in current_def:
            current_def_text = current_def['text']
            if current_def_text == def_text:
                return True
    return False


def append_word_defs(r: Redis, word, defs):
    current_defs = get_word_def_dic_from_redis(r, word)

    updated = False
    for new_definition in defs:
        if isinstance(new_definition, str) and len(new_definition) >= 3:
            new_definition = new_definition.strip()
            new_definition = new_definition[:MAX_DEF_LEN]

            if not _find_definition(current_defs, new_definition):
                current_defs.append({
                    'text': new_definition
                })
                updated = True

    if updated:
        save_to_redis(r, word, current_defs)
    return updated


def is_there_definition(r: Redis, word, count_empty=True):
    entry = r.get(word_def_key(word))
    if entry is None:
        return False
    if not count_empty and entry == "[]":
        return False
    return True


def get_word_def_dic_from_redis(r, word):
    text = r.get(word_def_key(word))
    return json.loads(text) if text is not None else []


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
    '''Split the list, xs, into n chunks'''
    L = len(xs)
    assert 0 < n <= L
    s = L // n
    return [xs[p:p + s] for p in range(0, L, s)]


def json_pp(json_data):
    print(json.dumps(json_data, indent=4, ensure_ascii=False))
