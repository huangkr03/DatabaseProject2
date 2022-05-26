--删改product 表
create or replace function product_check()
    returns trigger
as
$$
declare
    max int;
begin
    select max(id) into max from project_2.public.product;
    insert into project_2.public.product values (max + 1, new.number, new.model, new.name, new.unit_price);

    update stock s
    set model=new.model
    where s.model = old.model;

    update stockin si
    set product_model=new.model
    where si.product_model = old.model;

    update project_2.public.orders o
    set product_model = new.model
    where o.product_model = old.model;

    return null;

end
$$ language plpgsql;

create trigger product_update_trigger
    before update
    on project_2.public.product
    for each row
execute procedure product_check();

drop trigger product_update_trigger on project_2.public.product;

alter table project_2.public.product
    disable trigger all;
alter table project_2.public.product
    enable trigger all;
UPDATE project_2.public.product
SET model= 'AttendanceMachineW2'
where model = 'AttendanceMachineW1';

create or replace function product_delete_check()
    returns trigger
as
$$
begin
    delete
    from stock s
    where s.model = old.model;

    delete
    from stockin si
    where si.product_model = old.model;

    delete
    from project_2.public.orders o
    where o.product_model = old.model;

    return new;
end
$$ language plpgsql;

create trigger product_delete_trigger
    before delete
    on project_2.public.product
    for each row
execute procedure product_delete_check();

drop trigger product_delete_trigger on project_2.public.product;

delete
from project_2.public.product
where model = 'AttendanceMachineW1';