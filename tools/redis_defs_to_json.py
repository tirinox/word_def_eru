"""
Извлекает из Redis определения и сохраняет в JSON
"""

import json
from tqdm import tqdm
from util import *
from word_defs import WordDefs

if __name__ == '__main__':
    redis = get_redis()

    with open('../data/cross_used_words_1.txt', 'r') as f:
        words = f.readlines()

    words = list(map(str.strip, words))

    all_j = {}

    for word in tqdm(words):
        j = WordDefs(redis, word).load_defs()
        all_j[word] = j

    with open("../data/ext_defs.json", "w") as f:
        json.dump(all_j, f, ensure_ascii=False, indent=2)

