from util import *
from word_defs import WordDefs
import os
from functools import reduce
import time


ENGLISH_ROOT = '../data/eng/'
WORD_LISTS_PATH = os.path.join(ENGLISH_ROOT, 'word_list')
DICTS_LISTS_PATH = os.path.join(ENGLISH_ROOT, 'dict')


def compose2(f, g):
    return lambda *a, **kw: f(g(*a, **kw))


def compose(*fs):
    return reduce(compose2, fs)


def flatten(l):
    return (x for sub in l for x in sub)


def alphabet():
    yield from map(chr, range(ord('A'), ord('Z') + 1))


def all_word_lists():
    yield from map(lambda letter: os.path.join(WORD_LISTS_PATH, f'{letter}word.csv'), alphabet())


def all_dic_lists():
    yield from map(lambda letter: os.path.join(DICTS_LISTS_PATH, f'{letter}.csv'), alphabet())


def load_lines(file_name):
    with open(file_name, 'r', encoding='utf-8', errors='ignore') as f:
        return f.readlines()


def transform_lines(lines):
    yield from map(compose(str.strip, str.upper), lines)


def filter_empty(lines):
    yield from filter(lambda x: x, map(lambda x: x.strip().strip('"'), lines))


def get_word_from_def(d: str):
    r = d.strip('"').split(' (')
    if r:
        word = r[0].upper().replace('-', '').replace('"', '').replace('\'', '')
        l = len(word)
        if l >= 2 and l <= 15:
            if not any(str.isdigit(x) for x in word):
                if '\\' not in word and '/' not in word:
                    return word


def all_sources():
    n = 0
    s = set()
    for def_file in all_dic_lists():
        defs = filter_empty(load_lines(def_file))

        print('-' * 100)

        for word_def in defs:
            word = get_word_from_def(word_def)
            if not word:
                print(word_def)
            else:
                print('->', word.upper())
                s.add(word)
    print(len(s))


def main():
    all_sources()


    # r = get_redis()
    # wd = WordDefs(r, 'ПИВО')
    # print(wd.load_defs())


if __name__ == '__main__':
    main()