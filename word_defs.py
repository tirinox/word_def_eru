from util import *


class WordDefs:
    def __init__(self, r: Redis, word: str):
        self.r = r
        self.word = word
        self._hash = word_hash(word)

    def word_def_key(self):
        return 'word_def_' + self._hash

    def _save_to_redis(self, defs):
        key = self.word_def_key()
        def_json = json.dumps(defs, ensure_ascii=False)
        self.r.set(key, def_json)

    MAX_DEF_LEN = 512

    @staticmethod
    def _find_definition(current_defs, def_text):
        for current_def in current_defs:
            if 'text' in current_def:
                current_def_text = current_def['text']
                if current_def_text == def_text:
                    return True
        return False

    def load_defs(self):
        text = self.r.get(self.word_def_key())
        return json.loads(text) if text is not None else []

    def append_word_defs(self, defs):
        current_defs = self.load_defs()

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
            self._save_to_redis(current_defs)
        return updated

    def is_there_definition(self, count_empty=True):
        entry = self.r.get(self.word_def_key())
        if entry is None:
            return False
        if not count_empty and entry == "[]":
            return False
        return True
