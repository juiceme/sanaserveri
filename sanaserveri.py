from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
import ssl
import json
import time
import _thread
import random

from wordlist import WordList as wl
from wordtable import WordTable as wt
from database import Database as db
from session import Session as se

wordlists = []
for i in range(3,11):
    wordlists.append(wl("words" + str(i)))

database = db()
session = se()

def execute_periodically(period, function):
    def timer_tick():
        t = time.time()
        count = 0
        while True:
            count += 1
            yield max(t + count*period - time.time(), 0)
    tick = timer_tick()
    while True:
        function()
        time.sleep(next(tick))

def refresh_wordtable():
    global table
    table = wt()
    session.load_highscores()
    session.update_highscores()
    session.clear_used_vectors()
    session.clear_scores()
    for i in wordlists:
        table.add_word(i.get_random())

    table.print_table()
    print()
    table.fill_table()
    table.print_table()
    print()

_thread.start_new_thread(execute_periodically, (60, refresh_wordtable))

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
            if session.user_is_loggedin(current_session):
                if database.logout(current_session["key"]):
                    session.set_user(current_session, "")
                else:
                    print("Problem logging out user")
            session.delete(current_session)
            return json.dumps({"status": "OK"}).encode('ascii')
        if path == "/getwords":
            return json.dumps({ "table": table.get_raw_table(), "status": "OK" }).encode('ascii')
        if path == "/getstatistics":
            return json.dumps({"statistics": {"score": current_session["score"],
                                              "found_words": current_session["found_words"],
                                              "used_vectors": current_session["used_vectors"]},
                               "status": "OK"}).encode('ascii')
        if path == "/getsessions":
            if not session.user_is_loggedin(current_session):
                return json.dumps({"status": "FAIL", "error": "Not logged in"}).encode('ascii')
            else:
                if not session.user_is_admin(current_session):
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
            return json.dumps({"word": word, "score": current_session["score"], "status": "OK"}).encode('ascii')
        return json.dumps({"status": "FAIL", "error": "Not a word"}).encode('ascii')
    if path == "/login":
        if "username" not in data:
            return json.dumps({"status": "FAIL", "error": "No username"}).encode('ascii')
        username = data["username"]
        if "password" not in data:
            return json.dumps({"status": "FAIL", "error": "No password"}).encode('ascii')
        password = data["password"]
        if session.user_is_loggedin(current_session):
            return json.dumps({"status": "FAIL", "error": "Already logged in"}).encode('ascii')
        if database.login(username, password, current_session["key"]):
            session.set_user(current_session, username)
            return json.dumps({"status": "OK"}).encode('ascii')
        else:
            return json.dumps({"status": "FAIL", "error": "Invalid password"}).encode('ascii')
    if path == "/logout":
        if database.logout(current_session["key"]):
            session.set_user(current_session, "")
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
