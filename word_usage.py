from util import *
import math
from redis import Redis


class WordUsage:
    def __init__(self, r: Redis, word: str):
        self.r = r
        self.word = word
        self._hash = word_hash(word)

    KEY_MAX_WORD_USAGE = 'max_word_usage'
    UPPER_100_K = 0.6
    POW_COEFF = 0.2

    def word_usage_key(self):
        return 'wus_' + self._hash

    def word_max_score_key(self):
        return 'wms_' + self._hash

    def get_max_usage(self):
        return int_or_default(self.r.get(self.KEY_MAX_WORD_USAGE), 1)

    def increment_word_usage(self):
        key = self.word_usage_key()

        self.r.incr(key)

        cur_wu = int_or_default(self.r.get(key))
        max_wu = max(self.get_max_usage(), cur_wu)
        self.r.set(self.KEY_MAX_WORD_USAGE, max_wu)

    def update_max_score(self, profile_id, score):
        old_profile_id, old_score = self.get_best_profile_id_and_score()
        if old_score < score:
            self.r.set(self.word_max_score_key(), '{}:{}'.format(profile_id, score))

    def get_word_usage_count(self):
        this_word_usage = self.r.get(self.word_usage_key())
        this_word_usage = int_or_default(this_word_usage)
        return this_word_usage

    def get_word_usage_rate(self, this_word_usage):
        if this_word_usage == 0:
            return 0.0

        rate = this_word_usage / self.get_max_usage()
        if rate > self.UPPER_100_K:
            return 100.0
        else:
            rate = math.pow(rate / self.UPPER_100_K, self.POW_COEFF)

        return rate * 100.0

    def get_best_profile_id_and_score(self):
        key = self.word_max_score_key()
        s = self.r.get(key)
        return tuple(int(x) for x in s.split(':')) if s else (0, 0)
