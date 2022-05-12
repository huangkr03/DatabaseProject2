from psycopg2.extensions import cursor, connection
import csv


class StockIn:
    def __init__(self, conn: connection):
        self.__cur: cursor = conn.cursor()
        self.__conn = conn

    def __check_1(self, center_name: str, salesman_id: str):
        self.__cur.execute("select task1_1('%s', '%s')" % center_name, salesman_id)
        b1 = self.__cur.fetchone()[0]
        self.__cur.execute("select task1_2('%s')" % salesman_id)
        b2 = self.__cur.fetchone()[0]
        return b1 & b2

    def insert_data(self):
        self.__conn.autocommit = True
        self.__task1_create_function()
        self.__create_table()
        with open('task/task1_in_stoke_test_data_publish.csv') as task1:
            reader = csv.reader(task1)
            reader.__next__()
            for line in reader:
                line = str(line).lstrip('[').rstrip(']')
                try:
                    self.__cur.execute('insert into stockIn values (' + line + ')')
                except Exception as e:
                    # print(e)
                    continue
        self.__conn.autocommit = False
        # self.__cur.execute('alter table stockIn add column current_quantity integer;')
        # self.__cur.execute('update stockIn set current_quantity = quantity;')
        # self.__conn.commit()

    def __task1_create_function(self):
        self.__cur.execute('''drop function if exists task1_1;''')
        self.__cur.execute('''drop function if exists task1_2;''')
        self.__cur.execute('''create function task1_1(center_name varchar, salesman_id char(8), product_model varchar, qt integer)
    returns bool as
$$
declare
    result varchar;
    ch     varchar;
begin
    select s.supply_center
    into result
    from staff s
    where s.number = salesman_id;
    if result = center_name
    then
        select model
        into ch
        from stock
        where model = product_model
          and center = center_name;
        if ch is not null
        then
            update stock
            set quantity = quantity + qt
            where model = product_model
              and center = center_name;
            update stock
            set current_quantity = current_quantity + qt
            where model = product_model
              and center = center_name;
        else
            insert into stock values (product_model, center_name, qt, qt);
        end if;
        return true;
    else
        return false;
    end if;
end;
$$ language plpgsql;''')
        self.__cur.execute('''create function task1_2(salesman_num char(8))
        returns bool as
    $$
    declare
        result varchar;
    begin
        select s.type into result from staff s where s.number = salesman_num;
        if (result = 'Supply Staff')
        then
            return true;
        else
            return false;
        end if;
    end;
    $$ language plpgsql;''')
        self.__conn.commit()

    def __create_table(self):
        self.__cur.execute('drop table if exists stockIn;')
        self.__cur.execute('''create table if not exists stockIn
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
    foreign key (supply_staff) references staff (number),
    check ( task1_2(supply_staff) ),
    check ( task1_1(supply_center, supply_staff, product_model, quantity) )
);''')
        self.__conn.commit()
