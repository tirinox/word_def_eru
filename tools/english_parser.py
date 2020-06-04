from util import *
from word_defs import WordDefs
import os
from functools import reduce


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
        word = r[0].upper()
        word = word.replace('-', '').replace('"', '').replace('\'', '')

        if 2 <= len(word) <= 15:
            if not any(str.isdigit(x) for x in word):
                if '\\' not in word and '/' not in word:
                    return word


def all_sources():
    for def_file in all_dic_lists():
        defs = filter_empty(load_lines(def_file))
        for word_def in defs:
            word = get_word_from_def(word_def)
            if word:
                yield word, word_def


def group_defs_for_word(words_and_defs):
    last_word = None
    new_defs = []

    for word, word_def in words_and_defs:
        if last_word != word:
            if new_defs:
                yield last_word, list(new_defs)
            new_defs = [word_def]
            last_word = word
        else:
            new_defs.append(word_def)
    if new_defs:
        yield last_word, list(new_defs)


def main():
    r = get_redis()

    n = 0
    for word, word_defs in group_defs_for_word(all_sources()):
        w = WordDefs(r, word)

        word_defs = [{'text': t} for t in word_defs]

        w.append_word_defs(word_defs)
        n += 1
        if n % 500 == 0:
            print(n, word)
    r.save()


def test():
    r = get_redis()
    w = WordDefs(r, 'ABSTRUDE')
    print(w.load_defs())


if __name__ == '__main__':
    test()
    main()
