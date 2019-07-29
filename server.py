DEBUG = False
PORT = 34001

from flask import Flask, json, Response, request
from util import *
from word_defs import WordDefs
from word_usage import WordUsage

redis_db = get_redis()

app = Flask(__name__)


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


def get_word_from_request(content):
    word = content if type(content) is str else content['word']
    word_len = len(word)
    if not isinstance(word, str) or word_len < 2 or word_len > 30:
        raise Exception('invalid word')

    word = word.upper()
    return word


def format_usage(usage: WordUsage):
    profile_id, score = usage.get_best_profile_id_and_score()
    count = usage.get_word_usage_count()
    return {
        'word': usage.word,
        'usage': count,
        'rate': usage.get_word_usage_rate(count),
        'best': {
            'profile_id': profile_id,
            'score': score
        }
    }


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
            **format_usage(usage),
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

        return respond_json({
            'result': 'ok',
            **format_usage(wu)
        })
    except Exception as e:
        return respond_error(e)


@app.route('/use/<string:word>')
def use_word(word):
    try:
        word = get_word_from_request(word)

        wu = WordUsage(redis_db, word)
        wu.increment_word_usage()

        return respond_json({
            'result': 'ok',
            **format_usage(wu)
        })
    except Exception as e:
        return respond_error(e)


@app.route('/usage/<string:word>')
def get_word_usage(word):
    try:
        word = get_word_from_request(word)
        wu = WordUsage(redis_db, word)

        return respond_json({
            'result': 'ok',
            **format_usage(wu)
        })
    except Exception as e:
        return respond_error(e)


if __name__ == '__main__':

    # wu = WordUsage(redis_db, 'пиво')
    # for n in range(0, wu.get_max_usage() + 1):
    #     print(n, '\t', wu.get_word_usage_rate(n))
    # exit()

    app.run(debug=DEBUG, port=PORT, host='0.0.0.0')
