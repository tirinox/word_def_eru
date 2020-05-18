import operator

from tqdm import tqdm
import csv


PERM_POP_FILE = '../data/permutations.csv'
LANG = 'RUS'

ONLY_LENS = [7, 8]


def main():
    goods = []
    with open(PERM_POP_FILE, 'r') as ff:
        reader = csv.reader(ff)
        next(reader)
        for row in tqdm(reader):
            if len(row) >= 4:
                _, word, rating, variants, *permuts = row
                word = word.strip()
                wlen = len(word)
                if wlen in ONLY_LENS:
                    rating = int(rating)
                    variants = int(variants)
                    has_self_perm = any(len(p) == wlen for p in permuts if p != word)
                    if has_self_perm:
                        self_perms = [p for p in permuts if len(p) == wlen and p != word]
                        # print(f"{word} ({wlen}) => {self_perms}")
                        goods.append({
                            'word': word,
                            'self_perms': self_perms,
                            'rating': rating,
                            'variants': variants
                        })

    goods.sort(key=lambda w: (len(w['word']), w['rating']), reverse=True)
    for g in goods:
        w = g['word']
        l = len(w)
        sp = ', '.join(g['self_perms'])
        print(f'{w} ({l}) => {sp}')

main()
