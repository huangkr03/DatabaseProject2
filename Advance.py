from psycopg2.extensions import cursor


class Advance1:
    def __init__(self, pool):
        self.__pool = pool
        self.__create_function()

    def __create_function(self):
        conn = self.__pool.get_conn()
        cur: cursor = conn.cursor()
        cur.execute('drop function if exists get_enterprise_order(enterprise_name varchar);')
        cur.execute('''create function get_enterprise_order(enterprise_name varchar)
            returns table
                    (
                        product_model varchar,
                        quantity      int,
                        country       varchar,
                        city          varchar,
                        industry      varchar,
                        price         numeric,
                        total_price   numeric
                    )
        as
        $$
        begin
            RETURN QUERY
                select o.product_model           as products,
                       o.quantity                as quantity,
                       e.country                 as country,
                       e.city                    as city,
                       e.industry                as industry,
                       p.unit_price              as price,
                       p.unit_price * o.quantity as total_price
                from orders o
                         join enterprise e on o.enterprise = e.name
                         join product p on p.model = o.product_model
                where e.name = enterprise_name;
        end;
        $$ language plpgsql;''')
        cur.execute('drop function if exists get_center_stock(center_name varchar);')
        cur.execute('''create function get_center_stock(center_name varchar) --供应中心
    returns table
            (
                product     varchar,
                qt          int,
                price       numeric,
                total_price numeric
            )
as
$$
begin
    RETURN QUERY
        select s.model                                          as product,
               s.quantity - s.current_quantity                  as qt,
               p.unit_price                                     as price,
               (s.quantity - s.current_quantity) * p.unit_price as total_price
        from stock s
                 join product p on s.model = p.model
        where s.center = center_name
          and (s.quantity - s.current_quantity) <> 0;
end
$$ language plpgsql;''')
        conn.commit()
        cur.close()
        conn.close()

    def get_enterprise_order(self, enterprise_name):
        conn = self.__pool.get_conn()
        cur: cursor = conn.cursor()
        cur.execute("select * from get_enterprise_order('%s')" % enterprise_name)
        result = cur.fetchall()
        cur.close()
        conn.close()
        return result

    def get_center_stock(self, center_name):
        conn = self.__pool.get_conn()
        cur: cursor = conn.cursor()
        cur.execute("select * from get_center_stock('%s');" % center_name)
        result = cur.fetchall()
        cur.close()
        conn.close()
        return result
