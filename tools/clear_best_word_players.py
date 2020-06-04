from util import get_redis
from word_usage import *
from tqdm import tqdm


if __name__ == '__main__':
    wu = WordUsage(get_redis(), '')

    all_keys = wu.all_hashes_for_profiles()

    for key in tqdm(all_keys):
        wu.r.delete(key)

    # k = wu.r.get(keys[0])
    # print(k)