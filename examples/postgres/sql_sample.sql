-- this is a sample script for postgres.
--
-- if postgres version is >= 8.2.3 
-- you can remove the WITH OIDS clause and
-- set MOTHER_OIDS = False on the Mother 
-- configuration file.
--
-- if your postgres version is < 8.1 you
-- can remove WITH OIDS from your tables, but you 
-- have to set MOTHER_OIDS = True.
--
-- Otherwise use WITH_OIDS and set MOTHER_OIDS
-- to True
--
-- Note that updating postgres is not critical for
-- mother: just follow the previous advices.

create table stars (
    star_id         serial,
    star_name       text,
    star_age        int,
    star_mass       int,

    primary key(star_id)
) WITH OIDS;

create table planets (
    star_id         int,
    planet_id       serial,
    planet_name     text,
    planet_mass     int,

    primary key(planet_id),
    foreign key(star_id) references stars(star_id)
) WITH OIDS;

create table moons_info (
    planet_id       int,
    moon_info_id    serial,
    num_moons       int,

    primary key(moon_info_id),
    foreign key(planet_id) references planets(planet_id)
) WITH OIDS;

create table lifeforms (
    life_id         serial,
    life_name       text,
    life_age        int,

    primary key(life_id)
) WITH OIDS;

create table civilizations (
    life_id         int,
    planet_id       int,
    age             int,

    foreign key(life_id) references lifeforms(life_id),
    foreign key(planet_id) references planets(planet_id)
) WITH OIDS;
