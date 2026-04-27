-- Database schema for Predictive Supply Chain System.

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS shipments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source VARCHAR(120) NOT NULL,
    destination VARCHAR(120) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'On-time',
    location VARCHAR(120) NOT NULL,
    risk_level VARCHAR(20) NOT NULL DEFAULT 'Low',
    current_lat REAL NOT NULL,
    current_lng REAL NOT NULL,
    destination_lat REAL NOT NULL,
    destination_lng REAL NOT NULL,
    weather_condition VARCHAR(30) NOT NULL DEFAULT 'clear',
    traffic_level VARCHAR(30) NOT NULL DEFAULT 'light',
    eta_delay_minutes INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shipment_id INTEGER NOT NULL,
    message VARCHAR(255) NOT NULL,
    timestamp DATETIME NOT NULL,
    alert_type VARCHAR(30) NOT NULL DEFAULT 'Delay alert',
    FOREIGN KEY (shipment_id) REFERENCES shipments(id)
);
