create table stars (
    star_id         integer,
    star_name       text,
    star_age        integer,
    star_mass       integer,

    primary key(star_id)
) ;

create table planets (
    star_id         integer,
    planet_id       integer,
    planet_name     text,
    planet_mass     integer,

    primary key(planet_id),
    foreign key(star_id) references stars(star_id)
) ;

create table moons_info (
    planet_id       integer,
    moon_info_id    integer,
    num_moons       integer,

    primary key(moon_info_id),
    foreign key(planet_id) references planets(planet_id)
) ;

create table lifes (
    life_id         integer,
    life_name       text,
    life_age        integer,

    primary key(life_id)
) ;

create table civilizations (
    life_id         integer,
    planet_id       integer,
    age             integer,

    foreign key(life_id) references lifes(life_id),
    foreign key(planet_id) references planets(planet_id)
)
