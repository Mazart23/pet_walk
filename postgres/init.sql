CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    username VARCHAR(100),
    phone VARCHAR(15),
    bio TEXT,
    profile_picture_url TEXT,
    is_premium BOOLEAN DEFAULT FALSE,
    is_private BOOLEAN DEFAULT FALSE,
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS routes (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id),
    declared_distance INT,           
    real_distance INT,               
    is_avoid_green BOOLEAN,          
    is_prefer_green BOOLEAN,         
    is_include_weather BOOLEAN,      
    route geometry(LINESTRING, 4326),
    `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);