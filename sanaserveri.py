from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
import ssl
import json
import hashlib
import time
import random

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

sessions = []

def create_session():
    key = hashlib.sha1(str(time.time()+random.randrange(1000)).encode('utf-8')).hexdigest()
    sessions.append({"key": key, "score": 0, "found_words": [], "used_vectors": []})
    return { "key": key, "status": "OK" }

def get_session(key):
    session = ""
    for i in sessions:
        if i["key"] == key:
            session = i
            break
    return session

def handle_rest_get(path):
    if path == "/getwords":
        ret = { "table": table.get_raw_table(),
                "status": "OK" }
        return json.dumps(ret).encode('ascii')
    if path == "/startsession":
        return json.dumps(create_session()).encode('ascii')
    return json.dumps({"status": "FAIL", "error": "Invalid path"}).encode('ascii')

def handle_rest_put(path, body):
    data = json.loads(body)
    if "key" not in data:
        return json.dumps({"status": "FAIL", "error": "Invalid format"}).encode('ascii')
    session = get_session(data["key"])
    if session == "":
        return json.dumps({"status": "FAIL", "error": "Unknown session"}).encode('ascii')
    if path == "/checkword":
        if "word" not in data:
            return json.dumps({"status": "FAIL", "error": "Invalid format"}).encode('ascii')
        vector = json.loads(data["word"])
        if table.check_validity(vector):
            if vector in session["used_vectors"]:
                return json.dumps({"status": "FAIL", "error": "Duplicate vector"}).encode('ascii')
            word = table.get_word(vector)
            if len(word) < 3 or len(word) > 10:
                return json.dumps({"status": "FAIL", "error": "Invalid word"}).encode('ascii')
            if wordlists[len(word)-3].is_word(word):
                session["score"] = session["score"] + len(word) * len(word)
                session["found_words"].append(word)
                session["used_vectors"].append(vector)
                return json.dumps({"word": word, "score": session["score"], "status": "OK"}).encode('ascii')
        return json.dumps({"status": "FAIL", "error": "Not a word"}).encode('ascii')
    if path == "/getsessions":
        return json.dumps({"sessions": sessions, "status": "OK"}).encode('ascii')
    return json.dumps({"status": "FAIL", "error": "Invalid path"}).encode('ascii')

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(handle_rest_get(self.path))
    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        response = BytesIO()
        response.write(json.dumps({"status": "FAIL"}).encode('ascii'))
        self.wfile.write(response.getvalue())
    def do_PUT(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        response = BytesIO()
        response.write(handle_rest_put(self.path, body))
        self.wfile.write(response.getvalue())

httpd = HTTPServer(('localhost', 8088), MyHTTPRequestHandler)
httpd.socket = ssl.wrap_socket(httpd.socket, keyfile="/home/juice/key.pem",
                               certfile="/home/juice/cert.pem", server_side=True)
httpd.serve_forever()
