from util import *
from config import *
from word_defs import WordDefs
import json


def test_add(redis_db):
    with open('../data/mo.json', 'r') as f:
        content = json.load(f)

    word = get_word_from_request(content)

    defs = content['defs']
    if not isinstance(defs, list) or len(defs) < 1 or len(defs) > 20:
        raise Exception('invalid defs')

    result = WordDefs(redis_db, word).append_word_defs(defs)

    return {
        'result': 'ok',
        'was_definition_added': result
    }

def main():
    redis_db = get_redis()

    # print(test_add(redis_db))


    print(*WordDefs(redis_db, 'МО').load_defs(), sep='\n\n')

    # wd = WordDefs(redis_db, 'эйлерс')
    # wd.append_word_defs([
    #     {
    #         'text': 'магазинчик еды ололо',
    #         'imageURL': 'https://sun1-30.userapi.com/MDG7sfdXSkuD_6QtIhONI24931_SmcR3r8prpA/0D2GyafId-0.jpg'
    #     },
    #     {
    #         'text': 'принцип кино - больше сцен',
    #     }
    # ])
    #
    # print(wd.load_defs())
    # sep()

    # wd.update_def(2, {
    #     'text': 'изменено на другое 2',
    #     'imageURL': 'image...'
    # })




if __name__ == '__main__':
    main()
