"""
1. Удаляет из определений ненужные href!
2. Добавляет в JSON слово

Раньше было [
    {'text': 'См …', 'href': '....', 'dic': {'name': 'Словарь синонимов', 'href': '....'}}
]

Должно стать {
 word: "слово", defs: [
    'id': 0,
    'text': '.....',
    'dic': '...dic name...'
 ]
}

"""

import json
from util import *
from tqdm import tqdm
from word_defs import WordDefs
from collections import Counter
from fuzzywuzzy.process import dedupe

import unicodedata


def clear_text(text: str):
    text = text.replace('… …', '…')
    text = normalize_text(text)
    return text


def is_good_text(text):
    if 'ї' in text or 'ð' in text or 'I суффикс' in text:
        return False
    if len(text) < 10:
        return False
    if 'В Википедии есть статьи о других людях с такой фамилией' in text:
        return False
    return True


DEDUPE_THRESHOLD = 100

BAD_DICTS = {
    'Орфографічний словник української мови',
    'Slang lexicon',
    'Словарь ударений русского языка',
    'Lithuanian dictionary (lietuvių žodynas)',
    'Формы слов',
    'Морфемно-орфографический словарь',
    'Chemijos terminų aiškinamasis žodynas',
    'Український тлумачний словник',
    'Слитно. Раздельно. Через дефис.',
    'Словарь трудностей произношения и ударения в современном русском языке',
    'Fizikos terminų žodynas ',
    'Краткий словарь анаграмм ',
    'Татар теленең аңлатмалы сүзлеге',
    'Macedonian dictionary',
    'Русское словесное ударение',
    'Žuvų pavadinimų žodynas',
    'Penkiakalbis aiškinamasis metrologijos terminų žodynas',
    'Ekologijos terminų aiškinamasis žodynas',
    'Русские фамилии',
    'Каталог отелей',
    'Sporto terminų žodynas',
    'Словарь антонимов',
    'Словарь синонимов',
    'Automatikos terminų žodynas',
    'Radioelektronikos terminų žodynas ',
    'Paukščių pavadinimų žodynas',
    'Исторический словарь галлицизмов русского языка',
    'Словарь древнерусского языка (XI-XIV вв.)',
    'Фарҳанги тафсирии забони тоҷикӣ ',
    'Толковый украинский словарь',
    'Қазақ тілінің түсіндірме сөздігі ',
    'Словарь-справочник "Слово о полку Игореве"',
    'Қазақ дәстүрлі мәдениетінің энциклопедиялық сөздігі',
    'Фонетический словарь Тайского языка',
    'Адыгабзэм изэхэф гущыIалъ',
    'Словарь церковнославянского языка',
    'Русский орфографический словарь',
    'Орфографический словарь русского языка',
    'Словарь многих выражений',
    'Λεξικό Ελληνικά-ρωσική νέα (Греческо-русский новый словарь)',
    'Словарь криминального и полукриминального мира',
    'Фитопатологический словарь-справочник',
    'Смешной cловарь дайвера',
    'Орфоепічний словник української мови',
    'Deutsch Wikipedia',
    'Wikipédia en Français',
    'Гірничий енциклопедичний словник',
    'Зведений словник застарілих та маловживаних слів',
    'Словник синонімів української мови',
    'Правописание трудных наречий ',
    'Тёмная башня Стивена Кинга. Толковый словарь к книге.',
    'Қазақ тілінің аймақтық сөздігі',
    'Новый объяснительный словарь синонимов русского языка',
    'Нанайско-русский словарь',
    'Словарь сокращений и аббревиатур',
    'Словарь личных имен',
    'Энциклопедия кино',
    'Cонник Фрейда',
    'Словарь символов',
    'Сонник Мельникова ',
    'Словник лемківскої говірки',
    'Этимологический словарь русского языка Макса Фасмера',
    'Старабеларускі лексікон',
    'Словарь употребления буквы Ё',
}


def is_good_dic(d):
    if 'Топоним' in d or 'топоним' in d or 'i' in d or 'і' in d:
        return False
    return d not in BAD_DICTS


def fix_dic_name(d):
    if 'dic' not in d or not d['dic']:
        dic = 'internal'
    else:
        dic = d['dic']
        if isinstance(dic, dict):
            dic = dic['name']
    return dic


