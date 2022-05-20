import csv


class PlaceOrder:
    def __init__(self, pool):
        self.__pool = pool

    def insert_data(self):
        conn = self.__pool.get_conn()
        cur = conn.cursor()
        self.__task2_create_function(conn)
        self.__create_table(conn)
        # conn.autocommit = True
        with open('task/task2_test_data_publish.csv') as task2:
            reader = csv.reader(task2)
            reader.__next__()
            for line in reader:
                try:
                    cur.execute(
                        "insert into contracts values ('" + line[0] + "','" + line[4] + "','" + line[1] + "',0)")
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    # print(line)
                    print(e)
                    continue
        with open('task/task2_test_data_publish.csv') as task2:
            reader = csv.reader(task2)
            reader.__next__()
            for line in reader:
                contract_num = line[0]
                line = str(line).lstrip('[').rstrip(']')
                try:
                    cur.execute(
                        'insert into orders (contract_num,enterprise,product_model,quantity,contract_manager,' +
                        'contract_date,estimate_delivery_date,lodgement_date,salesman_num,contract_type) values ('
                        + line + ')')
                    cur.execute("update contracts set tot_order = tot_order + 1 " +
                                "where contract_num = '%s'" % contract_num)
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    # print(line)
                    print(e)
                    continue
        # conn.autocommit = False
        cur.close()
        conn.close()

    def __task2_create_function(self, conn):
        cur = conn.cursor()
        cur.execute('drop table if exists orders, contracts;')
        cur.execute('''drop function if exists task2_1;''')
        cur.execute('''drop function if exists task2_2;''')
        cur.execute('''create function task2_1(qt integer, prod_model varchar, enp_name varchar)
    returns bool as
$$
declare
    result integer;
    center_name varchar;
begin
    select en.supply_center
    into center_name
    from enterprise en
    where name = enp_name;

    select current_quantity
    into result
    from stock
    where model = prod_model
      and center = center_name;

    if result is not null
    then
        if (result >= qt)
        then
            update stock
            set current_quantity = current_quantity - qt
            where model = prod_model
              and center = center_name;
            return true;
        else
            return false;
        end if;
    else
        return false;
    end if;
end;
$$ language plpgsql;''')
        cur.execute('''create function task2_2(salesman_num char(8))
        returns bool as
    $$
    declare
        result varchar;
    
    begin
        select s.type
        into result
        from staff s
        where s.number = salesman_num;
        if (result = 'Salesman')
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
        cur.execute('''create table if not exists orders
(
    id                     serial primary key,
    contract_num           char(10) not null,
    enterprise             varchar  not null,
    product_model          varchar  not null,
    quantity               integer  not null,
    contract_manager       char(8)  not null,
    contract_date          date     not null,
    estimate_delivery_date date     not null,
    lodgement_date         date,
    salesman_num           char(8)  not null,
    contract_type          varchar  not null,
    foreign key (enterprise) references enterprise (name),
    foreign key (product_model) references product (model),
    foreign key (salesman_num) references staff (number),
    foreign key (contract_manager) references staff (number),
    check (task2_2(salesman_num)),
    check (task2_1(quantity, product_model, enterprise))
);''')
        cur.execute('''create table if not exists contracts
(
    contract_num char(10) primary key,
    manager varchar not null references staff (number),
    enterprise varchar not null references enterprise (name),
    tot_order    integer not null
);''')
        conn.commit()
        cur.close()
