"""
Скачивает картинки слов из кроссворд
"""

import json
import os
from tqdm import tqdm
from util import *
from word_defs import WordDefs
import requests
import shutil
from fake_useragent import UserAgent
ua = UserAgent()

SAVE_PATH = '../data/img/'


def get_image_url(wd: WordDefs):
    defs = wd.load_defs()
    for d in defs:
        img_url = d.get('imageURL')
        if img_url:
            return img_url


def get_image_path(img_url, name):
    ext = os.path.splitext(img_url)[1]
    ext = ext.lower()
    path = os.path.join(SAVE_PATH, name + ext)
    return path


def download_image(img_url, name):
    headers = {
        'User-Agent': ua.random,
    }

    path = get_image_path(img_url, name)
    if os.path.exists(path):
        return

    r = requests.get(img_url, stream=True, allow_redirects=True, verify=False, headers=headers)
    if r.status_code == 200:
        with open(path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    else:
        print(f'warning: file {img_url} ({word}) returned code {r.status_code}')


if __name__ == '__main__':
    redis = get_redis()

    with open('../data/cross_used_words_1.txt', 'r') as f:
        words = f.readlines()
    words = list(map(str.strip, words))

    all_images = {}

    for word in tqdm(words):
        wd = WordDefs(redis, word)
        img = get_image_url(wd)
        all_images[word] = img
        if img:
            download_image(img, word)
