from util import *
from config import *

def main():
    r = get_redis()

    test = get_word_def_dic_from_redis(r, 'АЭРОФИНИШЕР')[1]['href']
    print(test)

if __name__ == '__main__':
    main()