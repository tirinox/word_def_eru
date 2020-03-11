import os
from tqdm import tqdm
import word_usage
from util import *
import csv

FILE_LIST_TXT = '../data/wordlist/final.txt'


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


def write_out_csv(out_file, word_rate_stream):
    with open(out_file, 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for word, rate in word_rate_stream:
            writer.writerow((word, rate))


def main():
    words = read_words(FILE_LIST_TXT)
    redis = get_redis()

    rate_stream = word_rate_get(words, redis)

    rate_stream = tqdm(rate_stream, unit='word', total=len(words))  # progress bar

    write_out_csv('../data/popularity.csv', rate_stream)


main()
