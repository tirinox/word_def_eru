"""
Сей скрипт в Редис заливает списки слов с полулярностью и количеством вариантов
распределяет по корзинам
"""
from tqdm import tqdm
import word_permutation
from util import *
import csv


PERM_POP_FILE = '../data/permutations.csv'
LANG = 'RUS'


def get_permuts():
    redis = get_redis()
    perms = word_permutation.WordPermutations(redis, LANG)
    return perms


def main():
    permuts = get_permuts()
    permuts.drop_old()

    with open(PERM_POP_FILE, 'r') as ff:
        reader = csv.reader(ff)
        next(reader)
        for row in tqdm(reader):
            if len(row) >= 4:
                _, word, rating, variants, *_ = row
                rating = int(rating)
                variants = int(variants)
                permuts.add_to_list(word, rating, variants)

    test()


def test():
    permuts = get_permuts()

    batch = permuts.subsample(permuts.get_all_from_bucket(6, '31-40'), batch_size=105)

    print(batch)


main()
