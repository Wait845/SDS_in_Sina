create table user(
    id char(11) not null ,
    name varchar(128) not null ,
    location varchar(64) ,
    gender char(1) ,
    follower_count int ,
    friends_count int ,
    create_at timestamp ,
    finish boolean default false ,
    push_time varchar(10) not null ,
    primary key (id)
);