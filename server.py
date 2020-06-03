DEBUG = False
PORT = 34001

from flask import Flask, request
from util import *
from word_defs import WordDefs
from word_usage import WordUsage
from word_permutation import WordPermutations

redis_db = get_redis()

app = Flask(__name__)


@app.route('/')
def welcome():
    return 'Welcome to word_def!'


@app.route('/defs/<string:word>')
@fail_safe_json_responder
def index(word):
    word = get_word_from_request(word)

    defs = WordDefs(redis_db, word)
    usage = WordUsage(redis_db, word)

    return {
        **usage.to_json(),
        'defs': defs.load_defs(),
    }


@app.route('/add', methods=['POST'])
@fail_safe_json_responder
def add():
    content = request.get_json(silent=True)
    word = get_word_from_request(content)

    defs = content['defs']
    if not isinstance(defs, list) or len(defs) < 1 or len(defs) > 10:
        raise Exception('invalid defs')

    result = WordDefs(redis_db, word).append_word_defs(defs)

    return {
        'result': 'ok',
        'was_definition_added': result
    }


@app.route('/use/<string:word>/by/<int:profile_id>/score/<int:score>')
@fail_safe_json_responder
def use_word_ext(word, profile_id, score):
    word = get_word_from_request(word)
    profile_id = int(profile_id)
    score = int(score)

    wu = WordUsage(redis_db, word)
    wu.increment_word_usage()
    wu.update_max_score(profile_id, score)

    return wu.to_json()


@app.route('/use/<string:word>')
@fail_safe_json_responder
def use_word(word):
    word = get_word_from_request(word)

    wu = WordUsage(redis_db, word)
    wu.increment_word_usage()

    return wu.to_json()


@app.route('/usage/<string:word>')
@fail_safe_json_responder
def get_word_usage(word):
    word = get_word_from_request(word)
    wu = WordUsage(redis_db, word)

    return wu.to_json()


@app.route('/permuts/<string:lang>/<int:word_len>/<string:bucket>')
@fail_safe_json_responder
def permuts_get_words(lang, word_len, bucket):
    permuts = WordPermutations(redis_db, lang)
    variants = permuts.subsample(permuts.get_all_from_bucket(word_len, bucket), batch_size=PERMUT_BATCH_SIZE)
    return variants


if __name__ == '__main__':
    app.run(debug=DEBUG, port=PORT, host='0.0.0.0')
