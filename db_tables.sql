CREATE TABLE IF NOT EXISTS users (
    user_id serial PRIMARY KEY,
    nickname varchar(30) UNIQUE NOT NULL,
    first_name varchar(30) NOT NULL,
    last_name varchar(30) NOT NULL,
    user_pic text,
    email text UNIQUE NOT NULL,
    password text NOT NULL,
    friends text[],
    spot_photos text[],
    added_spots text[],
    favourite_spots text[],
    premium_account_type boolean NOT NULL DEFAULT FALSE,
    disabled boolean NOT NULL DEFAULT FALSE,
    created_at timestamp NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS spots (
    spot_id serial PRIMARY KEY,
    spot_name varchar(30),
    spot_pic varchar(50),
    spot_photos text[],
    spot_country varchar(20),
    spot_city varchar(20),
    spot_street varchar(30),
    spot_street_number varchar(10),
    spot_full_address text,
    spot_description text,
    spot_raiting double precision,
    comment text[],
    sport_type varchar(20) NOT NULL DEFAULT 'skateboarding',
    latitude double precision NOT NULL,
    longitude double precision NOT NULL,
    owner_id integer NOT NULL REFERENCES users(user_id),
    created_at timestamp NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS comments (
    comment_id serial PRIMARY KEY,
    body text NOT NULL,
    created_at timestamp NOT NULL DEFAULT now(),
    owner_id integer NOT NULL REFERENCES users(user_id),
    spot_id integer NOT NULL REFERENCES spots(spot_id) ON DELETE CASCADE
);