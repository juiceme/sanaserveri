import requests
import json
import sys
import itertools
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from wordtable import WordTable as wt

url = "https://localhost:8088/startsession"
res = requests.get(url, verify=False)
if res.status_code != 200:
    sys.exit("Cannot connect to the server")
resp = json.loads(res._content.decode('utf-8'))
if resp["status"] != "OK":
    sys.exit("Server does not give session key")
sessionkey = resp["key"]

url = "https://localhost:8088/getwords"
res = requests.get(url, verify=False)
if res.status_code != 200:
    sys.exit("Cannot connect to the server")
resp = json.loads(res._content.decode('utf-8'))
if resp["status"] != "OK":
    sys.exit("Server does not give session key")
wordtable = resp["table"]

words = []

def solve(cell, depth, word):
    if depth == 0:
        words.append(word)
        return
    else:
        word.append(cell)
        solve([cell[0], cell[1]-1], depth-1, word.copy())
        solve([cell[0], cell[1]+1], depth-1, word.copy())
        solve([cell[0]-1, cell[1]], depth-1, word.copy())
        solve([cell[0]+1, cell[1]], depth-1, word.copy())

table = wt()

for i in range(10):
    for j in range(10):
        word = []
        solve([i,j], 3, word)
        words.sort()
        words = list(words for words,_ in itertools.groupby(words))
        for k in words:
            if table.check_validity(k):
                url = "https://localhost:8088/checkword"
                data = {"word": str(k), "key": sessionkey}
                res = requests.put(url, data=json.dumps(data), verify=False)
