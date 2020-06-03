from util import *


class WordDefs:
    KEY_PREFIX = 'word_def_'

    def __init__(self, r: Redis, word: str):
        self.r = r
        self.word = word.strip().upper()
        self._hash = word_hash(self.word)

    @staticmethod
    def all_keys(r: Redis):
        return r.keys(WordDefs.KEY_PREFIX + '*')

    def word_def_key(self):
        return self.KEY_PREFIX + self._hash

    def save_to_redis(self, defs):
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

    EMPTY_DEF = {
            'word': '?',
            'defs': []
        }

    @staticmethod
    def decode_db_value(v, enum_them=True):
        r = json.loads(v) if v is not None else WordDefs.EMPTY_DEF
        if enum_them:
            r['defs'] = [
                {
                    **d,
                    'id': i
                } for i, d in enumerate(r['defs'])
            ]
        return r

    def remove_def(self, ident):
        defs = self.load_defs()


    def load_defs(self):
        text = self.r.get(self.word_def_key())
        return self.decode_db_value(text)

    def append_word_defs(self, defs):
        """
        :param defs: list of str
        :return: WordDef updated
        """
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
            self.save_to_redis(current_defs)
        return updated

    def is_there_definition(self, count_empty=True):
        entry = self.r.get(self.word_def_key())
        if entry is None:
            return False
        if not count_empty and entry == "[]":
            return False
        return True
