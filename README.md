# Joitex Fiber - Inventory & Operations Management System

A comprehensive web-based management system for fiber internet service providers.

## Features

- **Multi-Portal Architecture**: Admin, Call Center, Sales, Engineer, Inventory, Network, and Finance portals
- **Role-Based Access Control**: Secure authentication with JWT tokens
- **Real-Time Dashboard**: Live statistics and performance metrics
- **OLT Management**: Device monitoring, port management, and automatic logging
- **IP Address Management (IPAM)**: Pool management, allocation tracking, and subnet calculations
- **Inventory Control**: Stock tracking, transactions, and vendor management
- **Engineer Workflow**: Job assignment, device entry, and completion tracking

## Tech Stack

### Backend
- Python 3.11+
- Flask 2.3+
- SQLAlchemy (SQLite for dev, PostgreSQL/MySQL for production)
- JWT Authentication
- Gunicorn (production server)

### Frontend
- HTML5, CSS3, JavaScript (Vanilla)
- Bootstrap 5.3
- Chart.js

## Getting Started

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/joitex-fiber.git
   cd joitex-fiber
   ```

2. **Set up backend**
   ```bash
   cd backend
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run the development server**
   ```bash
   python run.py
   ```

5. **Access the application**
   - Frontend: Open `frontend/index.html` in your browser
   - API: http://localhost:5000

### Demo Credentials (Development Only)
| Role | Email | Password |
|------|-------|----------|
| Admin | admin@joitex.com | admin123 |
| Network | network@joitex.com | net123 |
| Engineer | engineer@joitex.com | eng123 |
| Inventory | inventory@joitex.com | inv123 |

## Production Deployment

### Environment Variables

```bash
FLASK_ENV=production
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
SQLALCHEMY_DATABASE_URI=postgresql://user:pass@host:5432/db
CORS_ORIGINS=https://yourdomain.com
```

### Using Gunicorn

```bash
gunicorn run:app --bind 0.0.0.0:$PORT --workers 4
```

### Docker (Optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/ .
RUN pip install -r requirements.txt
CMD gunicorn run:app --bind 0.0.0.0:$PORT
```

## API Documentation

Base URL: `/api`

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration

### Network Module
- `GET /api/network/stats` - Dashboard statistics
- `GET /api/network/olts` - List all OLTs
- `POST /api/network/olts` - Create OLT
- `GET /api/network/olts/:id/logs` - Get OLT logs

### Inventory Module
- `GET /api/inventory/stats` - Inventory statistics
- `GET /api/inventory/items` - List catalog items
- `POST /api/inventory/receive` - Receive stock
- `POST /api/inventory/issue` - Issue stock

## Project Structure

```
joitex-fiber/
├── backend/
│   ├── app/
│   │   ├── __init__.py      # App factory
│   │   ├── config.py        # Configuration
│   │   ├── models*.py       # Database models
│   │   └── routes/          # API endpoints
│   ├── run.py               # Entry point
│   ├── Procfile             # Production server config
│   └── requirements.txt     # Python dependencies
│
└── frontend/
    ├── index.html           # Login page
    ├── select-portal.html   # Portal selector
    ├── assets/
    │   ├── css/             # Stylesheets
    │   └── js/              # JavaScript modules
    └── portals/             # Portal-specific pages
        ├── admin/
        ├── network/
        ├── engineer/
        └── ...
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is proprietary software for Joitex Fiber.

## Support

For support, contact: support@joitex.com
