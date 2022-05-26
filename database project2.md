### 设计系统功能性需求API：

1. 基于实际需求，我们设计的function有：

- get_enterprise_order ：检索查看某个客户公司的所有订单，便于分析客户需求，为客户提供更好的服务。
- get_center_stock：检索查看某个供应中心产品的型号，库存，售价和销售总额，以便供应中心及时补货、调整售价。

2. 我们还设计了一个trigger：

- contract_type_trigger：在向订单表orders中插入订单记录时，根据 *estimate_delivery_date，lodgement_date* 和当前系统时间 *current_date* 自动补全订单状态：finished / unfinished.

3. 考虑到公司需要根据市场和行情动态调整上市产品，我们设计了**更改**或**删除** product表的 trigger：

```postgresql
create trigger product_update_trigger
    before update
    on project_2.public.product
    for each row
execute procedure product_check();

create trigger product_delete_trigger
    before delete
    on project_2.public.product
    for each row
    execute procedure product_delete_check();
```

- product_update_check()：保证更改product表中产品信息时，同步更新后信息到订单、库存等表。
- product_delete_check()：保证删除某个product，同时删除库存等表中的产品信息。



### Index：

​	Ⅰ. 我们尝试对orders的product_model，contract_manager 和 salesman_num列建立索引，原因如下：

1. product 和 staff 是给定情形中的"基础表"，较少涉及更改操作且较频繁地作为查询条件。

2. orders表是staff表和product表的从表。orders表的product_model，contract_manager 和 salesman_num列是外键列。

   > 如果从表没有包含外键列的索引，SQL 服务器需要扫描整个从表。从表越大，删除更新等操作的时间越长。且在高并发情形下容易造成阻塞。如果主表有唯一聚集或非聚集的索引，在从表中插入或修改时，能利用主表的索引快速定位。

3. orders中的每一条订单，一但形成并添加订单信息后，在现实情况下不易涉及更新操作。

```postgresql
--btree 对文本模糊匹配表现更好
CREATE INDEX product_index ON project_2.public.orders USING btree(product_model);
explain select * from  project_2.public.orders where product_model like 'Photo%';
--hash 适用于等值匹配
CREATE INDEX salesman_index ON project_2.public.orders using hash(salesman_num); 
CREATE INDEX manager_index ON project_2.public.orders using hash(contract_manager);
explain select * from project_2.public.orders where orders.salesman_num = '11110405';
```

Ⅱ. 对于stock表，建立表达式索引，更便于根据销售数量搜索产品。

```postgresql
CREATE INDEX sales_num_index ON stock ((stock.quantity-stock.current_quantity));
explain select * from  stock where stock.quantity-stock.current_quantity between 0 and 10;
```

<img src="C:\Users\Lenovo\Desktop\Project2\picture\without_index.png" alt="without_index" style="zoom:50%;" />

<img src="C:\Users\Lenovo\Desktop\Project2\picture\expression_index.png" alt="expression_index" style="zoom:50%;" />

[^添加索引前后搜索效率]: 10.72-->7.97



### Role：

基于实际需求，除了superuser postgres以外，我们新建了以下三个Role

- 管理产品信息的product_manager：具有product表的所有权限
- 代替超级用户管理数据库的database_manager：具有创建数据库和创建用户的权限
- 管理xxx供应中心的管理员xxx_center_manager：具有该供应中心的产品库存视图以及该供应中心员工信息视图的所有权限

<img src="C:\Users\Lenovo\Desktop\Project2\picture\role.png" alt="role" style="zoom:67%;" />



### 分布式设计：

#### 1. 使用PostgreSQL数据库的分布式中间件Citus

我们首先考虑使用Citus解决PostgreSQL横向扩展问题，以支持更大的数据量、更大的写入和查询性能。

我们分别在两台主机的Linux系统(wsl)上部署citus（安装citus扩展），并将添加结点位本机IP。

在各个节点上，开放5432端口。

<img src="C:\Users\Lenovo\Desktop\Project2\picture\citus.png" alt="citus" style="zoom: 50%;" />

<img src="C:\Users\Lenovo\Desktop\Project2\picture\hrk_citus.png" alt="hrk_citus" style="zoom: 60%;" />

由于wsl的IP是本机内IP，本机的IP又属于校园网内网IP，不是静态IP，因此要考虑部署NAT网络地址转换和端口映射。使得两台主机（服务器）能够互相通信，从而实现分布式。具体实现可以在docker中进行配置，此处我们了解概念后没有具体实现。