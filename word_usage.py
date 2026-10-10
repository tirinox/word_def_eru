from util import *
import math
import time
from redis import Redis
from redis.exceptions import WatchError


class WordUsage:
    def __init__(self, r: Redis, word: str):
        self.r = r  # type Redis
        self.word = word
        self._hash = word_hash(word)

    KEY_MAX_WORD_USAGE = 'max_word_usage'
    UPPER_100_K = 0.6
    POW_COEFF = 0.2

    def word_usage_key(self):
        return 'wus_' + self._hash

    def get_max_usage(self):
        return int_or_default(self.r.get(self.KEY_MAX_WORD_USAGE), 1)

    def increment_word_usage(self):
        key = self.word_usage_key()
        cur_wu = self.r.incr(key)

        while True:
            try:
                with self.r.pipeline() as pipeline:
                    pipeline.watch(self.KEY_MAX_WORD_USAGE)
                    stored_max = pipeline.get(self.KEY_MAX_WORD_USAGE)
                    max_wu = int_or_default(stored_max, 1)
                    if stored_max is not None and cur_wu <= max_wu:
                        pipeline.unwatch()
                        return

                    pipeline.multi()
                    pipeline.set(self.KEY_MAX_WORD_USAGE, max(max_wu, cur_wu))
                    pipeline.execute()
                    return
            except WatchError:
                continue

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

    # ------------------------------------

    def word_max_score_key(self):
        return 'wms_' + self._hash

    def word_max_score_time_key(self):
        return 'wmt_' + self._hash

    def all_hashes_for_profiles(self):
        return self.r.keys('wms_*')

    def update_max_score(self, profile_id, score):
        """Store the score if it beats the current record; return True when it did."""
        key = self.word_max_score_key()
        while True:
            try:
                with self.r.pipeline() as pipeline:
                    pipeline.watch(key)
                    current = pipeline.get(key)
                    old_score = int(current.split(':')[1]) if current else 0
                    if old_score >= score:
                        pipeline.unwatch()
                        return False

                    pipeline.multi()
                    pipeline.set(key, '{}:{}'.format(profile_id, score))
                    pipeline.set(self.word_max_score_time_key(), int(time.time()))
                    pipeline.execute()
                    return True
            except WatchError:
                continue

    def get_best_profile_id_and_score(self):
        key = self.word_max_score_key()
        s = self.r.get(key)
        return tuple(int(x) for x in s.split(':')) if s else (0, 0)

    def get_best_updated_at(self):
        """Unix time the record was set; None for records stored before it was tracked."""
        if not self.r.get(self.word_max_score_key()):
            return None
        t = self.r.get(self.word_max_score_time_key())
        return int(t) if t else None

    def to_json(self):
        profile_id, score = self.get_best_profile_id_and_score()
        count = self.get_word_usage_count()
        return {
            'word': self.word,
            'usage': count,
            'rate': self.get_word_usage_rate(count),
            'best': {
                'profile_id': profile_id,
                'score': score,
                'updated_at': self.get_best_updated_at()
            }
        }
