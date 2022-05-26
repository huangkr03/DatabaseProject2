--Index
CREATE INDEX product_index ON project_2.public.orders USING btree(product_model);--btree performs better on text fuzzy matching
CREATE INDEX salesman_index ON project_2.public.orders using hash(salesman_num); --hash applicable to equivalent matching
CREATE INDEX manager_index ON project_2.public.orders using hash(contract_manager);--hash applicable to equivalent matching
--TEST
explain select * from project_2.public.orders where orders.salesman_num = '11110405';
explain select * from  project_2.public.orders where product_model like 'Photo%';
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
create role America_center_manager with createdb ;
alter role America_center_manager with createrole ;
alter role America_center_manager with password '123456';
alter role America_center_manager with CONNECTION LIMIT 8;-- Connection number limit
    --center_view
create or replace view center_view as
    select si.supply_center,si.product_model,s.quantity,s.current_quantity
    from stockin si join stock s on si.product_model = s.model
    where si.supply_center='America';
    --America_staff_view
create or replace view  America_staff_view as
    select *
    from staff
    where supply_center='America';
--grant
grant all ON center_view to America_center_manager;
grant all ON America_staff_view to America_center_manager;

select * from America_staff_view;
select * from center_view;

--DROP
drop view America_staff_view;
drop view center_view;


ALTER USER postgres with password '123456';
revoke all on project_2.public.product from product_manager;


