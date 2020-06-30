"""
Скачивает картинки слов из кроссвордов с внешних сайтов
из списка слов (см. cross_used_words)
т.е. ищет в redis определения слов, достает оттуда картинку и заливает их в SAVE_PATH
имя в формате СЛОВО.ext
"""

import json
import os
from tqdm import tqdm
from util import *
from word_defs import WordDefs
import requests
import shutil
from fake_useragent import UserAgent
from tools.redis_defs_to_json import cross_used_words

ua = UserAgent()

IMG_SAVE_PATH = '../data/img/'


def get_image_path(img_url, name):
    ext = os.path.splitext(img_url)[1]
    ext = ext.lower()
    path = os.path.join(IMG_SAVE_PATH, name + ext)
    return path


def download_image(img_url, name, cached=True):
    headers = {
        'User-Agent': ua.random,
    }

    path = get_image_path(img_url, name)
    if cached and os.path.exists(path):
        return path

    r = requests.get(img_url, stream=True, allow_redirects=True, verify=False, headers=headers)
    if r.status_code == 200:
        with open(path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    else:
        print(f'warning: file {img_url} ({name}) returned code {r.status_code}')

    return path


if __name__ == '__main__':
    redis = get_redis()
    words = cross_used_words()

    all_images = {}

    for word in tqdm(words):
        wd = WordDefs(redis, word)
        img = wd.image_url
        all_images[word] = img
        if img:
            download_image(img, word)
