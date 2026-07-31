class MemoryStore:

    def __init__(self):

        self.memory = {}

    def save(self, key, value):

        self.memory[key] = value

    def get(self, key):

        return self.memory.get(key)

    def all(self):

        return self.memory