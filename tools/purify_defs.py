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


def clear_text(text: str):
    text = text.replace('… …', '…')
    return text


def is_good_text(text):
    if 'ї' in text or 'ð' in text or 'I суффикс' in text:
        return False
    if len(text) < 10:
        return False
    if 'В Википедии есть статьи о других людях с такой фамилией' in text:
        return False
    return True


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
    dic = d['dic']['name'] if 'dic' in d else ''
    if dic == '':
        return 'internal'
    return dic


def purify_defs(word, defs):
    if isinstance(defs, dict) and 'word' in defs:
        return defs  # all set

    defs = [{
        'text': clear_text(d['text']),
        'dic': fix_dic_name(d)
    } for d in defs if is_good_text(d['text'])]

    defs = [d for d in defs if is_good_dic(d['dic'])]

    return {
        'word': word,
        'defs': defs
    }


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

            for d in defs['defs']:
                print(f'{d["dic"]!r} : {d["text"]}\n')

            print(f'\n >>> {word} <<<< \n')

            input()
            print('\n' * 100)


def all_defs_purify(r: Redis, words: list):
    for word in tqdm(words):
        wd = WordDefs(r, word)
        defs = wd.load_defs()

        if len(defs):
            wd._defs = purify_defs(word, defs)
            wd.save_to_redis()


if __name__ == '__main__':
    assert False, "not working!"


    redis = get_redis()

    words = read_all_words_from_dictionary('../data/wordlist/final.txt')

    import random
    random.shuffle(words)

    # find_all_invalid_defs(redis)

    all_defs_purify(redis, words)

    # delete_empty_defs(redis)
