from util import *


class WordUsage:
    def __init__(self, r: Redis):
        self.r = r

    ESTIMATE_WORD_NUMBER = 150000
    KEY_TOTAL_WORD_USAGE = 'total_word_usage'

    @staticmethod
    def word_usage_key(word):
        return 'wus_' + word_hash(word)

    def increment_word_usage(self, word):
        self.r.incr(self.word_usage_key(word))
        self.r.incr(self.KEY_TOTAL_WORD_USAGE)

    def get_word_usage(self, word):
        this_word_usage = self.r.get(self.word_usage_key(word))
        this_word_usage = int_or_zero_if_none(this_word_usage)

        total_word_usage = self.r.get(self.KEY_TOTAL_WORD_USAGE)
        total_word_usage = int_or_zero_if_none(total_word_usage)
        if total_word_usage == 0:
            total_word_usage = 1

        rate = self.ESTIMATE_WORD_NUMBER * this_word_usage / total_word_usage * 100
        if rate < 0:
            rate = 0
        elif rate > 100:
            rate = 100

        return rate
