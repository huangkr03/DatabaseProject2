import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

import psycopg2 as pg
from psycopg2.extensions import *

from Select import SelectItem
from Task1 import StockIn
from Task2 import PlaceOrder
from Task3 import UpdateOrder
from Task4 import DeleteOrder

host = ('127.0.0.1', 8765)

conn: connection
methods = {}
connected = False
output = open('output.txt', 'w')
user: str


class Request(BaseHTTPRequestHandler):
    timeout = 5
    server_version = "Apache"

    def return_page(self, path: str):
        html_page = open(path, encoding='utf-8')
        contents = html_page.readlines()
        html_page.close()
        homepage = ''
        for e in contents:
            homepage += e
        self.wfile.write(homepage.encode())

    def return_ico(self, path: str):
        image = open(path, 'rb')
        file_data = image.read()
        image.close()
        self.wfile.write(file_data)

    def return_output(self):
        global output
        output.close()
        output = open('output.txt', encoding='utf-8')
        contents = output.readlines()
        output.close()
        output = open('output.txt', mode='a', encoding='utf-8')
        homepage = ''
        for e in contents:
            homepage += e
        self.wfile.write(homepage.encode())

    def do_GET(self):
        global conn
        self.send_response(200)
        if self.path == '/':  # get page
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.return_page('client/login.html')
        elif self.path.endswith('html'):
            self.send_header("Content-type", "text/html")
            self.end_headers()
            if not connected:
                self.return_page('client/login.html')
            else:
                self.return_page('client' + self.path)
        elif self.path.endswith('css'):
            self.send_header("Content-type", "text/css")
            self.end_headers()
            self.return_page('client' + self.path)
        elif self.path.endswith('js'):
            self.send_header("Content-type", "application/x-javascript")
            self.end_headers()
            self.return_page('client' + self.path)
        elif self.path.endswith('ico'):
            self.send_header("Content-type", "image/x-icon")
            self.end_headers()
            self.return_ico('client' + self.path)
        if '?' in self.path:
            cur: cursor = conn.cursor()
            command = self.path.split('?')[1]
            if command == 'contract_num':
                print('get contract_num')
                cur.execute('select contract_num from contracts;')
                contract_num = cur.fetchall()
                contract_num = [c[0] for c in contract_num]
                self.send_response(200)
                self.end_headers()
                self.wfile.write('&'.join(contract_num).encode())
            elif command == 'product_num':
                print('get product_num')
                cur.execute('select distinct number from product;')
                numbers = cur.fetchall()
                numbers = [n[0] for n in numbers]
                self.send_response(200)
                self.end_headers()
                self.wfile.write('&'.join(numbers).encode())
            elif command == 'import':
                print("import")
                import_data()
                self.send_response(200)
                self.end_headers()
            elif command == 'export':
                self.send_response(200)
                self.send_header("Content-Disposition", "output.txt")
                self.end_headers()
                self.return_output()
            elif command == 'person_info':
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                # print(str(get_person_info()))
                response = json.dumps(get_person_info()[0])
                self.wfile.write(response.encode())
            cur.close()
            conn.commit()

    def do_POST(self):
        path = self.path
        global conn
        if '?' not in path:
            data = self.rfile.read(int(self.headers['content-length']))  # get posted data
            form = data.decode()
            form = {i.split('=')[0]: i.split('=')[1] for i in form.split('&')}
            if not connected:
                connect_db(form)
            if not connected:
                self.send_response(200)
                self.end_headers()
                self.return_page('client/error.html')
            else:
                init_database()
                self.send_response(200)
                self.end_headers()
                self.return_page('client/database.html')
        else:
            cur: cursor = conn.cursor()
            command = self.path.split('?')[1]
            if command.startswith('Q'):
                global output
                output_str = ''
                if command == 'Q12':
                    product_num = self.rfile.read(int(self.headers['content-length'])).decode()
                    result = methods.get(command)(product_num)
                    output_str += (command + '\n')
                    result.insert(0, ['supply_center', 'product_number', 'product_model', 'purchase_price', 'quantity'])
                    out = get_format(result)
                    for i in result:
                        i = [str(k) for k in i]
                        output_str += (out % tuple(i))
                        output_str += '\n'
                elif command == 'Q13':
                    contract_num = self.rfile.read(int(self.headers['content-length'])).decode()
                    result, result1 = methods.get(command)(contract_num)
                    if not result:
                        result = ['None', 'None', 'None', 'None']
                    output_str += (command + '\n')
                    output_str += ('number: ' + str(result[0]) + '\n')
                    output_str += ('manager: ' + str(result[1]) + '\n')
                    output_str += ('enterprise: ' + str(result[2]) + '\n')
                    output_str += ('supply_center: ' + str(result[3]) + '\n')
                    result1.insert(0, ['product_model', 'salesman', 'quantity', 'unit_price', 'estimate_delivery_date',
                                       'lodgement_date'])
                    out = get_format(result1)
                    for i in result1:
                        i = [str(k) for k in i]
                        output_str += (out % tuple(i))
                        output_str += '\n'
                else:
                    result = methods.get(command)()
                    if command in ['Q7', 'Q8', 'Q9']:
                        output_str += (command + '\t')
                        output_str += str(result[0][0]) + '\n'
                    else:
                        out = get_format(result)
                        output_str += (command + '\n')
                        for i in result:
                            i = [str(k) for k in i]
                            output_str += (out % tuple(i))
                            output_str += '\n'
                print(output_str)
                output.write(output_str)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(output_str.encode())
            elif command == 'sql':
                sql = self.rfile.read(int(self.headers['content-length']))
                try:
                    cur.execute(sql)
                    self.send_response(200)
                    self.end_headers()
                except Exception as e:
                    conn.rollback()
                    response = str(e)
                    response = response.split('\n')
                    response = response[0] + '\n' + response[1]
                    self.send_response(400)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write(response.encode())
            elif command == 'select':
                sql = self.rfile.read(int(self.headers['content-length']))
                try:
                    cur.execute(sql)
                    self.send_response(200)

                    result = [[col[0] for col in cur.description]]
                    result.extend(cur.fetchall())
                    out = get_format(result)
                    print(out)
                    output_str = sql.decode() + '\n'
                    self.send_header("rows", str(len(result) - 1))
                    self.end_headers()
                    for i in result:
                        i = [str(k) for k in i]
                        print(tuple(i))
                        output_str += (out % tuple(i))
                        output_str += '\n'
                    print(output_str)
                    self.wfile.write(output_str.encode())
                except Exception as e:
                    conn.rollback()
                    response = str(e)
                    response = response.split('\n')
                    response = response[0] + '\n' + response[1]
                    self.send_response(400)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write(response.encode())
            cur.close()


