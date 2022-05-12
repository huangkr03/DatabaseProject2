from http.server import HTTPServer, BaseHTTPRequestHandler

host = ('127.0.0.1', 8765)


class Request(BaseHTTPRequestHandler):
    timeout = 5
    server_version = "Apache"  # 设置服务器返回的的响应头

    def return_page(self, page_name: str):
        html_page = open(page_name, encoding='utf-8')
        contents = html_page.readlines()
        homepage = ''
        for e in contents:
            homepage += e
        self.wfile.write(homepage.encode())

    def do_GET(self):
        self.send_response(200)
        # self.send_header("Content-type", "text/html")
        if self.path == '/':  # get page
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.return_page('client/login.html')
        elif self.path == '/login.css':
            self.send_header("Content-type", "text/css")
            self.end_headers()
            self.return_page('client/login.css')
        elif self.path == '/login.js':
            self.send_header("Content-type", "application/x-javascript")
            self.end_headers()
            self.return_page('client/login.js')

    def do_POST(self):
        path = self.path
        if path == '/':
            data = self.rfile.read(int(self.headers['content-length']))  # get posted data
            form = data.decode()
            form = {i.split('=')[0] : i.split('=')[1] for i in form.split('&')}
            print(form)
            self.send_response(403)
            self.end_headers()


if __name__ == '__main__':
    server = HTTPServer(host, Request)
    print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()
