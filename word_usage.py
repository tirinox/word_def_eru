from util import *
import math


class WordUsage:
    def __init__(self, r: Redis):
        self.r = r

    KEY_MAX_WORD_USAGE = 'max_word_usage'

    @staticmethod
    def word_usage_key(word):
        return 'wus_' + word_hash(word)

    def get_max_usage(self):
        return int_or_default(self.r.get(self.KEY_MAX_WORD_USAGE), 1)

    def increment_word_usage(self, word):
        key = self.word_usage_key(word)

        self.r.incr(key)

        cur_wu = int_or_default(self.r.get(key))
        max_wu = max(self.get_max_usage(), cur_wu)
        self.r.set(self.KEY_MAX_WORD_USAGE, max_wu)

    def get_word_usage_count(self, word):
        this_word_usage = self.r.get(self.word_usage_key(word))
        this_word_usage = int_or_default(this_word_usage)
        return this_word_usage

    def get_word_usage_rate(self, word):
        this_word_usage = self.r.get(self.word_usage_key(word))
        this_word_usage = int_or_default(this_word_usage)

        rate = this_word_usage / self.get_max_usage()
        if rate < 0.0:
            rate = 0.0
        elif rate > 1.0:
            rate = 1.0

        return rate * 100.0
