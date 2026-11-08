# 🚛 Smart Truck & Parking Assistant

> **KNOW WHERE YOU CAN DRIVE. KNOW WHERE YOU CAN STOP. DELIVER WITHOUT UNNECESSARY FINES.**

An intelligent mobile application that helps professional drivers and commercial transportation companies avoid parking violations, stopping violations, illegal truck routes, and costly traffic fines.

[![License](https://img.shields.io/badge/license-Proprietary-blue.svg)]()
[![Flutter](https://img.shields.io/badge/Flutter-3.47-blue.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+PostGIS-blue.svg)]()

---

## 🏗️ Architecture

```
smart-truck-parking-assistant/
├── mobile/          # Flutter mobile application (Android + iOS)
├── backend/         # FastAPI REST API backend
├── admin/           # Web administration dashboard (Phase 7)
├── infrastructure/  # Docker, scripts, deployment configs
└── docs/            # Documentation and diagrams
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Mobile** | Flutter + Dart | Cross-platform mobile app |
| **Backend** | Python + FastAPI | REST API server |
| **Database** | PostgreSQL + PostGIS | Relational + geospatial storage |
| **Maps** | Mapbox | Map tiles, routing, geocoding |
| **Notifications** | Firebase Cloud Messaging | Push notifications |
| **State Mgmt** | Riverpod | Flutter state management |
| **Auth** | JWT (Access + Refresh tokens) | Stateless authentication |

---

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** (for database and backend)
- **Flutter SDK** >= 3.10.0 (for mobile development)
- **Python** >= 3.11 (for backend development without Docker)

### 1. Clone and Configure

```bash
git clone <repository-url>
cd smart-truck-parking-assistant

# Copy environment template
cp .env.example .env
# Edit .env with your configuration
```

### 2. Start Backend Services

```bash
# Start PostgreSQL + PostGIS and FastAPI backend
docker-compose up -d

# Verify services are running
curl http://localhost:8000/api/v1/health
```

### 3. Run Database Migrations

```bash
cd backend
alembic upgrade head
```

### 4. Run Mobile App

```bash
cd mobile
flutter pub get
flutter run
```

---

## 🔧 Development

### Backend Development (without Docker)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --port 8000
```

### API Documentation

When the backend is running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Running Tests

```bash
# Backend tests
cd backend
pytest -v

# Mobile tests
cd mobile
flutter test
```

---

## 📱 Features

### Phase 1 — Foundation ✅
- [x] User registration and authentication
- [x] JWT-based auth with refresh tokens
- [x] Vehicle management (CRUD)
- [x] Role-based access control
- [x] Docker Compose development environment
- [x] Flutter app with Clean Architecture

### Phase 2 — Vehicle & Regulatory Data 🔄
- [ ] NYC Open Data integration
- [ ] Parking regulation database
- [ ] Regulatory evaluation engine
- [ ] Truck route data

### Phase 3 — Smart Map
- [ ] Interactive map with Mapbox
- [ ] Regulation overlays
- [ ] Vehicle-specific filtering

### Phase 4 — Real-Time Alerts
- [ ] GPS-based proximity warnings
- [ ] Background location monitoring
- [ ] Local notifications

### Phase 5 — Navigation & Parking
- [ ] Vehicle-specific route validation
- [ ] Parking search
- [ ] Parking timer

### Phase 6 — Fleet Management
- [ ] Company accounts
- [ ] Fleet dashboard
- [ ] Driver management

### Phase 7 — Testing & Deployment
- [ ] Comprehensive test suite
- [ ] CI/CD pipeline
- [ ] Production deployment

---

## 🌍 Data Sources

This application uses official public datasets from:

| Source | Dataset | Purpose |
|--------|---------|---------|
| NYC Open Data | Parking Regulation Locations and Signs (`xswq-wnv9`) | Parking/standing/stopping rules |
| NYC Open Data | NYC Truck Routes (`spax-mybh`) | Designated truck routes |
| NYC Open Data | Neighborhood Loading Zones (`6pjf-tf5u`) | Commercial loading areas |
| NYC Open Data | Citywide Low Bridges (`rn6h-i66u`) | Height restrictions |
| NYC Open Data | Street Closures by Block (`i6b5-j7bu`) | Temporary restrictions |
| NY State Open Data | Posted Bridges (`c4nn-gfqw`) | Weight restrictions |

Data is provided under NYC Local Law 11 of 2012 (public domain, open data).

---

## 🔐 Security

- Argon2 password hashing
- JWT with short-lived access tokens + rotating refresh tokens
- Role-based access control (RBAC)
- Input validation and sanitization
- SQL injection prevention (ORM-based queries)
- CORS configuration
- Rate limiting

---

## 📄 Environment Variables

See [`.env.example`](.env.example) for all required and optional configuration variables.

**Required for production:**
- `JWT_SECRET_KEY` — Long random secret
- `POSTGRES_PASSWORD` — Database password
- `MAPBOX_ACCESS_TOKEN` — For map functionality (Phase 3+)

---

## 📋 License

Proprietary. All rights reserved.

---

## 👥 Contributing

This is a commercial product. Contact the development team for contribution guidelines.
