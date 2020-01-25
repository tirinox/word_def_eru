DEBUG = False
PORT = 34001

from flask import Flask, request
from util import *
from word_defs import WordDefs
from word_usage import WordUsage

redis_db = get_redis()

app = Flask(__name__)


@app.route('/')
def welcome():
    return 'Welcome to word_def!'


@app.route('/defs/<string:word>')
def index(word):
    try:
        word = get_word_from_request(word)

        defs = WordDefs(redis_db, word)
        usage = WordUsage(redis_db, word)

        return respond_json({
            **usage.to_json(),
            'defs': defs.load_defs(),
        })
    except Exception as e:
        return respond_error(e)


@app.route('/add', methods=['POST'])
def add():
    try:
        content = request.get_json(silent=True)
        word = get_word_from_request(content)

        defs = content['defs']
        if not isinstance(defs, list) or len(defs) < 1 or len(defs) > 10:
            raise Exception('invalid defs')

        result = WordDefs(redis_db, word).append_word_defs(defs)

        return respond_json({
            'result': 'ok',
            'was_definition_added': result
        })
    except Exception as e:
        return respond_error(e)


@app.route('/use/<string:word>/by/<int:profile_id>/score/<int:score>')
def use_word_ext(word, profile_id, score):
    try:
        word = get_word_from_request(word)
        profile_id = int(profile_id)
        score = int(score)

        wu = WordUsage(redis_db, word)
        wu.increment_word_usage()
        wu.update_max_score(profile_id, score)

        return respond_json(wu.to_json())
    except Exception as e:
        return respond_error(e)


@app.route('/use/<string:word>')
def use_word(word):
    try:
        word = get_word_from_request(word)

        wu = WordUsage(redis_db, word)
        wu.increment_word_usage()

        return respond_json(wu.to_json())
    except Exception as e:
        return respond_error(e)


@app.route('/usage/<string:word>')
def get_word_usage(word):
    try:
        word = get_word_from_request(word)
        wu = WordUsage(redis_db, word)

        return respond_json(wu.to_json())
    except Exception as e:
        return respond_error(e)


@app.route('/cache/get/<string:key>')
def get_cache_key():
    ...

if __name__ == '__main__':
    app.run(debug=DEBUG, port=PORT, host='0.0.0.0')
