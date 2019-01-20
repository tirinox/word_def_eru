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


@app.route('/')
def welcome():
    return 'Welcome to word_def!'


@app.route('/<string:word>')
def index(word):
    try:
        word = get_word_from_request(word)
        return respond_json({
            'word': word,
            'defs': WordDefs(redis_db).get_word_def_dic_from_redis(word),
            'usage': WordUsage(redis_db).get_word_usage_count(word)
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

        result = WordDefs(redis_db).append_word_defs(word, defs)

        return respond_json({
            'result': 'ok',
            'was_definition_added': result
        })
    except Exception as e:
        return respond_error(e)


@app.route('/use/<string:word>')
def use_word(word):
    try:
        word = get_word_from_request(word)

        wu = WordUsage(redis_db)
        wu.increment_word_usage(word)

        return respond_json({
            'result': 'ok',
            'usage': wu.get_word_usage_count(word),
            'rate': wu.get_word_usage_rate(word)
        })
    except Exception as e:
        return respond_error(e)


@app.route('/usage/<string:word>')
def get_word_usage(word):
    try:
        word = get_word_from_request(word)

        wu = WordUsage(redis_db)
        rate = wu.get_word_usage_rate(word)
        usage_n = wu.get_word_usage_count(word)

        return respond_json({
            'result': 'ok',
            'usage': usage_n,
            'rate': rate
        })
    except Exception as e:
        return respond_error(e)


if __name__ == '__main__':
    app.run(debug=DEBUG, port=PORT, host='0.0.0.0')