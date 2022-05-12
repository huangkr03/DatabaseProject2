import asyncio
from asyncio.streams import StreamReader, StreamWriter

keys = ('method', 'path', 'Range')


class HTTPHeader:
    """
        HTTPHeader template, you can use it directly
    """

    def __init__(self):
        self.headers = {key: None for key in keys}
        self.version = '1.0 '
        self.server = 'Tai'
        self.contentLength = None
        self.contentRange = None
        self.contentType = None
        self.location = None
        self.range = None
        self.state = None

    def parse_header(self, line):
        fileds = line.split(' ')
        if fileds[0] == 'GET' or fileds[0] == 'POST' or fileds[0] == 'HEAD':
            self.headers['method'] = fileds[0]
            self.headers['path'] = fileds[1]
        fileds = line.split(': ', 1)
        if fileds[0] == 'Id':
            self.headers['id'] = fileds[1]
        if fileds[0] == 'Range':
            start, end = (fileds[1].strip().strip('bytes=')).split('-')
            self.headers['Range'] = start, end
        if fileds[0] == 'Danmu':
            self.headers['danmu'] = fileds[1]

    def set_version(self, version):
        self.version = version

    def set_location(self, location):
        self.location = location

    def set_state(self, state):
        self.state = state

    def set_info(self, contentType, contentRange):
        self.contentRange = contentRange
        self.contentType = contentType

    def set_range(self):
        start, end = self.headers['Range']
        contentRange = int(self.contentRange)
        if start == '':
            end = int(end)
            start = contentRange - end
            end = contentRange - 1
        if end == '':
            end = contentRange - 1
        start = int(start)
        end = int(end)
        self.contentLength = str(end - start + 1)
        self.range = (start, end)

    def get(self, key):
        return self.headers.get(key)

    def message(self):  # Return response header
        return 'HTTP/' + self.version + self.state + '\r\n' \
               + ('Content-Length:' + self.contentLength + '\r\n' if self.contentLength else '') \
               + ('Content-Type:' + 'text/html' + '; charset=utf-8' + '\r\n' if self.contentType else '') \
               + 'Server:' + self.server + '\r\n' \
               + ('Accept-Ranges: bytes\r\n' if self.range else '') \
               + ('Content-Range: bytes ' + str(self.range[0]) + '-' + str(
            self.range[1]) + '/' + self.contentRange + '\r\n' if self.range else '') \
               + ('Location: ' + self.location + '\r\n' if self.location else '') \
               + 'Connection: close\r\n' + '\r\n'


def return_page(page_name: str, httpHeader, writer):
    httpHeader.set_state('200 OK')
    writer.write(httpHeader.message().encode(encoding='utf-8'))  # construct 200 OK HTTP header
    html_page = open(page_name, encoding='utf-8')
    contents = html_page.readlines()
    homepage = ''
    for e in contents:
        homepage += e
    writer.write(homepage.encode())


async def dispatch(reader: StreamReader, writer: StreamWriter):
    # Use reader to receive HTTP request
    # Writer to send HTTP request
    httpHeader = HTTPHeader()
    while True:
        data = await reader.readline()
        message = data.decode()
        print(message)
        httpHeader.parse_header(message)
        if data == b'\r\n' or data == b'':
            break
    if httpHeader.get('method') == 'GET':
        if httpHeader.get('path') == '/':  # get page
            print('get page')
            return_page('login.html', httpHeader, writer)
        elif httpHeader.get('path') == '/login.css':
            return_page('login.css', httpHeader, writer)
        elif httpHeader.get('path') == '/login.js':
            return_page('login.js', httpHeader, writer)
        elif '?' in httpHeader.get('path'):
            print(1)
            # id = httpHeader.get('id')
            # if danmakusManagers.get(id) is None:  # there's no this client in client list
            #     print('new client login, id = ' + id, end='')
            #     manager = DanmakusManager(id)
            #     danmakusManagers.setdefault(id, manager)
            #     danmakusManagersList.append(manager)
            # manager = danmakusManagers.get(id)
            # danmu = manager.pop()
            # if danmu is not None:
            #     httpHeader.set_state('200 OK')
            #     writer.write(httpHeader.message().encode())
            #     writer.write(danmu.encode())
            # else:
            #     httpHeader.set_state('404 Not Found')
            #     writer.write(httpHeader.message().encode(encoding='utf-8'))
        else:  # if page name is not correct return 404 not found
            httpHeader.set_state('404 Not Found')
            writer.write(httpHeader.message().encode(encoding='utf-8'))
    elif httpHeader.get('method') == 'POST':  # get password
        data = await reader.readuntil(b'\x00')
        message = data.decode()
        print(message, flush=True)
        httpHeader.set_state('200')
        writer.write(httpHeader.message().encode(encoding='utf-8'))  # construct 200 OK HTTP header
    writer.close()


if __name__ == '__main__':
    port = 8765
    loop = asyncio.get_event_loop()
    co_ro = asyncio.start_server(dispatch, '127.0.0.1', port, loop=loop)
    server = loop.run_until_complete(co_ro)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
