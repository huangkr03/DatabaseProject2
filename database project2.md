## DB project 2

12010641 牛景萱

12012427 黄柯睿

### Bonus：

### 1.设计系统功能性需求API：

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

### 2.Index：

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

<img src="picture\without_index.png" alt="without_index" style="zoom:50%;" />

<img src="picture\expression_index.png" alt="expression_index" style="zoom:50%;" />

[^添加索引前后搜索效率]: 10.72-->7.97

<img src="picture\索引2.png" alt="索引2" style="zoom: 55%;" />

<img src="picture\索引1.png" alt="索引1" style="zoom: 50%;" />



[^添加索引前后搜索效率]: 15.61 --> 8.02

### 3.Role：

基于实际需求，除了superuser postgres以外，我们新建了以下三个Role

- 管理产品信息的product_manager：具有product表的所有权限
- 代替超级用户管理数据库的database_manager：具有创建数据库和创建用户的权限
- 管理xxx供应中心的管理员xxx_center_manager：具有该供应中心的产品库存视图以及该供应中心员工信息视图的所有权限

<img src="picture\role.png" alt="role" style="zoom:67%;" />

America_center_manager 操作示例：

<img src="picture\image-20220527111226059(1).png" alt="image-20220527111226059(1)" style="zoom: 50%;" />

### 4.前端

此次前端我们主要实现两个页面，一个是登录页面，用于用户验证，一个是数据库管理页面

以下是两个页面的截图：

login界面：

<img src="picture/login.png" alt="login" style="zoom: 80%;" />

database界面：

<img src="picture\database.png" alt="database" style="zoom: 50%;" />

在登录验证时，用户需要输入四项信息，分别是：用户名，密码，数据库以及主机地址，在用户输入正确的信息之后，后端将会连上数据库并初始化数据库连接池，以便之后使用

**前端支持的操作有**：

1. 一键导入操作
2. 一键导出操作（将查询结果保存为txt文件）
3. Q6-Q13的查询操作
4. Q12-Q13的自动补全（输入一部分字符可以自动补全其余字符）
5. 面板清空操作（只是清空前端显示，不会清空后端的查询结果）
6. 手动输入SQL语句，并将执行结果打印到工作台中（如果是select语句的话）

### 5.数据库连接池

本次数据库我们所使用的的连接池是python的DBUtils包下的PooledDB

```python
pool = PooledDB(
    creator=pg,
    mincached=1,
    maxcached=20,
    blocking=True,
    port=5432,
    database='project_2',
    user='postgres',
    password='123456',
    host='localhost',
    ping=0
)
```

初始连接设置为1，最大连接设置为20，blocking设置为True

对于单个服务器，我们也实现了缓存功能：即如果客户端反复向服务器请求同一个内容，就从缓存中读取，而不是向数据请求建立连接。缓存极大的增强了数据库处理高并发单一查询的能力。

压力测试（2000线程）：

<img src="C:\Users\Lenovo\Desktop\Project2\picture\CHCHE.png" alt="CHCHE" style="zoom:50%;" />

### 6.后端

后端支持http连接和RESTful服务，http连接用于前后端交互，RESTful服务用于一些复杂查询，然后后端利用psycopg2来连接数据库

运行成功的画面是这样：

<img src="picture\server.png" alt="server" style="zoom:80%;" />

遇到请求时处理结果如下：

<img src="picture\server2.png" alt="server2"  />

### 7.分布式设计：

#### 1. 使用PostgreSQL数据库的分布式中间件Citus

我们首先考虑使用Citus解决PostgreSQL横向扩展问题，以支持更大的数据量、更大的写入和查询性能。

我们分别在两台主机的Linux系统(wsl)上部署citus（安装citus扩展），并将添加结点位本机IP。

在各个节点上，开放5432端口。

<img src="picture\citus.png" alt="citus" style="zoom: 50%;" />

<img src="picture\hrk_citus.png" alt="hrk_citus" style="zoom: 60%;" />

由于wsl的IP是本机内IP，本机的IP又属于校园网内网IP，不是静态IP，因此要考虑部署NAT网络地址转换和端口映射。使得两台主机（服务器）能够互相通信，从而实现分布式。具体实现可以在docker中进行配置，此处我们了解概念后没有具体实现。

#### 2. 手动实现简单分布式

由于上面的那一种方式需要公网IP，或者云端服务器，并且由于我们使用的wsl所在网段是我们电脑的子网，不在校园网的子网下，因此并不能绑定校园网的IP，并且我们的校园网服务器给我们分配的ip是随时间动态改变的，切换的时候会很不方便。因此我们最终放弃了上面的那种分布式设计，我们准备手动实现我们自己的分布式。

我们的想法是另开一个proxy.py作为代理服务器，里面维护一个服务器列表，当有查询结果的时候，从服务器列表中选择一个服务器来进行查询，并返回查询结果，当需要做出改变的时候（如update，delete等），所有的服务器都需要改变。这样做的好处就是减少高并发带来的服务器压力，并且避免单个服务器宕机引起查询失败。代理服务器绑定的IP就是校园网IP，这样，只要设备和代理服务器处于同一个子网下（也就是校园网），就都可以拿来当服务器。

### 压力测试：

压力测试这部分我们使用的是Apache下的Jmeter软件来进行压力测试。软件是基于java编写的。

我们最后选择测试的线程数是：

1server（无分布式）：400线程、600线程、800线程、1000线程

2server：1000线程、1200线程、1400线程、1600线程、1800线程

#### 1server时结果如下：

400线程：

<img src="picture\400_1server.png" alt="400_1server" style="zoom:80%;" />

600线程：

<img src="picture\600_1server.png" alt="600_1server" style="zoom: 80%;" />

800线程：

<img src="picture\800_1server.png" alt="800_1server" style="zoom:80%;" />

1000线程：

<img src="picture\1000_1server.png" alt="1000_1server" style="zoom:80%;" />

可以看出，从600线程开始，服务器的处理能力就开始下降了，开始出现丢包的情况，到1000线程时，服务器已经非常卡顿，最终有34%的异常

#### 2server时结果如下：

1000线程：

<img src="picture\1000_2server.png" alt="1000_2server" style="zoom:80%;" />

1200线程：

<img src="picture\1200_2server.png" alt="1200_2server" style="zoom:80%;" />

1400线程：

<img src="picture\1400_2server.png" alt="1400_2server" style="zoom:80%;" />

1600线程：

<img src="picture\1600_2server.png" alt="1600_2server" style="zoom:80%;" />

1800线程：

<img src="picture\1800_2server.png" alt="1800_2server" style="zoom:80%;" />

可以看出，使用分布式之后，仅仅只是两个server，已经可以轻松处理1000线程不报错了。

在1200线程的时候才开始出现丢包的情况，并且在1800线程的时候也仅有15%左右的异常，并且没有明显卡顿。可以看出分布式对于查询的优化效率是成倍的增长的

以下是根据异常率画的图：

<img src="picture\压力测试.png" alt="压力测试" style="zoom: 67%;" />