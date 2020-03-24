from util import *
from word_defs import WordDefs
import codecs


def find_orphans(redis):
    words = read_all_words_from_dictionary('../data/wordlist/final.txt')

    orphans = []

    i = 1
    n = len(words)
    for word in words:
        wd = WordDefs(redis, word)
        value = wd.load_defs()
        if value is None or value == []:
            orphans.append(word)
            print("[{}/{}] {}".format(i, n, word))

        i += 1

    orphans.sort(key=len)

    with codecs.open('data/orphans1.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(orphans))

    total = len(orphans)
    print('Total: {}'.format(total))


redis = get_redis()


find_orphans(redis)