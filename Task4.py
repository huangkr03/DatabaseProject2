from psycopg2.extensions import cursor, connection


class DeleteOrder:
    def __init__(self, conn: connection):
        self.__cur: cursor = conn.cursor()
        self.__conn = conn

    def delete_data(self):
        self.__task4_create_function()
        with open('task/task34_delete_test_data_publish.tsv') as task4:
            task4.readline()
            lines = task4.readlines()
            for line in lines:  # contract0 salesman1 seq2
                line = line.rstrip('\n')
                line = line.split('\t')
                # print(line)
                self.__cur.execute("select task4('" + line[0] + "', '" + line[1] + "', " + line[2] + ")")
                # print(self.__cur.fetchone()[0])
        self.__conn.commit()

    def __task4_create_function(self):
        self.__cur.execute('drop function if exists task4;')
#         self.__cur.execute('''create function task4(contract_numbers char(10), salesman_numbers char(8), seq integer)
#     returns bool as
# $$
# declare
#     result    integer;
#     salesman  char(8);
#     stock_num integer;
#     contract  char(10);
#     product   varchar;
# begin
#     with a as (
#         select o.id, row_number() over (order by o.estimate_delivery_date, o.contract_num) row_num
#         from orders o
#         where o.contract_num = contract_numbers
#           and o.salesman_num = salesman_numbers
#         order by o.estimate_delivery_date,
#                  o.product_model)
#     select a.id
#     into result
#     from a
#     where row_num = seq;
#
#     select o.salesman_num, o.quantity, o.contract_num, o.product_model
#     into salesman,stock_num,contract,product
#     from orders o
#     where o.id = result;
#
#     if (salesman = salesman_numbers)
#     then
#         delete
#         from orders
#         where id = result;
#
#         update stockin
#         set current_quantity = current_quantity + stock_num
#         where product_model = product
#           and supply_staff = salesman;
#
#         update contracts
#         set tot_order=tot_order - 1
#         where contract_num = contract;
#
#         return true;
#     else
#         return false;
#     end if;
# end;
# $$ language plpgsql;''')
        self.__cur.execute('''create function task4(contract_numbers char(10), salesman_numbers char(8), seq integer)
    returns bool as
$$
declare
    result      integer;
    salesman    char(8);
    stock_num   integer;
    contract    char(10);
    product_mod varchar;
    enp         varchar;
    center_name varchar;
begin
    with a as (
        select o.id, row_number() over (order by o.estimate_delivery_date, o.contract_num) row_num
        from orders o
        where o.contract_num = contract_numbers
          and o.salesman_num = salesman_numbers
        order by o.estimate_delivery_date,
                 o.product_model)
    select a.id
    into result --待删除订单的id
    from a
    where row_num = seq;

    select o.salesman_num, o.quantity, o.contract_num, o.product_model, o.enterprise
    into salesman,stock_num,contract,product_mod, enp
    from orders o
    where o.id = result;

    select supply_center
    into center_name
    from enterprise
    where name = enp;

    if (salesman = salesman_numbers)
    then
        delete
        from orders
        where id = result;

        update stock
        set current_quantity = current_quantity + stock_num
        where model = product_mod
          and center = center_name;

        update contracts
        set tot_order=tot_order - 1
        where contract_num = contract;

        return true;
    else
        return false;
    end if;
end;
$$ language plpgsql;''')
        self.__conn.commit()
