from util import *
from config import *
from word_defs import WordDefs





def main():
    redis_db = get_redis()

    someword = 'EXCESS'

    wd = WordDefs(redis_db, someword)
    print(wd.load_defs())


if __name__ == '__main__':
    main()