--1 get_enterprise_order
create function get_enterprise_order (enterprise_name varchar)
returns table (product_model varchar,quantity int, country varchar,city varchar,industry varchar,price numeric,total_price numeric)as
$$
begin
    RETURN QUERY
    select o.product_model products,o.quantity quantity,e.country country ,e.city city,e.industry industry,p.unit_price price, p.unit_price*o.quantity total_price
    from orders o join enterprise e on o.enterprise=e.name join product p on  p.model=o.product_model
    where e.name=enterprise_name
    ;
end;
$$ language plpgsql;

drop function get_enterprise_order(enterprise_name varchar);

select * from get_enterprise_order('Rwe Group');

--2 get_center_stock
create function get_center_stock (center_name varchar) --供应中心
returns table (product varchar,inventory int,price numeric,total_price numeric)as
$$
begin
    RETURN QUERY
    select s.model product, s.quantity-s.current_quantity inventory,p.unit_price price,(s.quantity-s.current_quantity)*p.unit_price total_price
    from stock s join product p on s.model = p.model
    where s.center=center_name
    ;
end;
$$ language plpgsql;

drop function get_center_stock(center_name varchar);
select * from get_center_stock('Asia');

--3 type_check
create or replace function type_check()
returns trigger
as
$$

begin
    if new.estimate_delivery_date=new.lodgement_date then
        select 'Finished' into new.contract_type;
    elseif new.estimate_delivery_date<new.lodgement_date then
        select 'Delay' into new.contract_type;
    elseif new.estimate_delivery_date>current_date then
        select 'Unfinished' into new.contract_type;
    else
    select 'none'into new.contract_type;
    end if;
    return new;
end
$$ language plpgsql;

create trigger contract_type_trigger
 before insert
 on project_2.public.orders
 for each row
 execute procedure type_check();

insert into project_2.public.orders(contract_num, enterprise, product_model, quantity, contract_manager, contract_date, estimate_delivery_date, salesman_num) values ('CSE0000101','ENI','DisplayChipB4',0,'12011529','2022-01-06','2022-05-22','11911204')

