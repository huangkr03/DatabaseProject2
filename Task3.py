class UpdateOrder:
    def __init__(self, pool):
        self.__pool = pool

    def update_data(self):
        conn = self.__pool.get_conn()
        cur = conn.cursor()
        self.__task3_create_function(conn)
        with open('task/task3_final.tsv') as task3:
            task3.readline()
            lines = task3.readlines()
            for line in lines:  # contract0 product_model1 salesman2 quantity3 estimate_delivery_date4 lodgement_date5
                line = line.rstrip('\n')
                line = line.split('\t')
                # print(line)
                cur.execute("select task3_1('" + line[2] + "', '" + line[0] + "', '" + line[1] + "')")
                if cur.fetchone()[0]:
                    cur.execute(
                        "select task3_2('" + line[0] + "', " + line[3] + ", '" + line[1] + "', '" + line[2] + "')")
                    cur.execute(
                        "select task3_3('" + line[0] + "', " + line[3] + ",'" + line[1] + "', '" + line[2] + "')")
                    # "select task3_3('" + line[0] + "', " + line[3] + ')')
                    # print(cur.fetchone()[0])
        conn.commit()
        cur.close()
        conn.close()

    def __task3_create_function(self, conn):
        cur = conn.cursor()
        cur.execute('''drop function if exists task3_1;''')
        cur.execute('''drop function if exists task3_2;''')
        cur.execute('''drop function if exists task3_3;''')
        cur.execute('''create function task3_1(salesman_number char(8), contract_num char(10), product_mod varchar)
    returns bool as
$$
begin
    if ((contract_num, product_mod) in (select o.contract_num, o.product_model
                                        from orders o
                                        where o.salesman_num = salesman_number
                                          and o.product_model = product_mod))
    then
        return true;
    else
        return false;
    end if;
end;
$$ language plpgsql;''')
        cur.execute('''create function task3_2(contract_number char(10), quant integer, product_mod varchar, s_num char(8))
    returns bool as
$$
declare
    result        integer;
    used_quantity integer;
    con_center    varchar;
    con_ent       varchar;
begin
    select o.quantity, o.enterprise
    into used_quantity, con_ent
    from orders o
    where o.contract_num = contract_number
      and o.product_model = product_mod
      and o.salesman_num = s_num;

    select en.supply_center
    into con_center
    from enterprise en
    where en.name = con_ent;

    select current_quantity
    into result --得到库存数量
    from stock
    where model = product_mod
      and center = con_center;

    if result is not null
    then
        if result + used_quantity >= quant
        then
            update stock
            set current_quantity = current_quantity + used_quantity - quant
            where model = product_mod
              and center = con_center;
            return true;
        else
            return false;
        end if;
    else
        return false;
    end if;
end;
$$ language plpgsql;''')
        cur.execute('''create function task3_3(contract_number char(10), quantity_zero integer, product_mod varchar, salesman char(8))
    returns bool as
$$
begin
    if (quantity_zero = 0)
    then
        update contracts
        set tot_order = tot_order - 1
        where contract_num = contract_number;

        delete
        from orders
        where contract_num = contract_number
          and product_model = product_mod
          and salesman_num = salesman;
        return true;
    else
        return false;
    end if;
end;
$$ language plpgsql;''')
        conn.commit()
        cur.close()
