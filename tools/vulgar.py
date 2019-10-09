from tools.import_collins_defs import DEFS_FILE, source_file_with_bar

if __name__ == '__main__':
    stop_defs = (
        '(offensive slang)',
        'fuck',
        '(vulgar)',
        '(offensive us slang)',
        '(offensive)',
        '(vulgar slang)'
    )

    n = 0
    with open('../data/vulgar_list.txt', 'w') as out_file:
        for line in source_file_with_bar(DEFS_FILE):
            word, definition = str(line).split('\t')
            word = str(word).lower().strip()
            definition = str(definition).lower().strip()
            if any(stop in definition or stop in word for stop in stop_defs):
                print(word, file=out_file)
                print(word, '>>=>>', definition)
                n += 1

    print(f'total bad words: {n}')

