from util import *
from word_defs import WordDefs
import tqdm
import os


DEFS_FILE = '../data/collins-2019-def.txt'


def source_file_with_bar(filename):
    with tqdm.tqdm(total=os.path.getsize(filename)) as pbar:
        with open(filename, "r") as f:
            for line in f:
                pbar.update(len(line))
                yield line


def main():
    redis_db = get_redis()

    for line in source_file_with_bar(DEFS_FILE):
        word, definition = str(line).split('\t')

        wd = WordDefs(redis_db, word)
        wd.append_word_defs([definition])

    redis_db.save()


if __name__ == '__main__':
    main()