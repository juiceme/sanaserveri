import requests
import json
import sys
import itertools
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from wordtable import WordTable as wt
from wordlist import WordList as wl

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

vectors = []

def solve(cell, depth, vector):
    if depth == 0:
        vectors.append(vector)
        return
    else:
        vector.append(cell)
        solve([cell[0], cell[1]-1], depth-1, vector.copy())
        solve([cell[0], cell[1]+1], depth-1, vector.copy())
        solve([cell[0]-1, cell[1]], depth-1, vector.copy())
        solve([cell[0]+1, cell[1]], depth-1, vector.copy())

table = wt()
table.set_table(wordtable)

wordlist = wl("words3")
used_vectors = []

for i in range(10):
    for j in range(10):
        solve([i,j], 3, [])
        vectors.sort()
        vectors = list(vectors for vectors,_ in itertools.groupby(vectors))
        for k in vectors:
            if table.check_validity(k):
                word = table.get_word(k)
                if wordlist.is_word(word):
                    if k not in used_vectors:
                        url = "https://localhost:8088/checkword"
                        data = {"word": str(k), "key": sessionkey}
                        res = requests.put(url, data=json.dumps(data), verify=False)
                        if res.status_code != 200:
                            sys.exit("Cannot connect to the server")
                        resp = json.loads(res._content.decode('utf-8'))
                        if resp["status"] == "OK":
                            used_vectors.append(k)