def get_format(result: list):
    m = [(max(len(str(a[i])) for a in result) + 1) for i in range(len(result[0]))]
    s = [('%-' + str(i) + 's') for i in m]
    out = ''.join(s)
    return out


def get_person_info():
    global conn
    cur: cursor = conn.cursor()
    cur.execute("select * from pg_roles where rolname = '" + user + "';")
    columns = [col[0] for col in cur.description]
    data = [
        dict(zip(columns, row))
        for row in cur.fetchall()
    ]
    cur.close()
    return data


def connect_db(form: dict):
    global conn, connected, user
    try:
        if connected:
            conn.close()
        conn = pg.connect(database=form.get('database'), user=form.get('user'),
                          password=form.get('password'), host=form.get('host'), port=5432)
        connected = True
        user = form.get('user')
        conn.autocommit = False
    except Exception:
        connected = False


def create_tables():
    global conn
    cur: cursor = conn.cursor()
    cur.execute('''create table if not exists center
(
    id   integer primary key,
    name varchar not null unique
);''')
    cur.execute('''create table if not exists product
(
    id         integer primary key,
    number     char(8) not null,
    model      varchar unique,
    name       varchar not null,
    unit_price numeric not null
);''')
    cur.execute('''create table if not exists enterprise
(
    id            integer primary key,
    name          varchar not null unique,
    country       varchar not null,
    city          varchar,
    supply_center varchar not null,
    industry      varchar not null,
    foreign key (supply_center) references center (name)
);''')
    cur.execute('''create table if not exists staff
(
    id            integer primary key,
    name          varchar  not null,
    age           integer  not null,
    gender        varchar  not null check ( gender in ('Male', 'Female')),
    number        char(8)  not null unique,
    supply_center varchar  not null,
    mobile_number char(11) not null,
    type          varchar check ( type in ('Director', 'Supply Staff', 'Salesman', 'Contracts Manager')),
    foreign key (supply_center) references center (name)
);''')
    cur.execute('''create table if not exists stockIn
(
    id             integer primary key,
    supply_center  varchar not null,
    product_model  varchar not null,
    supply_staff   char(8) not null,
    date           date    not null,
    purchase_price numeric not null,
    quantity       integer not null,
    foreign key (supply_center) references center (name),
    foreign key (product_model) references product (model),
    foreign key (supply_staff) references staff (number)
);''')
    cur.execute('''create table if not exists orders
(
    id                     serial primary key,
    contract_num           char(10) not null,
    enterprise             varchar  not null,
    product_model          varchar  not null,
    quantity               integer  not null,
    contract_manager       varchar  not null,
    contract_date          date     not null,
    estimate_delivery_date date     not null,
    lodgement_date         date,
    salesman_num           char(8)  not null,
    contract_type          varchar  not null,
    foreign key (enterprise) references enterprise (name),
    foreign key (product_model) references product (model),
    foreign key (salesman_num) references staff (number),
    foreign key (contract_manager) references staff (number)
);''')
    cur.execute('''
create table if not exists stock
(
    model            varchar not null,
    center           varchar not null,
    quantity         integer not null,
    current_quantity integer not null,
    primary key (model, center)
);''')
    cur.close()
    conn.commit()


