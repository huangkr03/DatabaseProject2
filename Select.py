class SelectItem:
    def __init__(self, pool):
        self.__pool = pool

    def getAllStaffCount(self):
        conn = self.__pool.get_conn()
        cur = conn.cursor()
        cur.execute('''select type staff_type, count(type)
from staff
group by type;''')
        result = cur.fetchall()
        cur.close()
        conn.close()
        return result

    def getContractCount(self):
        conn = self.__pool.get_conn()
        cur = conn.cursor()
        cur.execute('''select count(contract_num)
from contracts;''')
        result = cur.fetchall()
        cur.close()
        conn.close()
        return result

    def getOrderCount(self):
        conn = self.__pool.get_conn()
        cur = conn.cursor()
        cur.execute('''select count(*)
from orders;''')
        result = cur.fetchall()
        cur.close()
        conn.close()
        return result

    def getNeverSoldProductCount(self):
        conn = self.__pool.get_conn()
        cur = conn.cursor()
        cur.execute('''with a as (select distinct model
           from stock
           where quantity <> current_quantity
             and quantity > 0)
select (select count(distinct model) from stock) - count(*)
from a;''')
        result = cur.fetchall()
        cur.close()
        conn.close()
        return result

    def getFavoriteProductModel(self):
        conn = self.__pool.get_conn()
        cur = conn.cursor()
        cur.execute('''with a as (select model, quantity, current_quantity, max(quantity - current_quantity) over () max
           from stock)
select model model_name, max as quantity
from a
where quantity - current_quantity = max;''')
        result = cur.fetchall()
        cur.close()
        conn.close()
        return result

    def getAvgStockByCenter(self):
        conn = self.__pool.get_conn()
        cur = conn.cursor()
        cur.execute('''select center, round(avg(current_quantity), 1) average
from stock
group by center
order by center;''')
        result = cur.fetchall()
        cur.close()
        conn.close()
        return result

    def getProductByNumber(self, product_num: str):
        conn = self.__pool.get_conn()
        cur = conn.cursor()
        cur.execute("""select s.supply_center, p.number product_number, s.product_model, s.purchase_price, s2.current_quantity
from stockIn s
         join product p on s.product_model = p.model join stock s2 on s.product_model = s2.model
where p.number = '""" + product_num + "';")
        result = cur.fetchall()
        cur.close()
        conn.close()
        return result

    def getContractInfo(self, contract_num: str):
        conn = self.__pool.get_conn()
        cur = conn.cursor()
        cur.execute("""select distinct c.contract_num as number, s.name as manager, c.enterprise, e.supply_center
from contracts c
         join enterprise e on e.name = c.enterprise
         join staff s on s.number = c.manager
where c.contract_num = '""" + contract_num + "';")
        a = cur.fetchone()
        cur.execute("""select o.product_model, s.name salesman, quantity, p.unit_price, o.estimate_delivery_date, o.lodgement_date
from orders o
         join staff s on o.salesman_num = s.number
         join product p on p.model = o.product_model
where o.contract_num = '""" + contract_num + "';")
        b = cur.fetchall()
        cur.close()
        conn.close()
        return a, b
