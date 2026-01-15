# 📈 Crypto Trading Simulator

A full-stack paper trading platform for cryptocurrencies with real-time price data from Binance.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6?logo=typescript)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)

---

## ✨ Features

- **Real-time cryptocurrency prices** from Binance API
- **Paper trading** - practice trading without risking real money
- **WebSocket updates** - live price updates and server status
- **User authentication** with JWT tokens
- **Admin panel** for managing tracked cryptocurrencies
- **Interactive price charts** with candlestick data
- **Portfolio management** with profit/loss tracking

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│              React + Vite + TailwindCSS                      │
│                    (nginx :80)                               │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP / WebSocket
┌─────────────────────────┴───────────────────────────────────┐
│                        Backend                               │
│                FastAPI + SQLAlchemy                          │
│                   (uvicorn :8000)                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────────┐
│                       Database                               │
│                PostgreSQL 16 Alpine                          │
│                      (:5432)                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start (Docker Compose)

### Prerequisites
- Docker & Docker Compose installed

### Run the application

```bash
# Clone the repository
git clone <repository-url>
cd TradingSimulator

# Start all services
docker compose up --build
```

This will:
1. Start **PostgreSQL** database
2. Build and start **Backend** (runs migrations + seeds database)
3. Build and start **Frontend** (nginx serving React app)

### Access the application

| Service   | URL                           |
|-----------|-------------------------------|
| Frontend  | http://localhost              |
| Backend API | http://localhost:8000       |
| API Docs  | http://localhost:8000/docs    |

### Default Admin Account

After seeding, you can log in with:

| Field    | Value               |
|----------|---------------------|
| Username | `admin`             |
| Password | `admin123`          |

---

## 🌱 Seed Script (`seed.py`)

The `seed.py` script initializes the database with:

### Default Admin User
- **Username:** `admin`
- **Email:** `admin@tradingsim.com`
- **Password:** `admin123`
- **Balance:** $100,000.00
- **Role:** Admin

### Initial Cryptocurrencies
| Ticker | Name     | Binance Symbol |
|--------|----------|----------------|
| BTC    | Bitcoin  | BTCUSDT        |
| ETH    | Ethereum | ETHUSDT        |
| SOL    | Solana   | SOLUSDT        |

The seed script runs automatically when the backend container starts. It only seeds data if the database is empty.

---

## 🛠️ Development Setup

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/trading_simulator"
export SECRET_KEY="your-secret-key"

# Run migrations
alembic upgrade head

# Seed database
python seed.py

# Start development server
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

---

## 📁 Project Structure

```
TradingSimulator/
├── compose.yaml           # Docker Compose configuration
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── clients/       # External API clients (Binance)
│   │   │   ├── controllers/   # REST API endpoints
│   │   │   ├── core/          # Config, security, dependencies
│   │   │   ├── db/            # Database session
│   │   │   ├── models/        # SQLAlchemy models
│   │   │   ├── repositories/  # Data access layer
│   │   │   ├── schemas/       # Pydantic schemas
│   │   │   └── services/      # Business logic
│   │   └── main.py            # FastAPI application
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Unit tests
│   ├── seed.py                # Database seeder
│   ├── run.sh                 # Container startup script
│   └── Dockerfile
└── frontend/
    ├── src/
    │   ├── api/               # API client functions
    │   ├── components/        # React components
    │   ├── context/           # Auth context
    │   ├── hooks/             # Custom hooks (WebSocket)
    │   ├── pages/             # Page components
    │   └── types/             # TypeScript types
    ├── nginx.conf             # Nginx configuration
    └── Dockerfile
```

---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint           | Description       |
|--------|-------------------|-------------------|
| POST   | `/api/auth/register` | Register user   |
| POST   | `/api/auth/login`    | Login (get JWT) |

### Trading
| Method | Endpoint              | Description          |
|--------|----------------------|----------------------|
| POST   | `/api/trade/buy`      | Buy cryptocurrency   |
| POST   | `/api/trade/sell`     | Sell cryptocurrency  |
| GET    | `/api/trade/wallet`   | Get portfolio        |
| GET    | `/api/trade/transactions` | Transaction history |
| POST   | `/api/trade/reset`    | Reset account        |

### Assets
| Method | Endpoint                 | Description              |
|--------|-------------------------|--------------------------|
| GET    | `/api/assets/`           | List active assets       |
| GET    | `/api/assets/{id}/klines`| Candlestick chart data   |
| GET    | `/api/assets/admin/all`  | All assets (admin)       |
| POST   | `/api/assets/`           | Create asset (admin)     |
| PUT    | `/api/assets/{id}`       | Update asset (admin)     |
| DELETE | `/api/assets/{id}`       | Delete asset (admin)     |

### WebSocket
| Endpoint | Description                      |
|----------|----------------------------------|
| `/ws`    | Real-time prices & server status |

---

## 🧪 Running Tests

```bash
cd backend

# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app
```

---

## ⚙️ Environment Variables

### Backend

| Variable                   | Description                    | Default               |
|----------------------------|--------------------------------|-----------------------|
| `DATABASE_URL`             | PostgreSQL connection string   | Required              |
| `SECRET_KEY`               | JWT signing key                | Required              |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration            | `30`                  |

---

## 📄 License

MIT License