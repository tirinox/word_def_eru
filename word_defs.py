from util import *
from redis.exceptions import WatchError


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
    def from_key(cls, redis, key):
        info = WordDefs.decode_db_value(redis.get(key))
        if not isinstance(info, dict) or 'word' not in info:
            return None
        wd = cls(redis, info['word'])
        wd._defs = info['defs']
        return wd

    @property
    def image_url(self):
        for d in self.load_defs():
            img_url = d.get('imageURL')
            if img_url:
                return img_url

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
        self.r.set(key, self._encode_db_value(self.word, self._defs))

    @staticmethod
    def _encode_db_value(word, defs):
        return json.dumps({
            'word': word,
            'defs': defs
        }, ensure_ascii=False)

    def _state_from_db_value(self, value):
        decoded = self.decode_db_value(value)
        if isinstance(decoded, dict):
            return decoded.get('word', self.word), decoded.get('defs', [])
        if isinstance(decoded, list):
            return self.word, decoded
        return self.word, []

    def _update_atomically(self, update):
        key = self.word_def_key()
        while True:
            try:
                with self.r.pipeline() as pipeline:
                    pipeline.watch(key)
                    word, defs = self._state_from_db_value(pipeline.get(key))
                    changed, result = update(defs)

                    if changed:
                        pipeline.multi()
                        pipeline.set(key, self._encode_db_value(word, defs))
                        pipeline.execute()
                    else:
                        pipeline.unwatch()

                    self.word = word
                    self._defs = defs
                    return result
            except WatchError:
                continue

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
        return self._check_ident_in_defs(ident, self._defs)

    @staticmethod
    def _check_ident_in_defs(ident, defs):
        ident = int(ident)
        if ident < 0 or ident >= len(defs):
            raise Exception('ident out of range')
        return ident

    def remove_def(self, ident):
        def remove(defs):
            checked_ident = self._check_ident_in_defs(ident, defs)
            del defs[checked_ident]
            return True, None

        return self._update_atomically(remove)

    def move_def(self, ident, direction):
        def move(defs):
            checked_ident = self._check_ident_in_defs(ident, defs)
            move_element_in_list(defs, checked_ident, direction)
            return True, None

        return self._update_atomically(move)

    def load_defs(self, forced=False):
        if forced or not self._defs:
            text = self.r.get(self.word_def_key())
            r = self.decode_db_value(text)

            if isinstance(r, dict):
                self._defs = r.get('defs', [])
                self.word = r.get('word', self.word)
            elif isinstance(r, list):
                self._defs = r

        return self._defs

    def _clean_def(self, new_definition):
        text = str(new_definition['text']).strip()
        image_url = str(new_definition.get('imageURL', ''))
        dic = str(new_definition.get('dic', 'internal'))

        if len(text) < 10 or len(text) > self.MAX_DEF_LEN:
            raise Exception('invalid definition text')
        if len(dic) >= self.MAX_DIC_NAME_LEN:
            raise Exception('invalid dictionary name')
        if len(image_url) >= self.MAX_URL_LEN:
            raise Exception('invalid image URL')

        new_def = {'text': text}
        if image_url:
            new_def['imageURL'] = image_url
        if dic:
            new_def['dic'] = dic
        return new_def

    def update_def(self, ident, new_def):
        new_def = self._clean_def(new_def)

        def update(defs):
            checked_ident = self._check_ident_in_defs(ident, defs)
            defs[checked_ident] = new_def
            return True, None

        return self._update_atomically(update)

    def append_word_defs(self, new_defs):
        """
        :param new_defs: list of [{'text': ...., 'imageURL': ???, 'dic': ???}]
        :return: WordDef updated
        """
        if not isinstance(new_defs, (list, tuple)):
            new_defs = [new_defs]
        new_defs = [self._clean_def(definition) for definition in new_defs]

        def append(defs):
            not_image_yet = not self.has_image(defs)
            prepend_list = []
            updated = False

            for new_definition in new_defs:
                text = new_definition['text']

                if not_image_yet and self.has_image([new_definition]):
                    prepend_list.append(new_definition)
                    updated = True
                    not_image_yet = False
                elif not any(d.get('text') == text for d in defs):
                    prepend_list.append(new_definition)
                    updated = True

            if updated:
                defs[:0] = prepend_list
            return updated, updated

        return self._update_atomically(append)

    def is_there_definition(self, count_empty=True):
        entry = self.r.get(self.word_def_key())
        if entry is None:
            return False
        if not count_empty and entry == "[]":
            return False
        return True

    def update_image_url(self, new_image_url):
        for d in self._defs:
            if 'imageURL' in d:
                if new_image_url:
                    d['imageURL'] = new_image_url
                else:
                    del d['imageURL']
                break
