import random
from redis import Redis
from operator import itemgetter


class WordPermutations:
    VARIANT_BUCKETS = {
        '< 5': (0, 4),
        '5-10': (5, 10),
        '11-15': (11, 15),
        '16-20': (16, 20),
        '21-30': (21, 30),
        '31-40': (31, 40),
        '41-50': (41, 50),
        '51-75': (50, 75),
        '76-100': (76, 100),
        '> 100': (101, 100000)
    }

    LEN_VARIANTS = list(range(3, 10))

    def __init__(self, r: Redis, lang='RUS'):
        self.r = r  # type Redis
        self.lang = lang

    def key_for_len_and_variants(self, word_len: int, variant_bucket: str):
        variant_bucket = variant_bucket.replace(' ', '')
        return f'wperm_{self.lang}_{word_len}_{variant_bucket}'

    def all_keys(self):
        return [self.key_for_len_and_variants(wl, vc)
                for wl in self.LEN_VARIANTS
                for vc in self.VARIANT_BUCKETS.keys()]

    def drop_old(self):
        self.r.delete(*self.all_keys())

    def bucket_from_variant_count(self, vc):
        for name, (start, end) in self.VARIANT_BUCKETS.items():
            if start <= vc <= end:
                return name
        return list(self.VARIANT_BUCKETS.keys())[-1]

    def add_to_list(self, word, rating, variant_count):
        bucket = self.bucket_from_variant_count(variant_count)
        l = len(word)
        key = self.key_for_len_and_variants(l, bucket)
        value = f'{word},{rating},{variant_count}'
        self.r.lpush(key, value)

    def get_all_from_bucket(self, word_len: int, variant_bucket: str):
        strings = self.r.lrange(self.key_for_len_and_variants(word_len, variant_bucket), 0, -1)
        for string_v in strings:
            word, rating, variants = string_v.split(',')
            yield word, int(rating), int(variants)

    def get_count(self, word_len: int, variant_bucket: str):
        return self.r.llen(self.key_for_len_and_variants(word_len, variant_bucket))

    @staticmethod
    def subsample(items, batch_size=10):
        items = list(items)
        if not items:
            return []
        batch = random.sample(items, batch_size)
        batch.sort(key=itemgetter(1), reverse=True)  # sort by rating descending
        return [{
            'word': word,
            'rating': rating,
            'variants': variants
        } for word, rating, variants in batch]
