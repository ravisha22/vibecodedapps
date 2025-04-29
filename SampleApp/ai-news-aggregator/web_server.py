import http.server
import socketserver
import json
from aggregator import get_news_from_db, update_news_read_status
from urllib.parse import urlparse, parse_qs

PORT = 8000

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        if path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as file:
                self.wfile.write(file.read())
        elif path == '/news':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            news = get_news_from_db()
            self.wfile.write(json.dumps(news).encode())
        elif path == '/mark-as-read':
            news_id = int(query_params.get('id', [None])[0])
            
            if news_id != None:
                update_news_read_status(news_id, 1)
                self.send_response(200)
            else:
                self.send_response(400)
            self.end_headers()

        else:
            return super().do_GET()

    def log_message(self, format, *args):
        # Do not log the request
        return
        

def run_server():
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
