IN_DIRECTORY = 'data/out/articles'
OUT_JSON_COMPOSITION = 'data/out/all_word_defs.json'

import os
import codecs
import json

def get_file_list(path):
    return (file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file)))

if __name__ == '__main__':
    files = list(get_file_list(IN_DIRECTORY))

    all_infos = {}

    i = 1
    n = len(files)
    for file in files:
        with codecs.open(os.path.join(IN_DIRECTORY, file), 'r', encoding='utf-8') as f:
            raw_text = f.read()
            json_data = json.loads(raw_text)
            word = json_data['word']
            defs = json_data['defs']
            all_infos[word] = defs

            print("[{}/{}] {}".format(i, n, word))
        i += 1

    print("Writing the out file")
    with codecs.open(OUT_JSON_COMPOSITION, 'w', encoding='utf-8') as out_f:
        out_f.write(json.dumps(all_infos))
    print("done!")


