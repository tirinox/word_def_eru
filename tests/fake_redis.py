import fnmatch


class FakeRedis:
    """Small decode-responses Redis substitute for deterministic unit tests."""

    def __init__(self):
        self._values = {}
        self._lists = {}

    def get(self, key):
        return self._values.get(key)

    def set(self, key, value):
        self._values[key] = str(value)
        return True

    def delete(self, *keys):
        deleted = 0
        for key in keys:
            if key in self._values:
                del self._values[key]
                deleted += 1
            if key in self._lists:
                del self._lists[key]
                deleted += 1
        return deleted

    def incr(self, key):
        value = int(self._values.get(key, 0)) + 1
        self._values[key] = str(value)
        return value

    def keys(self, pattern="*"):
        keys = set(self._values) | set(self._lists)
        return sorted(key for key in keys if fnmatch.fnmatch(key, pattern))

    def scan_iter(self, pattern="*"):
        yield from self.keys(pattern)

    def lpush(self, key, *values):
        target = self._lists.setdefault(key, [])
        for value in values:
            target.insert(0, str(value))
        return len(target)

    def lrange(self, key, start, end):
        values = self._lists.get(key, [])
        stop = len(values) if end == -1 else end + 1
        return values[start:stop]

    def llen(self, key):
        return len(self._lists.get(key, []))

    def save(self):
        return True

    def pipeline(self):
        return FakePipeline(self)


class FakePipeline:
    def __init__(self, redis):
        self._redis = redis
        self._commands = []
        self._in_transaction = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.reset()

    def watch(self, *keys):
        return True

    def unwatch(self):
        return True

    def get(self, key):
        return self._redis.get(key)

    def multi(self):
        self._in_transaction = True

    def set(self, key, value):
        if self._in_transaction:
            self._commands.append((self._redis.set, (key, value)))
            return self
        return self._redis.set(key, value)

    def execute(self):
        results = [command(*args) for command, args in self._commands]
        self.reset()
        return results

    def reset(self):
        self._commands = []
        self._in_transaction = False
