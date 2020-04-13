from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
import ssl
import json

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

def handle_rest_get(path):
    if path == "/getwords":
        ret = { "table": table.get_raw_table(),
                "status": "OK" }
        return json.dumps(ret).encode('ascii')
    return json.dumps({"status": "FAIL"}).encode('ascii')

def handle_rest_put(path, body):
    if path == "/checkword":
        data = json.loads(body)
        print(data["word"])
        if table.check_validity(json.loads(data["word"])):
            word = table.get_word(json.loads(data["word"]))
            print(word)
            if len(word) < 3 or len(word) > 10:
                return json.dumps({"status": "FAIL"}).encode('ascii')
            if wordlists[len(word)-3].is_word(word):
                return json.dumps({"status": "OK"}).encode('ascii')
    return json.dumps({"status": "FAIL"}).encode('ascii')

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(handle_rest_get(self.path))
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        response = BytesIO()
        response.write(b'This is POST request. ')
        response.write(b'Received: ')
        response.write(body)
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
