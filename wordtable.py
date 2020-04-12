import random

class WordTable:
    def __init__(self):
        self.table = self.create_table()

    def create_table(self):
        table = []
        for i in range(10):
            row = []
            for j in range(10):
                row.append(".")
            table.append(row)
        return table

    def duplicate_table(self):
        table = self.create_table()
        for i in range(10):
            for j in range(10):
                table[i][j] = self.table[i][j]
        return table

    def set_table(self, table):
        for i in range(10):
            for j in range(10):
                self.table[i][j] = table[i][j]

    def add_word(self, word):
        original_table = self.duplicate_table()
        word = word.upper()
        while True:
            x0 = random.randrange(10)
            y0 = random.randrange(10)
            if self.table[x0][y0] == ".":
                self.table[x0][y0] = word[0]
                break
        direction0 = random.randrange(4)
        for i in range(len(word)-1):
            count = 0
            while True:
                count = count+1
                direction = random.randrange(20)
                if direction > 3:
                    direction = direction0
                if direction == 0:
                    x = x0-1
                    y = y0
                    direction0 = 0
                if direction == 1:
                    x = x0+1
                    y = y0
                    direction0 = 1
                if direction == 2:
                    x = x0
                    y = y0-1
                    direction0 = 2
                if direction == 3:
                    x = x0
                    y = y0+1
                    direction0 = 3
                if y>0 and y<10 and x>0 and x<10:
                    if self.table[x][y] == ".":
                        self.table[x][y] = word[i+1]
                        x0 = x
                        y0 = y
                        break
                if count > 20:
                    self.set_table(original_table)
                    return False
        return True
        
    def fill_table(self):
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for i in range(10):
            for j in range(10):
                if self.table[i][j] == ".":
                    self.table[i][j] = random.choice(chars)

    def print_table(self):
        for i in range(10):
            for j in range(10):
                print(self.table[i][j], end=" ")
            print()
