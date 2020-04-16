import random
import itertools

class WordTable:
    def __init__(self):
        self.size = 10
        self.table = self.create_table()

    def create_table(self):
        table = []
        for i in range(self.size):
            row = []
            for j in range(self.size):
                row.append(".")
            table.append(row)
        return table

    def duplicate_table(self):
        table = self.create_table()
        for i in range(self.size):
            for j in range(self.size):
                table[i][j] = self.table[i][j]
        return table

    def set_table(self, table):
        for i in range(self.size):
            for j in range(self.size):
                self.table[i][j] = table[i][j]

    def add_word(self, word):
        original_table = self.duplicate_table()
        word = word.upper()
        while True:
            x0 = random.randrange(self.size)
            y0 = random.randrange(self.size)
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
                if y>-1 and y<self.size and x>-1 and x<self.size:
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
        for i in range(self.size):
            for j in range(self.size):
                if self.table[i][j] == ".":
                    self.table[i][j] = random.choice(chars)

    def get_raw_table(self):
        return self.table

    def get_word(self, vector):
        word = ""
        for i in vector:
            word = word + self.table[i[0]][i[1]]
        return word

    def check_validity(self, vector):
        v1 = vector.copy()
        v1.sort()
        v1 = list(v1 for v1,_ in itertools.groupby(v1))
        if len(vector) != len(v1):
            print("F1")
            return False
        for i in vector:
            if i[0] < 0 or i[0] > self.size-1 or i[1] < 0 or i[1] > self.size-1:
                print("F2")
                return False
        x0 = self.size
        y0 = self.size
        for i in vector:
            if x0 != self.size:
                xdiff = abs(i[0] - x0)
                ydiff = abs(i[1] - y0)
                if xdiff + ydiff != 1:
                    print("F3")
                    return False
            x0 = i[0]
            y0 = i[1]
        return True

    def print_table(self):
        output_table = self.duplicate_table()
        rounds = self.size-1
        for i in range(int(self.size/2)):
            for j in range(i, rounds-i):
                swap = output_table[i][j]
                output_table[i][j] = output_table[j][rounds-i]
                output_table[j][rounds-i] = output_table[rounds-i][rounds-j]
                output_table[rounds-i][rounds-j] = output_table[rounds-j][i]
                output_table[rounds-j][i] = swap
        for i in range(self.size):
            for j in range(self.size):
                print(output_table[i][j], end=" ")
            print()
