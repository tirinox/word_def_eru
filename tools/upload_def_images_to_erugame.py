"""
Загрузит картинки скачанные с левых сайтов для определений слов на наш хостинг!
DATA_IMG_DIR - адрес картинок в формате СЛОВО.ext
создает маппинг word2upurl.json {СЛОВО: новый URL}
"""

import requests
import os
import json
from tqdm import tqdm
import io
from PIL import Image, ImageFile

os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'


ImageFile.LOAD_TRUNCATED_IMAGES = True


DATA_IMG_DIR = '../data/img'
EXAMPLE_FILE = 'АВТОБУС.jpg'
UPLOAD_ENDPOINT = 'https://erugame.ru/upload.php?mode=crossword'
WORD_TO_UP_URL_FILE = '../data/word2upurl.json'

MAX_SIZE = (640, 480)
JPEG_QUALITY = 70


def is_erugame_image_url(image_url: str):
    return image_url and image_url.startswith('https://erugame.ru/')


def upload_image(path):
    # return path + '/debug!'  # debug

    img = Image.open(path)
    img.thumbnail(MAX_SIZE)

    if path.endswith('.png'):
        img_format = 'PNG'
    else:
        img_format = 'JPEG'

    b = io.BytesIO()
    img.save(b, img_format, quality=JPEG_QUALITY)
    b.seek(0)

    size = b.getbuffer().nbytes
    if size >= 500_000:
        print(f'warning: size = {size // 1024} KB')

    files = {
        'upfile': b
    }

    r = requests.post(UPLOAD_ENDPOINT, files=files)
    r = json.loads(r.text)
    return r['answers']['file']


def upload_example():
    r = upload_image(path=os.path.join(DATA_IMG_DIR, EXAMPLE_FILE))
    print(r)


def list_images(path):
    arr = os.listdir(path)

    def is_good(name):
        ext = name.split('.')[-1]
        return ext.lower() in ('jpg', 'jpeg', 'png')

    return {name.split('.')[-2]: os.path.join(path, name) for name in arr if is_good(name)}


def save_word_map(word2upurl):
    print('Saving...')
    with open(WORD_TO_UP_URL_FILE, 'w') as f:
        json.dump(word2upurl, f, ensure_ascii=False, indent=4)


def load_word_map():
    if os.path.exists(WORD_TO_UP_URL_FILE):
        with open(WORD_TO_UP_URL_FILE, 'r') as f:
            return json.load(f)
    else:
        return {}


def should_reload(value: str):
    return value is None or not value.startswith('https://')


if __name__ == '__main__':
    images = list_images(DATA_IMG_DIR)

    word2upurl = load_word_map()

    try:
        i = 0
        for word, path in tqdm(images.items()):
            if should_reload(word2upurl.get(word)):
                if word in word2upurl:
                    print(f'Reuploading {word} reason {word2upurl[word]}')
                word2upurl[word] = upload_image(path)

                if i >= 50:
                    save_word_map(word2upurl)
                    i = 0
                else:
                    i += 1

    except KeyboardInterrupt:
        save_word_map(word2upurl)
        raise

    save_word_map(word2upurl)
