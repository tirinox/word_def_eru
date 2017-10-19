DEBUG=False
PORT=34001

from flask import Flask, jsonify, json, Response
from util import *

redis_db = get_redis()

app = Flask(__name__)


@app.route('/<string:word>')
def index(word):

    word = word.upper()

    data = {
        'word': word,
        'defs': get_word_def_dic_from_redis(redis_db, word)
    }

    response = Response(
        response=json.dumps(data, ensure_ascii=False),
        status=200,
        mimetype='application/json'
    )
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

if __name__ == '__main__':
    app.run(debug=DEBUG, port=PORT, host='0.0.0.0')