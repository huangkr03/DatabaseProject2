import sys

import psycopg2 as pg
from psycopg2.extensions import *
from Task1 import StockIn
from Task2 import PlaceOrder
from Task3 import UpdateOrder
from Task4 import DeleteOrder
from Select import SelectItem

methods = {}
connected = False
output = open('output.txt', 'w')


def connect_db():
    global connected
    try:
        conn = pg.connect(database='project_2', user='postgres',
                          password='123456', host='localhost', port=5432)
        connected = True
        conn.autocommit = False
        return conn
    except Exception:
        return None


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


def get_format(result: list):
    m = [(max(len(str(a[i])) for a in result) + 1) for i in range(len(result[0]))]
    s = [('%-' + str(i) + 's') for i in m]
    out = ''.join(s)
    return out


if __name__ == '__main__':
    conn: connection
    conn = connect_db()
    if conn is None:
        print('connection failed')
        sys.exit(1)
    methods = {}

    drop_tables()
    create_tables()
    import_data()

    # t1 = StockIn(conn)
    # t1.insert_data()
    # t2 = PlaceOrder(conn)
    # t2.insert_data()
    # t3 = UpdateOrder(conn)
    # t3.update_data()
    # t4 = DeleteOrder(conn)
    # t4.delete_data()

    select = SelectItem(conn)
    methods.setdefault('Q6', select.getAllStaffCount)
    methods.setdefault('Q7', select.getContractCount)
    methods.setdefault('Q8', select.getOrderCount)
    methods.setdefault('Q9', select.getNeverSoldProductCount)
    methods.setdefault('Q10', select.getFavoriteProductModel)
    methods.setdefault('Q11', select.getAvgStockByCenter)
    methods.setdefault('Q12', select.getProductByNumber)
    methods.setdefault('Q13', select.getContractInfo)

    output = open('output.txt', 'w')
    commands = ['Q6', 'Q7', 'Q8', 'Q9', 'Q10', 'Q11']

    product_nums = input().split(',')
    contract_nums = input().split(',')
    for command in commands:
        output_str = ''
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
        print(output_str, end='')
        output.write(output_str)
    # Q12
    for product_num in product_nums:
        output_str = ''
        result = methods.get('Q12')(product_num)
        output_str += ('Q12' + '\n')
        result.insert(0, ['supply_center', 'product_number', 'product_model', 'purchase_price', 'quantity'])
        out = get_format(result)
        for i in result:
            i = [str(k) for k in i]
            output_str += (out % tuple(i))
            output_str += '\n'
        print(output_str, end='')
    # Q13
    for contract_num in contract_nums:
        output_str = ''
        result, result1 = methods.get('Q13')(contract_num)
        if not result:
            result = ['None', 'None', 'None', 'None']
        output_str += ('Q13' + '\n')
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
        print(output_str, end='')
    output.flush()
    output.close()
    conn.close()
