from fake_useragent import UserAgent

import threading
import random

import academic_parse
from util import *


def save_to_redis(r, word, defs):
    key = word_def_key(word)
    def_json = json.dumps(defs, ensure_ascii=False)
    r.set(key, def_json)


ua = UserAgent()


def random_proxy():
    return random.choice(PROXIES)


def worker(thread_id, words):
    r = get_redis()

    n = len(words)
    proxy = random_proxy()

    print("THREAD #{} Started worker for N = {} words with proxy {}".format(thread_id, n, proxy))

    session = create_new_session(ua, proxy=proxy)

    i = 1
    for word in words:
        print("THREAD #{} -> [{}/{}] processing word: {} (key: {})".format(thread_id, i, n, word, word_def_key(word)))
        if not is_there_definition(r, word, count_empty=False):
            word_defs = academic_parse.download_word_definition(word, session=session)
            save_to_redis(r, word, word_defs)
            n_defs = len(word_defs)
            if n_defs > 0:
                print("{} defs added".format(n_defs))
        i += 1

    print("THREAD #{} finished!".format(thread_id))


def main():
    print("loading the word list")
    words = read_all_words_from_dictionary(WORD_LIST_TEXT_FILE)

    word_chunks = chunk_them(words, THREADS)

    threads = []
    thread_id = 1
    for chunk in word_chunks:
        thread = threading.Thread(target=worker, args=(thread_id, chunk,))
        thread.start()
        threads.append(thread)
        thread_id += 1

    for thread in threads:
        thread.join()

    print("ALL IS DONE!")


if __name__ == '__main__':
    main()
