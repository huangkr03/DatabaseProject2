import csv


class StockIn:
    def __init__(self, pool):
        self.__pool = pool

    def insert_data(self):
        conn = self.__pool.get_conn()
        cur = conn.cursor()
        self.__task1_create_function(conn)
        self.__create_table(conn)
        # conn.autocommit = True
        with open('task/task1_final.csv') as task1:
            reader = csv.reader(task1)
            reader.__next__()
            for line in reader:
                line = str(line).lstrip('[').rstrip(']')
                try:
                    cur.execute('insert into stockIn values (' + line + ')')
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    # print(e)
                    continue
        # conn.autocommit = False
        # conn.commit()
        cur.close()
        conn.close()

    def __task1_create_function(self, conn):
        cur = conn.cursor()
        cur.execute('drop table if exists stockIn;')
        cur.execute('drop function if exists task1_1;')
        cur.execute('drop function if exists task1_2;')
        cur.execute('''create function task1_1(center_name varchar, salesman_id char(8), product_model varchar, qt integer)
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
        cur.execute('''create function task1_2(salesman_num char(8))
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
        conn.commit()
        cur.close()

    def __create_table(self, conn):
        cur = conn.cursor()
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
    foreign key (supply_staff) references staff (number),
    check ( task1_2(supply_staff) ),
    check ( task1_1(supply_center, supply_staff, product_model, quantity) )
);''')
        conn.commit()
        cur.close()
