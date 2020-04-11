import random

class WordList:
    def __init__(self, list):
        self.wordlist = []
        file = open(list, "r")
        words = file.readlines()
        for word in words:
            self.wordlist.append(word.rstrip())

    def get_random(self):
        return random.choice(self.wordlist)

    def is_word(self, word):
        for i in self.wordlist:
            if word == i:
                return True
        return False

    def dump_words(self):
        print(self.wordlist)


