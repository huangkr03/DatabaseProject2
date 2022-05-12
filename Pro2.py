import psycopg2 as pg
from psycopg2.extensions import *
from Task1 import StockIn
from Task2 import PlaceOrder
from Task3 import UpdateOrder
from Task4 import DeleteOrder
from Select import SelectItem


conn: connection
cur: cursor


def connect_db():
    try:
        conn = pg.connect(database='project_2', user='postgres',
                          password='123456', host='localhost', port=5432)
        conn.autocommit = False
    except Exception as e:
        raise e
    else:
        return conn, conn.cursor()


def create_tables(cur: cursor, conn: connection):
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
    conn.commit()


def import_data(cur: cursor, conn: connection):
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
    conn.commit()


def drop_tables(cur: cursor, conn: connection):
    cur.execute('drop table if exists product, enterprise, center, staff, stockIn, orders, contracts;')
    conn.commit()


if __name__ == '__main__':
    conn, cur = connect_db()
    methods = {}

    drop_tables(cur, conn)
    create_tables(cur, conn)
    import_data(cur, conn)

    print(1)
    t1 = StockIn(cur, conn)
    t1.insert_data()
    print(2)
    t2 = PlaceOrder(cur, conn)
    t2.insert_data()
    print(3)
    t3 = UpdateOrder(cur, conn)
    t3.update_data()
    print(4)
    t4 = DeleteOrder(cur, conn)
    t4.delete_data()

    select = SelectItem(cur, conn)
    methods.setdefault('Q6', select.getAllStaffCount)
    methods.setdefault('Q7', select.getContractCount)
    methods.setdefault('Q8', select.getOrderCount)
    methods.setdefault('Q9', select.getNeverSoldProductCount)
    methods.setdefault('Q10', select.getFavoriteProductModel)
    methods.setdefault('Q11', select.getAvgStockByCenter)
    methods.setdefault('Q12', select.getProductByNumber)
    methods.setdefault('Q13', select.getContractInfo)

    output = open('output.txt', 'w')
    while (True):
        method = input('Please Input Method: ')
        if method.lower() == 'exit':
            break
        if method not in methods.keys():
            print('Method is not correct! Please input Q6 ~ Q13')
            continue
        if method == 'Q12':
            product_num = input('Input Product_num: ')
            result = methods.get(method)(product_num)
            output.write(method + '\n')
            output.write('supply_center\tproduct_number\tproduct_model\tpurchase_price\tquantity\n')
            for i in result:
                i = [str(k) for k in i]
                output.write('\t'.join(i))
                output.write('\n')
        elif method == 'Q13':
            contract_num = input('Input Contract_num: ')
            result, result1 = methods.get(method)(contract_num)
            if not result:
                result = ['None', 'None', 'None', 'None']
            output.write(method + '\n')
            output.write('number: ' + str(result[0]) + '\n')
            output.write('manager: ' + str(result[1]) + '\n')
            output.write('enterprise: ' + str(result[2]) + '\n')
            output.write('supply_center: ' + str(result[3]) + '\n')
            output.write(
                'product_model\tsalesman\tquantity\tunit_price\testimate_delivery_date\tlodgement_date')
            for i in result1:
                i = [str(k) for k in i]
                output.write('\t'.join(i))
                output.write('\n')
        else:
            result = methods.get(method)()
            if method in ['Q7', 'Q8', 'Q9']:
                output.write(method + '\t')
            else:
                output.write(method + '\n')
            for i in result:
                i = [str(k) for k in i]
                output.write('\t'.join(i))
                output.write('\n')
    output.flush()
    output.close()
    conn.close()
