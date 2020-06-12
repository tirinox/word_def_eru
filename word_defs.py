from util import *


class WordDefs:
    KEY_PREFIX = 'word_def_'
    MAX_DEF_LEN = 512
    MAX_DIC_NAME_LEN = 256
    MAX_URL_LEN = 1024

    def __init__(self, r: Redis, word: str):
        self.r = r
        self.word = word.strip().upper()
        self._hash = word_hash(self.word)
        self._defs = []

    @classmethod
    def has_image(cls, defs):
        for d in defs:
            img = d.get('imageURL', '')
            if img and isinstance(img, str) and len(img) >= 10:
                return True
        return False

    def delete(self):
        self._defs = []
        self.r.delete(self.word_def_key())

    @staticmethod
    def all_keys(r: Redis):
        return r.keys(WordDefs.KEY_PREFIX + '*')

    def word_def_key(self):
        return self.KEY_PREFIX + self._hash

    def save_to_redis(self):
        key = self.word_def_key()
        def_json = json.dumps({
            'word': self.word,
            'defs': self._defs
        }, ensure_ascii=False)
        self.r.set(key, def_json)

    def _find_definition(self, needle_text):
        for current_def in self._defs:
            if 'text' in current_def:
                current_def_text = current_def['text']
                if current_def_text == needle_text:
                    return True
        return False

    @staticmethod
    def decode_db_value(v):
        r = json.loads(v) if v is not None else {}
        return r

    def get_defs(self, enum_them=True):
        defs = list(self._defs)
        if enum_them:
            defs = [
                {
                    **d,
                    'id': i
                } for i, d in enumerate(defs)
            ]
        return defs

    def _check_ident(self, ident):
        self.load_defs()
        ident = int(ident)
        if ident < 0 or ident >= len(self._defs):
            raise Exception('ident out of range')
        return ident

    def remove_def(self, ident):
        ident = self._check_ident(ident)
        del self._defs[ident]
        self.save_to_redis()

    def move_def(self, ident, direction):
        ident = self._check_ident(ident)
        items = self._defs
        move_element_in_list(items, ident, direction)
        self.save_to_redis()

    def load_defs(self, forced=False):
        if forced or not self._defs:
            text = self.r.get(self.word_def_key())
            r = self.decode_db_value(text)
            self._defs = r.get('defs', [])
            self.word = r.get('word', self.word)
        return self._defs

    def _clean_def(self, new_definition):
        text = str(new_definition['text']).strip()
        image_url = str(new_definition.get('imageURL', ''))
        dic = str(new_definition.get('dic', 'internal'))

        assert len(dic) < self.MAX_DIC_NAME_LEN
        assert len(image_url) < self.MAX_URL_LEN
        assert isinstance(text, str) and len(text) >= 10

        new_def = {'text': text}
        if image_url:
            new_def['imageURL'] = image_url
        if dic:
            new_def['dic'] = dic
        return new_def

    def update_def(self, ident, new_def):
        ident = self._check_ident(ident)
        new_def = self._clean_def(new_def)
        self._defs[ident] = new_def
        self.save_to_redis()

    def append_word_defs(self, new_defs):
        """
        :param new_defs: list of [{'text': ...., 'imageURL': ???, 'dic': ???}]
        :return: WordDef updated
        """
        self.load_defs()

        not_image_yet = not self.has_image(self._defs)

        if not isinstance(new_defs, (list, tuple)):
            new_defs = [new_defs]

        prepend_list = []

        updated = False
        for new_definition in new_defs:
            new_definition = self._clean_def(new_definition)
            text = new_definition['text']

            if not_image_yet and self.has_image([new_definition]):
                prepend_list.append(new_definition)
                updated = True
                not_image_yet = False
            elif not self._find_definition(text):
                prepend_list.append(new_definition)
                updated = True

        if updated:
            self._defs = prepend_list + self._defs
            self.save_to_redis()
        return updated

    def is_there_definition(self, count_empty=True):
        entry = self.r.get(self.word_def_key())
        if entry is None:
            return False
        if not count_empty and entry == "[]":
            return False
        return True
