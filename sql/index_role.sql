--Index
CREATE INDEX product_index ON project_2.public.orders USING btree(product_model);--btree对文本模糊匹配表现更好
CREATE INDEX salesman_index ON project_2.public.orders using hash(salesman_num); --hash 适用于等值匹配
CREATE INDEX manager_index ON project_2.public.orders using hash(contract_manager);--hash 适用于等值匹配
--TEST
explain select * from project_2.public.orders where orders.salesman_num = '11110405';
explain select * from  project_2.public.orders where product_model = 'Cabinet07';

--Expression index: Find the total sales of a product
CREATE INDEX sales_num_index ON stock ((stock.quantity-stock.current_quantity));
--TEST
explain select * from  stock where stock.quantity-stock.current_quantity between 0 and 10;
--DROP
drop index sales_num_index;
drop index product_index;
drop index salesman_index;
drop index manager_index;

--Role
--show roles in pgsql
select rolname from PG_ROLES;
--product_manager
create user product_manager with password '123456';
grant all on project_2.public.product to product_manager;
select * from information_schema.table_privileges where grantee='product_manager'; --Check the privilege
--create a role 'database_manager' that has the CREATEDB and CREATEROLE privileges
create role database_manager with createdb ;
alter role database_manager with createrole ;
alter role database_manager with password '123456';
alter role database_manager with CONNECTION LIMIT 20;-- Connection number limit
--center_manager: Take America as an example
create user america_center_manager with createdb ;
alter user america_center_manager with createrole ;
alter user america_center_manager with password '123456';
alter user america_center_manager with CONNECTION LIMIT 8;--连接数限制
create or replace view center_view as
    select si.supply_center,si.product_model,s.quantity,s.current_quantity
    from stockin si join stock s on si.product_model = s.model
    where si.supply_center='America';
create or replace view  america_staff_view as
    select *
    from staff
    where supply_center='America';
grant all ON center_view to america_center_manager;
grant all ON america_staff_view to america_center_manager;

select * from america_staff_view;
select * from center_view;
drop view america_staff_view;
DROP VIEW center_view;
--REVOKE & DROP
revoke  all on center_view from america_center_manager;
revoke  all on america_staff_view from america_center_manager;
drop user america_center_manager;

ALTER USER postgres with password '123456';

