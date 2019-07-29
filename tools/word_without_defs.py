from util import *
import codecs


def find_orphans(redis):
    words = read_all_words_from_dictionary(WORD_LIST_TEXT_FILE)

    orphans = []

    i = 1
    n = len(words)
    for word in words:
        value = load_defs(redis, word)
        if value is None or value == []:
            orphans.append(word)
            print("[{}/{}] {}".format(i, n, word))

        i += 1

    orphans.sort(key=len)

    with codecs.open('data/orphans.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(orphans))

    total = len(orphans)
    print('Total: {}'.format(total))


redis = get_redis()

# print(load_defs(redis, 'ПИВО'))

find_orphans(redis)