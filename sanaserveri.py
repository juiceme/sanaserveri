from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
import ssl

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
        return table.get_raw_table()
    return b"{status: OK}"

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
        response.write(b'This is PUT request. ')
        response.write(b'Received: ')
        response.write(body)
        self.wfile.write(response.getvalue())

httpd = HTTPServer(('localhost', 8088), MyHTTPRequestHandler)
httpd.socket = ssl.wrap_socket(httpd.socket, keyfile="/home/juice/key.pem",
                               certfile="/home/juice/cert.pem", server_side=True)
httpd.serve_forever()
