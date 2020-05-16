from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
import ssl
import json
import hashlib
import time
import random

from wordlist import WordList as wl
from wordtable import WordTable as wt
from database import Database as db

wordlists = []
for i in range(3,11):
    wordlists.append(wl("words" + str(i)))

table = wt()
for i in wordlists:
    table.add_word(i.get_random())

database = db()

table.print_table()
print()
table.fill_table()
table.print_table()

class Session:
    def __init__(self):
        self.sessions = []

    def create(self):
        key = hashlib.sha1(str(time.time()+random.randrange(1000)).encode('utf-8')).hexdigest()
        self.sessions.append({"key": key, "score": 0, "found_words": [], "used_vectors": [], "username": ""})
        return { "key": key, "status": "OK" }

    def delete(self, key):
        for i in self.sessions:
            if i["key"] == key:
                self.sessions.remove(i)
                return True
        return False

    def get(self, key):
        for i in self.sessions:
            if i["key"] == key:
                return i
        return False

    def set_user(self, key, username):
        for i in self.sessions:
            if i["key"] == key:
                i["username"] = username
                return True
        return False

    def dump(self):
        return self.sessions


session = Session()

def handle_rest_get(path, body):
    if path == "/startsession":
        return json.dumps(session.create()).encode('ascii')
    if body != "":
        data = json.loads(body)
        if "key" not in data:
            return json.dumps({"status": "FAIL", "error": "Invalid format"}).encode('ascii')
        current_session = session.get(data["key"])
        if current_session == False:
            return json.dumps({"status": "FAIL", "error": "Unknown session"}).encode('ascii')
        if path == "/stopsession":
            if current_session["username"] != "":
                if database.logout(current_session["key"]):
                    current_session["username"] = ""
                else:
                    print("Problem logging out user")
            if session.delete(current_session["key"]):
                return json.dumps({"status": "OK"}).encode('ascii')
            else:
                return json.dumps({"status": "FAIL", "error": "Unknown session"}).encode('ascii')
        if path == "/getwords":
            return json.dumps({ "table": table.get_raw_table(), "status": "OK" }).encode('ascii')
        if path == "/getstatistics":
            return json.dumps({"statistics": {"score": current_session["score"],
                                              "found_words": current_session["found_words"],
                                              "used_vectors": current_session["used_vectors"]},
                               "status": "OK"}).encode('ascii')
        if path == "/getsessions":
            if current_session["username"] == "":
                return json.dumps({"status": "FAIL", "error": "Not logged in"}).encode('ascii')
            else:
                if current_session["username"] != "Admin":
                    return json.dumps({"status": "FAIL", "error": "No priviliges"}).encode('ascii')
                else:
                    return json.dumps({"sessions": session.dump(), "status": "OK"}).encode('ascii')
    return json.dumps({"status": "FAIL", "error": "Invalid path"}).encode('ascii')

def handle_rest_put(path, body):
    data = json.loads(body)
    if "key" not in data:
        return json.dumps({"status": "FAIL", "error": "Invalid format"}).encode('ascii')
    current_session = session.get(data["key"])
    if current_session == False:
        return json.dumps({"status": "FAIL", "error": "Unknown session"}).encode('ascii')
    if path == "/checkword":
        if "word" not in data:
            return json.dumps({"status": "FAIL", "error": "Invalid format"}).encode('ascii')
        vector = json.loads(data["word"])
        if not table.check_validity(vector):
            return json.dumps({"status": "FAIL", "error": "Invalid word vector"}).encode('ascii')
        if vector in current_session["used_vectors"]:
            return json.dumps({"status": "FAIL", "error": "Duplicate word vector"}).encode('ascii')
        word = table.get_word(vector)
        if len(word) < 3:
            return json.dumps({"status": "FAIL", "error": "Too short word"}).encode('ascii')
        if len(word) > 10:
            return json.dumps({"status": "FAIL", "error": "Too long word"}).encode('ascii')
        if wordlists[len(word)-3].is_word(word):
            current_session["score"] = current_session["score"] + len(word) * len(word)
            current_session["found_words"].append(word)
            current_session["used_vectors"].append(vector)
            database.update_highscore(current_session["key"], current_session["score"])
            return json.dumps({"word": word, "score": current_session["score"], "status": "OK"}).encode('ascii')
        return json.dumps({"status": "FAIL", "error": "Not a word"}).encode('ascii')
    if path == "/login":
        if "username" not in data:
            return json.dumps({"status": "FAIL", "error": "No username"}).encode('ascii')
        username = data["username"]
        if "password" not in data:
            return json.dumps({"status": "FAIL", "error": "No password"}).encode('ascii')
        password = data["password"]
        if current_session["username"] != "":
            return json.dumps({"status": "FAIL", "error": "Already logged in"}).encode('ascii')
        if database.login(username, password, current_session["key"]):
            current_session["username"] = username
            return json.dumps({"status": "OK"}).encode('ascii')
        else:
            return json.dumps({"status": "FAIL", "error": "Invalid password"}).encode('ascii')
    if path == "/logout":
        if database.logout(current_session["key"]):
            current_session["username"] = ""
            return json.dumps({"status": "OK"}).encode('ascii')
        else:
            return json.dumps({"status": "FAIL", "error": "Not logged in"}).encode('ascii')
    return json.dumps({"status": "FAIL", "error": "Invalid path"}).encode('ascii')

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        if "Content-Length" in self.headers:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            response = BytesIO()
            response.write(handle_rest_get(self.path, body))
            self.wfile.write(response.getvalue())
        else:
            self.wfile.write(handle_rest_get(self.path, ""))
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
    def log_message(self, format, *args):
        return
    
httpd = HTTPServer(('localhost', 8088), MyHTTPRequestHandler)
httpd.socket = ssl.wrap_socket(httpd.socket, keyfile="./key.pem",
                               certfile="./cert.pem", server_side=True)
httpd.serve_forever()