def import_data():
    global conn
    cur: cursor = conn.cursor()
    drop_tables()
    create_tables()
    center = open('center.csv')
    center.readline()
    enterprise = open('enterprise.csv')
    enterprise.readline()
    product = open('model.csv')
    product.readline()
    staff = open('staff.csv')
    staff.readline()
    cur.copy_expert('copy center from stdin with (format csv)', center)
    cur.copy_expert('copy enterprise from stdin with (format csv)', enterprise)
    cur.copy_expert('copy product from stdin with (format csv)', product)
    cur.copy_expert('copy staff from stdin with (format csv)', staff)
    center.close()
    enterprise.close()
    product.close()
    staff.close()
    cur.close()
    conn.commit()

    t1 = StockIn(conn)
    t1.insert_data()
    t2 = PlaceOrder(conn)
    t2.insert_data()
    t3 = UpdateOrder(conn)
    t3.update_data()
    t4 = DeleteOrder(conn)
    t4.delete_data()


def drop_tables():
    global conn
    cur: cursor = conn.cursor()
    cur.execute('drop table if exists product, enterprise, center, staff, stockIn, orders, contracts, stock;')
    cur.close()
    conn.commit()


def init_database():
    global conn, methods
    cur: cursor = conn.cursor()

    select = SelectItem(conn)
    methods.setdefault('Q6', select.getAllStaffCount)
    methods.setdefault('Q7', select.getContractCount)
    methods.setdefault('Q8', select.getOrderCount)
    methods.setdefault('Q9', select.getNeverSoldProductCount)
    methods.setdefault('Q10', select.getFavoriteProductModel)
    methods.setdefault('Q11', select.getAvgStockByCenter)
    methods.setdefault('Q12', select.getProductByNumber)
    methods.setdefault('Q13', select.getContractInfo)
    cur.close()


class ThreadingHttpServer(ThreadingMixIn, HTTPServer):
    pass


if __name__ == '__main__':
    myServer = ThreadingHttpServer(host, Request)
    print("Starting server, listen at: %s:%s" % host)
    try:
        myServer.serve_forever()
    except Exception:
        myServer.server_close()
