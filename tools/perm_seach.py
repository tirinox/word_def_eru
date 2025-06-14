import csv

from tqdm import tqdm

PERM_POP_FILE = '../data/permutations.csv'
LANG = 'RUS'

ONLY_LENS = [4]


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
                    if variants > 10:
                        goods.append({
                            'word': word,
                            'n_variants': variants,
                            'variants': sorted(permuts, key=len, reverse=True),
                            'rating': rating
                        })

    goods.sort(key=lambda w: (len(w['word']), w['rating']), reverse=True)
    for g in goods:
        w = g['word']
        l = len(w)
        sp = ', '.join(g['variants'])
        print(f'{w} ({l}) => {sp}')

main()
