import os
import http.server
import socketserver
import multiprocessing
from http import HTTPStatus

def server():
    PORT = 60407 # GODOT

    class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
            self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')

    Handler = MyHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Godot serving at port {PORT}")
        httpd.serve_forever()

def run():
    multiprocessing.Process(target=server, args=(), daemon=True).start()
    while True:
        pass
    
if __name__ == '__main__':
    print("Starting Godot server")
    run()