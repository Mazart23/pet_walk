CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    username VARCHAR(100),
    phone VARCHAR(15),
    avatar_url TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE TABLE IF NOT EXISTS routes (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id),
    declared_distance INT,           
    real_distance INT,               
    is_avoid_green BOOLEAN,          
    is_prefer_green BOOLEAN,         
    is_include_weather BOOLEAN,      
    route geometry(LINESTRING, 4326) 
);