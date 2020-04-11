from wordlist import WordList as wl
from wordtable import WordTable as wt

wordlists = []
for i in range(3,11):
    wordlists.append(wl("words" + str(i)))

table = wt()
for i in wordlists:
    table.add_word(i.get_random())

table.print_table()
print()
table.fill_table()
table.print_table()
