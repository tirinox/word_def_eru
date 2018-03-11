DEBUG = False
PORT = 34001


from flask import Flask, jsonify, json, Response, request
from util import *

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


@app.route('/<string:word>')
def index(word):
    try:
        return respond_json({
            'word': word,
            'defs': get_word_def_dic_from_redis(redis_db, word.upper())
        })
    except Exception as e:
        return respond_error(e)


@app.route('/add', methods=['POST'])
def add():
    try:
        content = request.get_json(silent=True)
        word = content['word']
        word_len = len(word)
        if not isinstance(word, str) or word_len < 2 or word_len > 30:
            raise Exception('invalid word')

        word = word.upper()

        defs = content['defs']
        if not isinstance(defs, list) or len(defs) < 1 or len(defs) > 10:
            raise Exception('invalid defs')

        result = append_word_defs(redis_db, word, defs)

        return respond_json({
            'result': 'ok',
            'was_definition_added': result
        })
    except Exception as e:
        return respond_error(e)


if __name__ == '__main__':
    app.run(debug=DEBUG, port=PORT, host='0.0.0.0')