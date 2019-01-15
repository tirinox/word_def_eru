from util import *


class WordDefs:
    def __init__(self, r: Redis):
        self.r = r

    @staticmethod
    def word_def_key(word):
        return 'word_def_' + word_hash(word)

    def _save_to_redis(self, word, defs):
        key = self.word_def_key(word)
        def_json = json.dumps(defs, ensure_ascii=False)
        self.r.set(key, def_json)

    MAX_DEF_LEN = 320

    @staticmethod
    def _find_definition(current_defs, def_text):
        for current_def in current_defs:
            if 'text' in current_def:
                current_def_text = current_def['text']
                if current_def_text == def_text:
                    return True
        return False

    def get_word_def_dic_from_redis(self, word):
        text = self.r.get(self.word_def_key(word))
        return json.loads(text) if text is not None else []

    def append_word_defs(self, word, defs):
        current_defs = self.get_word_def_dic_from_redis(word)

        updated = False
        for new_definition in defs:
            if isinstance(new_definition, str) and len(new_definition) >= 3:
                new_definition = new_definition.strip()
                new_definition = new_definition[:self.MAX_DEF_LEN]

                if not self._find_definition(current_defs, new_definition):
                    current_defs.append({
                        'text': new_definition
                    })
                    updated = True

        if updated:
            self._save_to_redis(word, current_defs)
        return updated

    def is_there_definition(self, word, count_empty=True):
        entry = self.r.get(self.word_def_key(word))
        if entry is None:
            return False
        if not count_empty and entry == "[]":
            return False
        return True