def dedupe_defs(defs):
    only_texts = [d['text'] for d in defs]

    if DEDUPE_THRESHOLD == 100:
        deduped_texts = set(only_texts)
    else:
        try:
            deduped_texts = set(dedupe(only_texts, threshold=DEDUPE_THRESHOLD))
        except IndexError:
            print('failed to use fuzzywuzzy to dedupe defs; using strict comparison')
            n = len(only_texts)
            deduped_texts = set(only_texts)
            print(f'{n} -> {len(deduped_texts)}')

    out_defs = {}
    for d in defs:
        if d['text'] in deduped_texts and 'imageURL' in d and d['imageURL']:
            out_defs[d['text']] = d

    for d in defs:
        if d['text'] in deduped_texts and d['text'] not in out_defs:
            out_defs[d['text']] = d

    return list(out_defs.values())


def has_image(defs):
    return any(1 for d in defs if 'imageURL' in d and len(d['imageURL']) >= 10)


def normalize_text(input_text):
    return unicodedata.normalize('NFKD', input_text)


def purify_defs(word, defs):
    while isinstance(defs, dict):
        defs = defs['defs']

    defs = [{
        'text': clear_text(d['text']),
        'dic': fix_dic_name(d)
    } for d in defs if is_good_text(d['text'])]

    defs = [d for d in defs if is_good_dic(d['dic'])]

    n = len(defs)
    had_image = has_image(defs)

    defs = dedupe_defs(defs)

    if n != len(defs):
        print(f'deduped: {word} {n} -> {len(defs)}')

    if had_image != has_image(defs):
        sep()
        print('ERROR: image removed:')
        print_defs(defs)
        sep()
        exit(-1)

    return defs


def is_def_invalid(v):
    if not isinstance(v, dict) or 'word' not in v or 'defs' not in v or not isinstance(v['defs'], list):
        return True

    for d in v['defs']:
        if 'dic' in d and not isinstance(d['dic'], str):
            return True
        if 'text' not in d or not isinstance(d['text'], str) or len(d['text']) < 10:
            return True

    return False


def delete_empty_defs(r: Redis):
    print('Delete empty defs. Loading keys...')
    keys = WordDefs.all_keys(r)

    n = 0
    print('Removing bad keys...')
    for key in tqdm(keys):
        j = WordDefs.decode_db_value(r.get(key))
        if not j:
            r.delete(key)
            n += 1

    print(f'Done! {n} keys were removed.')


def find_all_invalid_defs(r: Redis):
    print('Find all invalid defs.')

    print('Getting all the keys...')
    keys = WordDefs.all_keys(r)

    print('Processing...')
    badkeys = {}
    for key in tqdm(keys):
        j = WordDefs.decode_db_value(r.get(key))
        if is_def_invalid(j):
            badkeys[key] = j
            if len(badkeys) % 100 == 0:
                print(f'Bad keys: {len(badkeys)}')

            if j:
                print(j)

            r.delete(key)

    print(f'Bad keys: {len(badkeys)}')

    with open('../data/orphan_defs_1.txt', 'w') as f:
        json.dump(badkeys, f, ensure_ascii=False, indent=4)

    return badkeys


def interactive_dic_quality_env(redis: Redis, words: list, max_len=5):
    for word in tqdm(words):
        wd = WordDefs(redis, word)
        defs = wd.load_defs()

        if defs:
            if len(word) > max_len:
                continue

            defs = purify_defs(word, defs)

            for d in defs:
                print(f'{d["dic"]!r} : {d["text"]}\n')

            print(f'\n >>> {word} <<<< \n')

            input()
            print('\n' * 100)


def all_defs_purify(r: Redis, words: list):
    print('all_defs_purify')

    n = 0
    for word in tqdm(words):
        wd = WordDefs(r, word)
        entry = WordDefs.decode_db_value(r.get(wd.word_def_key()))

        if entry:
            wd._defs = purify_defs(word, entry)
            wd.save_to_redis()

            n += 1

    print(f'all_defs_purify => {n} purified')


def main(redis: Redis):
    print('loading words...')
    words = read_all_words_from_dictionary('../data/wordlist/final.txt')

    import random
    random.shuffle(words)

    sep()

    # delete_empty_defs(redis)

    sep()

    all_defs_purify(redis, words)

    sep()

    print('saving redis db...')
    redis.save()
    print('done')


def print_defs(defs):
    print(*defs, sep='\n----\n')


def test_dedupe(redis):
    wd = WordDefs(redis, 'скат')
    wd.load_defs()

    wd._defs[1]['imageURL'] = 'image-url-set'

    defs = wd.get_defs()

    print_defs(defs)
    sep()

    clean = dedupe_defs(wd.get_defs())
    print_defs(clean)


if __name__ == '__main__':
    redis = get_redis()

    main(redis)
