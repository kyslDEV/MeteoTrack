CREATE DATABASE IF NOT EXISTS meteotrack
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE meteotrack;

CREATE TABLE IF NOT EXISTS weather_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(10) NOT NULL,
    country VARCHAR(80) NOT NULL,
    record_date DATE NOT NULL,
    temp_min DECIMAL(5,2) NOT NULL,
    temp_max DECIMAL(5,2) NOT NULL,
    temp_mean DECIMAL(5,2) NOT NULL,
    classification VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_weather_city_state_date (city, state, record_date)
);
