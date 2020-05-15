from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
import ssl
import json
import hashlib
import time
import random
import mysql.connector as mariadb

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

mariadb_connection = mariadb.connect(user='sanaserveri', password='54n453rv3r1', database='sanaserveri', host='toosa')
cursor = mariadb_connection.cursor()

sessions = []
users = []

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

def get_user(username, password):
    for i in users:
        if i["username"] == username:
            if i["password"] == password:
                return True
            else:
                return False
    users.append({"username": username, "password": password})
    return True

def handle_rest_get(path, body):
    if path == "/startsession":
        return json.dumps(create_session()).encode('ascii')
    if body != "":
        data = json.loads(body)
        if "key" not in data:
            return json.dumps({"status": "FAIL", "error": "Invalid format"}).encode('ascii')
        session = get_session(data["key"])
        if session == "":
            return json.dumps({"status": "FAIL", "error": "Unknown session"}).encode('ascii')
        if path == "/getwords":
            ret = { "table": table.get_raw_table(),
                    "status": "OK" }
            return json.dumps(ret).encode('ascii')
        if path == "/getstatistics":
            return json.dumps({"statistics": {"score": session["score"],
                                              "found_words": session["found_words"],
                                              "used_vectors": session["used_vectors"]},
                               "status": "OK"}).encode('ascii')
        if path == "/getsessions":
            if "username" not in session:
                return json.dumps({"status": "FAIL", "error": "Not logged in"}).encode('ascii')
            else:
                if session["username"] != "Admin":
                    return json.dumps({"status": "FAIL", "error": "No priviliges"}).encode('ascii')
                else:
                    return json.dumps({"sessions": sessions, "status": "OK"}).encode('ascii')
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
        if not table.check_validity(vector):
            return json.dumps({"status": "FAIL", "error": "Invalid word vector"}).encode('ascii')
        if vector in session["used_vectors"]:
            return json.dumps({"status": "FAIL", "error": "Duplicate word vector"}).encode('ascii')
        word = table.get_word(vector)
        if len(word) < 3:
            return json.dumps({"status": "FAIL", "error": "Too short word"}).encode('ascii')
        if len(word) > 10:
            return json.dumps({"status": "FAIL", "error": "Too long word"}).encode('ascii')
        if wordlists[len(word)-3].is_word(word):
            session["score"] = session["score"] + len(word) * len(word)
            session["found_words"].append(word)
            session["used_vectors"].append(vector)
            try:
                cursor.execute("select id from highscores where username like %s", (session["key"],))
                records = cursor.fetchall()
                if cursor.rowcount == 0:
                    cursor.execute("insert into highscores (username, score) values (%s,%s)", (session["key"], session["score"]))
                    mariadb_connection.commit()
                else:
                    cursor.execute("update highscores set score=%s where username=%s ", (session["score"], session["key"]))
                    mariadb_connection.commit()
            except mariadb.Error as error:
                print("Error: {}".format(error))
            return json.dumps({"word": word, "score": session["score"], "status": "OK"}).encode('ascii')
        return json.dumps({"status": "FAIL", "error": "Not a word"}).encode('ascii')
    if path == "/login":
        if "username" not in data:
            return json.dumps({"status": "FAIL", "error": "No username"}).encode('ascii')
        username = data["username"]
        if "password" not in data:
            return json.dumps({"status": "FAIL", "error": "No password"}).encode('ascii')
        password = data["password"]
        if get_user(username, password):
            session["username"] = username
            return json.dumps({"status": "OK"}).encode('ascii')
        else:
            return json.dumps({"status": "FAIL", "error": "Invalid password"}).encode('ascii')
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
