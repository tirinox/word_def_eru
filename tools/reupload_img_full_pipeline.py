"""
Обновляет картинки из Redis загружая их на наш хостинг
"""

from tqdm import tqdm
from util import *
import os
from word_defs import WordDefs
# from tools.upload_redis2mysql import get_mysql_connect, distinct_cross_words
from tools.download_images import cross_used_words, download_image, IMG_SAVE_PATH
from tools.upload_def_images_to_erugame import upload_image, is_erugame_image_url


def run_pipeline(source, total=None):
    for wd in tqdm(source, total=total):
        img_url = wd.image_url
        if img_url:
            if is_erugame_image_url(img_url):
                continue

            local_image = download_image(img_url, wd.word, cached=False)

            if local_image.startswith('http'):
                new_remote_url = upload_image(local_image)
            else:
                new_remote_url = local_image

            if is_erugame_image_url(new_remote_url):
                wd.update_image_url(new_remote_url)
                wd.save_to_redis()
            else:
                print(f'Upload error: {new_remote_url} for wrd {wd.word}')


# def all_crossword_words(directly_from_mysql=True):
#     if directly_from_mysql:
#         mysql = get_mysql_connect()
#         words = distinct_cross_words(mysql)
#         return words
#     else:
#         return cross_used_words()


def word_defs_from_keys(keys, redis):
    for key in keys:
        wd = WordDefs.from_key(redis, key)
        if not wd:
            continue
        yield wd


def word_defs_from_list(redis, word_list):
    for word in word_list:
        wd = WordDefs(redis, word)
        wd.load_defs()
        yield wd


if __name__ == '__main__':
    redis = get_redis()

    os.makedirs(IMG_SAVE_PATH, exist_ok=True)

    all_word_keys = WordDefs.all_keys(redis)

    source = word_defs_from_keys(all_word_keys, redis)
    run_pipeline(source, total=len(all_word_keys))
