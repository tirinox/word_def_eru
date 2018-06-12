from util import *
import codecs

def find_orphans(redis):
    words = read_all_words_from_dictionary(WORD_LIST_TEXT_FILE)

    orphans = []

    i = 1
    n = len(words)
    for word in words:
        value = get_word_def_dic_from_redis(redis, word)
        if value is None or value == []:
            orphans.append(word)
            print("[{}/{}] {}".format(i, n, word))

        i += 1

    orphans.sort(key=len)

    with codecs.open('data/orphans.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(orphans))


redis = get_redis()

# print(get_word_def_dic_from_redis(redis, 'ПИВО'))

find_orphans(redis)