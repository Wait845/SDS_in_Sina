create table relation (
    s_id char(11) not null ,
    s_name varchar(128) not null ,
    d_id char(11) not null ,
    d_name varchar(128) not null,
    relation int not null ,
    primary key (s_id, d_id, relation)
);