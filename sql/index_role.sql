--Index
CREATE INDEX IF NOT EXISTS product_index ON project_2.public.orders USING btree(product_model);
CREATE INDEX IF NOT EXISTS salesman_index ON project_2.public.orders using btree(salesman_num);
CREATE INDEX IF NOT EXISTS manager_index ON project_2.public.orders using btree(contract_manager);
drop index if exists product_index;
drop index if exists salesman_index;
drop index if exists manager_index;
explain select salesman_num from project_2.public.orders where orders.salesman_num like '11110405';

CREATE INDEX sales_index ON staff using btree(number);
drop index sales_index;
explain select * from staff where number like '11110405';

--Role
select rolname from PG_ROLES;--show roles in pgsql
DROP ROLE product_manager;
revoke  all on project_2.public.product from product_manager;

create user product_manager with password '123456';
grant all on project_2.public.product to product_manager;
select * from information_schema.table_privileges where grantee='product_manager';  --有关于product表的所有权限
select * from information_schema.usage_privileges where grantee='product_manager' ;

--create a role 'database_manager' that has the CREATEDB and CREATEROLE privileges
create role database_manager with createdb ;
alter role database_manager with createrole ;
alter role database_manager with password '123456';
alter role database_manager with CONNECTION LIMIT 20;--连接数限制

--供应中心管理员
create role America_center_manager with createdb ;
alter role America_center_manager with createrole ;
alter role America_center_manager with password '123456';
alter role America_center_manager with CONNECTION LIMIT 8;--连接数限制
create or replace view center_view as
    select si.supply_center,si.product_model,s.quantity,s.current_quantity
    from stockin si join stock s on si.product_model = s.model
    where si.supply_center='America';
create or replace view  America_staff_view as
    select *
    from staff
    where supply_center='America';
grant all ON center_view to America_center_manager;
grant all ON America_staff_view to America_center_manager;

select * from America_staff_view;
select * from center_view;

