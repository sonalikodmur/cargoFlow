# Predictive Supply Chain Disruption Detection and Route Optimization

Production-ready demo web application built with Flask, Bootstrap, JavaScript, and SQLite (MySQL-ready config).

## 1) Folder Structure

```text
supplychain/
|-- app.py
|-- requirements.txt
|-- schema.sql
|-- .env.example
|-- README.md
|-- app/
|   |-- __init__.py
|   |-- models.py
|   |-- seed.py
|   |-- utils.py
|   |-- routes/
|   |   |-- __init__.py
|   |   |-- auth.py
|   |   |-- main.py
|   |   |-- api.py
|   |   |-- rest.py
|   |-- services/
|   |   |-- __init__.py
|   |   |-- risk_engine.py
|   |   |-- route_optimizer.py
|   |-- templates/
|   |   |-- base.html
|   |   |-- index.html
|   |   |-- login.html
|   |   |-- register.html
|   |   |-- dashboard.html
|   |   |-- tracking.html
|   |-- static/
|       |-- css/
|       |   |-- styles.css
|       |-- js/
|           |-- dashboard.js
|           |-- tracking.js
```

## 2) Features Implemented

- Authentication: signup/login/logout with role support (`admin`/`user`) and secure password hashing.
- Dashboard: total shipments, active shipments, delayed shipments, high-risk alerts.
- Shipment Tracking: Leaflet + OpenStreetMap marker plotting with current shipment location and status (free, no autopay).
- Risk Detection: rule-based logic using weather + traffic + delay trends.
- Route Optimization: current route vs optimized route suggestion.
- Alerts: near real-time alert polling on dashboard (`/alerts` endpoint).
- REST Endpoints: `/login`, `/register`, `/shipments`, `/alerts` plus `/api/*` endpoints.
- Sample Data: auto-seeded users, shipments, and alerts on first app run.

## 3) API Endpoints

- `POST /login` - Login via form or JSON payload.
- `POST /register` - Register via form or JSON payload.
- `GET /shipments` - Shipment list with risk percentage and route recommendation.
- `GET /alerts` - Latest operational alerts.
- `GET /api/dashboard` - Dashboard card data.
- `GET /api/shipments` - API namespaced shipments data.
- `GET /api/alerts` - API namespaced alert feed.

## 4) Database Schema

Tables created:
- `users (id, name, email, password, role)`
- `shipments (id, source, destination, status, location, risk_level, ...)`
- `alerts (id, shipment_id, message, timestamp, alert_type)`

`schema.sql` is included for reference. Application auto-creates schema through SQLAlchemy.

## 5) Setup Instructions

### Step 1: Create and activate virtual environment

Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Step 2: Install dependencies

```powershell
pip install -r requirements.txt
```

### Step 3: Configure environment variables

```powershell
copy .env.example .env
```

Update `.env` values:
- `SECRET_KEY`
- `DATABASE_URL` (`sqlite:///supplychain.db` for demo)
- `GOOGLE_MAPS_API_KEY` (`NOT_REQUIRED` when using Leaflet/OpenStreetMap)
- `WEATHER_API_KEY` (`NOT_REQUIRED` when using Open-Meteo style free integration)

### Step 4: Run the Flask server

```powershell
python app.py
```

Open in browser:
- `http://127.0.0.1:5000`

## 6) Free API Choice (No Autopay Required)

- Map provider: OpenStreetMap tiles through Leaflet CDN.
- Weather provider recommendation: Open-Meteo (no key required for basic forecasts).
- Your current app now runs map tracking without Google billing setup.

## 7) Demo Accounts

- Admin: `admin@supplychain.com` / `admin123`
- User: `user@supplychain.com` / `user123`

## 8) MySQL Support (Optional)

To use MySQL, set:

```env
DATABASE_URL=mysql+pymysql://username:password@localhost/supplychain_db
```

Then install driver:

```powershell
pip install pymysql
```
