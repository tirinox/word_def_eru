IN_DIRECTORY = 'data/out/articles'
OUT_JSON_COMPOSITION = 'data/out/all_word_defs.json'

REDIS_HOST = 'localhost'
REDIS_PORT = '6379'
REDIS_DB = 0

import os
import codecs
import json
import redis


def get_file_list(path):
    return (file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file)))


def read_one_word_def(filename):
    with codecs.open(os.path.join(IN_DIRECTORY, filename), 'r', encoding='utf-8') as f:
        raw_text = f.read()
        json_data = json.loads(raw_text)
        word = json_data['word']
        defs = json_data['defs']
        return (word, defs)


def compose_to_json_file(files):
    all_infos = {}

    i = 1
    n = len(files)
    for file in files:
        word, defs = read_one_word_def(file)
        all_infos[word] = defs
        print("[{}/{}] {}".format(i, n, word))
        i += 1

    print("Writing the out file")
    with codecs.open(OUT_JSON_COMPOSITION, 'w', encoding='utf-8') as out_f:
        out_f.write(json.dumps(all_infos))


def compose_to_redis(files):
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

    i = 1
    n = len(files)
    for file in files:
        word, defs = read_one_word_def(file)

        defs_json = json.dumps(defs, ensure_ascii=False)

        r.set('word_def_' + word, defs_json)

        print("[{}/{}] {}".format(i, n, word))
        i += 1

if __name__ == '__main__':
    files = list(get_file_list(IN_DIRECTORY))
    compose_to_redis(files)
    print("done!")



