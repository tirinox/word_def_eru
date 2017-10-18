WORD_LIST_TEXT_FILE = 'data/raw/final.txt'
OUTPUT_DIR = 'data/out/articles'

from bs4 import BeautifulSoup
import json
from fake_useragent import UserAgent
import codecs
import hashlib
import requests
import os
from pathlib import Path
import urllib.parse as urlencode


def load_word_html_data(word, session):
    word = urlencode.quote_plus(str(word))
    url = 'https://dic.academic.ru/searchall.php?SWord={}&from=xx&to=ru&did=&stype='.format(word)
    request = session.get(url)
    return request.text


def get_article_text(article):
    UNDESIRED_PREFIX = ' — '
    t = article.find('p').contents[3]
    if t.startswith(UNDESIRED_PREFIX):
        t = t[len(UNDESIRED_PREFIX):]
    t = t.strip()
    return t


def get_article_dic(article):
    t = article.find('p', {'class': 'src'}).find('a').text
    return t


def get_word_definition(article):
    return {
        'text': get_article_text(article),
        'dic': get_article_dic(article)
    }


def get_word_definitions(html_text):
    soup = BeautifulSoup(html_text, "lxml")

    found_articles = soup.find('ul', {
        'id': 'found_articles'
    }).find_all('li')

    definitions = [get_word_definition(a) for a in found_articles]

    return definitions


def create_new_session(user_agent_generator, proxy=None):
    s = requests.Session()
    s.headers.update({
        'User-Agent': user_agent_generator.random
    })
    if proxy is not None:
        s.proxies = {
            "http": proxy
        }
    return s


def read_all_words_from_dictionary(dictionary_filename):
    with codecs.open(dictionary_filename, 'r', encoding='utf-8') as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    return [x.strip() for x in content]


def word_def_filename(word):
    return os.path.join(OUTPUT_DIR, hashlib.sha1(word.encode('utf-8')).hexdigest() + '.json')


def is_there_definition(word):
    return Path(word_def_filename(word)).is_file()


def download_word_definition(word, session):
    html_text = load_word_html_data(word, session)
    defs = get_word_definitions(html_text)
    return defs


def write_word_definition(word, defs):
    n = len(defs)
    if n is 0:
        print('WARNING: no definitions for {} word!'.format(word))

    data = {
        'word': word,
        'defs': defs
    }
    json_data = json.dumps(data, indent=4, ensure_ascii=False)

    out_filename = word_def_filename(word)
    with codecs.open(out_filename, 'w', encoding='utf-8') as f:
        f.write(json_data)


def main():
    print("loading the word list")
    words = read_all_words_from_dictionary(WORD_LIST_TEXT_FILE)

    print("creating a session")
    ua = UserAgent()
    s = create_new_session(ua, proxy="http://107.172.4.200:1080")

    # d = download_word_definition(words[0], s)
    # write_word_definition(words[0], d)
    # print(d)

    all = len(words)
    i = 1
    for word in words:
        print("[{}/{}] processing word: {}".format(i, all, word))
        if not is_there_definition(word):
            word_defs = download_word_definition(word, session=s)
            write_word_definition(word, word_defs)
        i += 1


if __name__ == '__main__':
    main()
