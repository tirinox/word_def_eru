"""
Сей скрипт из Редиса качает все рейтинги поплуярности слов (0-100) и пишет в табличку CSV
"""
from tqdm import tqdm
import word_usage
from util import *
import csv
from collections import Counter, defaultdict

FILE_LIST_TXT = '../data/wordlist/final.txt'

OUTPUT_FILE = '../data/popularity.csv'

MIN_LENGTH = 2
MAX_LENGTH = 15

WITH_PERMUTATIONS = False
FILTER_ZERO_RATE = True


def read_words(file):
    with open(file, 'r') as f:
        return f.readlines()


def word_rate_get(words, redis):
    for word in words:
        word = word.strip()
        wu = word_usage.WordUsage(redis, word)
        count = wu.get_word_usage_count()
        rate = wu.get_word_usage_rate(count)
        yield word, int(rate)


def write_out_csv(out_file, word_rate_stream, names):
    with open(out_file, 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(names)
        for i, entries in enumerate(word_rate_stream):
            writer.writerow((i, *entries))


class PermutationScanner:
    def __init__(self, words) -> None:
        self.all_words = set(words)
        self.counters = {w: Counter(w) for w in tqdm(self.all_words)}

        word_groups = defaultdict(set)
        for w in self.all_words:
            word_groups[len(w)].add(w)

        self.word_groups = word_groups

    def find_all_subwords(self, word):
        word = word.upper()
        subwords = set()
        this_counter = Counter(word)
        this_len = len(word)
        for word_len, group in self.word_groups.items():
            if word_len <= this_len:
                for word in group:
                    counter = self.counters[word]
                    for k, v in counter.items():
                        if v > this_counter.get(k, 0):
                            break
                    else:
                        subwords.add(word)
        return subwords


def word_permutation_counts(all_words, items):
    p = PermutationScanner(all_words)
    for word, *rest in items:
        all_sub_words = p.find_all_subwords(word)
        yield (word, *rest, len(all_sub_words), *all_sub_words)


def main():
    # 1. read
    words = read_words(FILE_LIST_TXT)

    # 2. filter by length
    words = (w.strip() for w in words)
    words = (w for w in words if MIN_LENGTH <= len(w) <= MAX_LENGTH)

    # 3. sort
    words = sorted(words, key=lambda w: (-len(w), w))

    # 4. extract ratings
    redis = get_redis()
    rate_stream = word_rate_get(words, redis)

    if FILTER_ZERO_RATE:
        rate_stream = ((w, r) for w, r in rate_stream if r > 0)

    if WITH_PERMUTATIONS:
        rate_stream = word_permutation_counts(words, rate_stream)
        columns = ('ID', 'Word', 'Rating', 'NSubWords', 'Permutations')
    else:
        columns = ('ID', 'Word', 'Rating')


    # 5. make a progresss bar
    rate_stream = tqdm(rate_stream, unit='word', total=len(words))  # progress bar

    # 6. run the pipeline and save the results
    write_out_csv(OUTPUT_FILE, rate_stream, columns)


main()
