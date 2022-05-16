from psycopg2.extensions import cursor, connection


class SelectItem:
    def __init__(self, conn: connection):
        self.__cur: cursor = conn.cursor()
        self.__conn = conn

    def getAllStaffCount(self):
        self.__cur.execute('''select type staff_type, count(type)
from staff
group by type;''')
        return self.__cur.fetchall()

    def getContractCount(self):
        self.__cur.execute('''select count(contract_num)
from contracts;''')
        return self.__cur.fetchall()

    def getOrderCount(self):
        self.__cur.execute('''select count(*)
from orders;''')
        return self.__cur.fetchall()

    def getNeverSoldProductCount(self):
        self.__cur.execute('''with a as (select distinct model
           from stock
           where quantity <> current_quantity
             and quantity > 0)
select (select count(distinct model) from stock) - count(*)
from a;''')
        return self.__cur.fetchall()

    def getFavoriteProductModel(self):
        self.__cur.execute('''with a as (select model, quantity, current_quantity, max(quantity - current_quantity) over () max
           from stock)
select model model_name, max as quantity
from a
where quantity - current_quantity = max;''')
        return self.__cur.fetchall()

    def getAvgStockByCenter(self):
        self.__cur.execute('''select center, round(avg(current_quantity), 1) average
from stock
group by center
order by center;''')
        return self.__cur.fetchall()

    def getProductByNumber(self, product_num: str):
        self.__cur.execute("""select s.supply_center, p.number product_number, s.product_model, s.purchase_price, s2.current_quantity
from stockIn s
         join product p on s.product_model = p.model join stock s2 on s.product_model = s2.model
where p.number = '""" + product_num + "';")
        return self.__cur.fetchall()

    def getContractInfo(self, contract_num: str):
        self.__cur.execute("""select distinct c.contract_num as number, s.name as manager, c.enterprise, e.supply_center
from contracts c
         join enterprise e on e.name = c.enterprise
         join staff s on s.number = c.manager
where c.contract_num = '""" + contract_num + "';")
        a = self.__cur.fetchone()
        self.__cur.execute("""select o.product_model, s.name salesman, quantity, p.unit_price, o.estimate_delivery_date, o.lodgement_date
from orders o
         join staff s on o.salesman_num = s.number
         join product p on p.model = o.product_model
where o.contract_num = '""" + contract_num + "';")
        b = self.__cur.fetchall()
        return a, b
