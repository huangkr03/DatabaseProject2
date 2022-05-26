--index
CREATE INDEX product_index ON project_2.public.orders USING btree(product_model);
CREATE INDEX salesman_index ON project_2.public.orders using btree(salesman_num);
CREATE INDEX manager_index ON project_2.public.orders using btree(contract_manager);
drop index product_index;
drop index salesman_index;
explain select * from project_2.public.orders where orders.salesman_num like '11110405';

CREATE INDEX sales_index ON staff using btree(number);
drop index sales_index;
explain select * from staff where number like '11110405';

--Role
select rolname from PG_ROLES;--show roles in pgsql
DROP ROLE product_manager;
select * from information_schema.table_privileges where grantee='product_manager';  --有关于product表的所有权限
select * from information_schema.usage_privileges where grantee='product_manager' ;

--create a role 'database_manager' that has the CREATEDB and CREATEROLE privileges
create role database_manager with createdb ;
alter role database_manager with createrole ;
alter role database_manager with password '123456';
alter role database_manager with CONNECTION LIMIT 20;--连接数限制

--供应中心管理员
create role center_manager with createdb ;
alter role center_manager with createrole ;
alter role center_manager with password '123456';
alter role center_manager with CONNECTION LIMIT 8;--连接数限制
create view center_view as
    select si.supply_center,si.product_model,s.quantity,s.current_quantity
    from stockin si join stock s on si.product_model = s.model;
select * from center_view;
grant all ON center_view to center_manager;