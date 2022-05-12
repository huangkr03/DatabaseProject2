from psycopg2.extensions import cursor, connection


class UpdateOrder:
    def __init__(self, conn: connection):
        self.__cur: cursor = conn.cursor()
        self.__conn = conn

    def update_data(self):
        self.__task3_create_function()
        with open('task/task34_update_test_data_publish.tsv') as task3:
            task3.readline()
            lines = task3.readlines()
            for line in lines:  # contract0 product_model1 salesman2 quantity3 estimate_delivery_date4 lodgement_date5
                line = line.rstrip('\n')
                line = line.split('\t')
                # print(line)
                self.__cur.execute("select task3_1('" + line[2] + "', '" + line[0] + "', '" + line[1] + "')")
                if self.__cur.fetchone()[0]:
                    self.__cur.execute(
                        "select task3_2('" + line[0] + "', " + line[3] + ", '" + line[1] + "', '" + line[2] + "')")
                    self.__cur.execute(
                        "select task3_3('" + line[0] + "', " + line[3] + ",'" + line[1] + "', '" + line[2] + "')")
                        # "select task3_3('" + line[0] + "', " + line[3] + ')')
                    # print(self.__cur.fetchone()[0])
        self.__conn.commit()

    def __task3_create_function(self):
        self.__cur.execute('''drop function if exists task3_1;''')
        self.__cur.execute('''drop function if exists task3_2;''')
        self.__cur.execute('''drop function if exists task3_3;''')
        self.__cur.execute('''create function task3_1(salesman_number char(8), contract_num char(10), product_mod varchar)
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
#         self.__cur.execute('''create function task3_2(contract_number char(10), quant integer, product_mod varchar, s_num char(8))
#     returns bool as
# $$
# declare
#     result        integer;
#     used_quantity integer;
#     con_center    varchar;
#     con_ent       varchar;
# begin
#     select o.quantity, o.enterprise
#     into used_quantity, con_ent
#     from orders o
#     where o.contract_num = contract_number
#       and o.product_model = product_mod
#       and o.salesman_num = s_num;
#
#     select en.supply_center
#     into con_center
#     from enterprise en
#     where en.name = con_ent;
#
#     select si.quantity
#     into result
#     from stockin si
#     where si.supply_center = con_center
#       and si.product_model = product_mod
#       and si.supply_staff = s_num;
#     update stockin
#     set current_quantity = current_quantity + used_quantity - quant
#     where supply_center = con_center
#       and product_model = product_mod
#       and supply_staff = s_num;
#     return true;
# end;
# $$ language plpgsql;''')
        self.__cur.execute('''create function task3_2(contract_number char(10), quant integer, product_mod varchar, s_num char(8))
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
        self.__cur.execute('''create function task3_3(contract_number char(10), quantity_zero integer, product_mod varchar, salesman char(8))
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
        self.__conn.commit()