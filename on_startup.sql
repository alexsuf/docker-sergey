create table dataflow(
    flow_id varchar(60) primary key
    ,flow_name varchar(128)
    ,flow_env varchar(60) default 'dev'
    ,flow_type varchar(60) default 'spark'
    ,driver_memory varchar(60) default '1g'
    ,executor_memory varchar(60) default '1g'
    ,executor_instances int default 2
    ,spark_master varchar(60) default 'local[1]'
    ,constraint uq_dataflow unique(flow_name, flow_env)
);

create table if not exists public.customers
(
    customer_id   varchar(5)  not null
        constraint pk_customers
            primary key,
    company_name  varchar(40) not null,
    contact_name  varchar(30),
    contact_title varchar(30),
    address       varchar(60),
    city          varchar(15),
    region        varchar(15),
    postal_code   varchar(10),
    country       varchar(15),
    phone         varchar(24),
    fax           varchar(24)
);

create table dataobject(
    object_name varchar(256)
    ,schema_name varchar(60)
    ,flow_id varchar(60)
    ,direction varchar(60) default 'source'
    ,driver_type varchar(60) default 'jdbc'
    ,db_type varchar(60) default 'postgres'
    ,host varchar(256)
    ,port int
    ,database_name varchar(60)
    ,user_name varchar(60)
    ,constraint uq_dataobject unique(object_name, schema_name, flow_id)
    ,constraint fk_flow_id foreign key(flow_id) references dataflow(flow_id)
);

INSERT INTO public.dataflow (flow_id, flow_name, flow_env, flow_type, driver_memory, executor_memory, executor_instances, spark_master)
VALUES ('cutsrv_rtim_dev', 'cutsrv_rtim_dev', 'dev', 'spark', '256M', '256M', 2, 'local[1]');
INSERT INTO public.dataflow (flow_id, flow_name, flow_env, flow_type, driver_memory, executor_memory, executor_instances, spark_master) 
VALUES ('cutsrv_rtim_prod', 'cutsrv_rtim_prod', 'prod', 'spark', '2g', '2g', 4, 'yarn');

INSERT INTO public.dataobject (object_name, schema_name, flow_id, direction, driver_type, db_type, host, port, database_name, user_name, user_pass) 
VALUES ('customers', 'public', 'cutsrv_rtim_dev', 'source', 'jdbc', 'postgres', 'localhost', 1111, 'postgres', 'postgres', 'secret');

INSERT INTO public.customers (customer_id, company_name, contact_name, contact_title, address, city, region, postal_code, country, phone, fax) VALUES ('ALFKI', 'Alfreds Futterkiste', 'Maria Anders', 'Sales Representative', 'Obere Str. 57', 'Berlin', null, '12209', 'Germany', '030-0074321', '030-0076545');
INSERT INTO public.customers (customer_id, company_name, contact_name, contact_title, address, city, region, postal_code, country, phone, fax) VALUES ('ANATR', 'Ana Trujillo Emparedados y helados', 'Ana Trujillo', 'Owner', 'Avda. de la Constitución 2222', 'México D.F.', null, '05021', 'Mexico', '(5) 555-4729', '(5) 555-3745');
INSERT INTO public.customers (customer_id, company_name, contact_name, contact_title, address, city, region, postal_code, country, phone, fax) VALUES ('ANTON', 'Antonio Moreno Taquería', 'Antonio Moreno', 'Owner', 'Mataderos  2312', 'México D.F.', null, '05023', 'Mexico', '(5) 555-3932', null);
INSERT INTO public.customers (customer_id, company_name, contact_name, contact_title, address, city, region, postal_code, country, phone, fax) VALUES ('AROUT', 'Around the Horn', 'Thomas Hardy', 'Sales Representative', '120 Hanover Sq.', 'London', null, 'WA1 1DP', 'UK', '(171) 555-7788', '(171) 555-6750');
INSERT INTO public.customers (customer_id, company_name, contact_name, contact_title, address, city, region, postal_code, country, phone, fax) VALUES ('BERGS', 'Berglunds snabbköp', 'Christina Berglund', 'Order Administrator', 'Berguvsvägen  8', 'Luleå', null, 'S-958 22', 'Sweden', '0921-12 34 65', '0921-12 34 67');
INSERT INTO public.customers (customer_id, company_name, contact_name, contact_title, address, city, region, postal_code, country, phone, fax) VALUES ('BLAUS', 'Blauer See Delikatessen', 'Hanna Moos', 'Sales Representative', 'Forsterstr. 57', 'Mannheim', null, '68306', 'Germany', '0621-08460', '0621-08924');
INSERT INTO public.customers (customer_id, company_name, contact_name, contact_title, address, city, region, postal_code, country, phone, fax) VALUES ('BLONP', 'Blondesddsl père et fils', 'Frédérique Citeaux', 'Marketing Manager', '24, place Kléber', 'Strasbourg', null, '67000', 'France', '88.60.15.31', '88.60.15.32');
INSERT INTO public.customers (customer_id, company_name, contact_name, contact_title, address, city, region, postal_code, country, phone, fax) VALUES ('BOLID', 'Bólido Comidas preparadas', 'Martín Sommer', 'Owner', 'C/ Araquil, 67', 'Madrid', null, '28023', 'Spain', '(91) 555 22 82', '(91) 555 91 99');
INSERT INTO public.customers (customer_id, company_name, contact_name, contact_title, address, city, region, postal_code, country, phone, fax) VALUES ('BONAP', 'Bon app''', 'Laurence Lebihan', 'Owner', '12, rue des Bouchers', 'Marseille', null, '13008', 'France', '91.24.45.40', '91.24.45.41');
INSERT INTO public.customers (customer_id, company_name, contact_name, contact_title, address, city, region, postal_code, country, phone, fax) VALUES ('BOTTM', 'Bottom-Dollar Markets', 'Elizabeth Lincoln', 'Accounting Manager', '23 Tsawassen Blvd.', 'Tsawassen', 'BC', 'T2F 8M4', 'Canada', '(604) 555-4729', '(604) 555-3745');