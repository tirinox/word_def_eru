from util import *
from config import *
from tools import academic_parse
from fake_useragent import UserAgent

# ua = UserAgent()
#     session = create_new_session(ua)
#     test = academic_parse.download_word_definition('ПИЗДОХУЙ', session)
#     json_pp(test)


def main():
    redis_db = get_redis()

    someword = 'ПИЗОУЙ'
    d1 = get_word_def_dic_from_redis(redis_db, someword)
    json_pp(d1)
    x = append_word_defs(redis_db, someword, [
        'Противный столоездП! '
    ])
    print('Success?', x)

    d2 = get_word_def_dic_from_redis(redis_db, someword)
    json_pp(d2)


if __name__ == '__main__':
    main()