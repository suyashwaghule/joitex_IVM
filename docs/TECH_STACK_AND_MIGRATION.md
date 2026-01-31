# Joitex Fiber - Tech Stack & Database Migration Guide

## Current Tech Stack

### Backend
| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Runtime | Python | 3.11+ | Server-side programming |
| Framework | Flask | 2.3+ | Web framework & REST API |
| ORM | SQLAlchemy | 2.0+ | Database abstraction |
| Authentication | Flask-JWT-Extended | 4.5+ | JWT token management |
| Password Hashing | bcrypt | 4.0+ | Secure password storage |
| CORS | Flask-CORS | 4.0+ | Cross-origin requests |
| Rate Limiting | Flask-Limiter | 3.5+ | API protection |
| Production Server | Gunicorn | 21.0+ | WSGI HTTP server |

### Frontend
| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Structure | HTML5 | - | Page structure |
| Styling | CSS3 + Bootstrap | 5.3 | UI styling |
| Logic | Vanilla JavaScript | ES6+ | Client-side logic |
| Charts | Chart.js | 4.x | Data visualization |
| Icons | Bootstrap Icons | 1.x | Icon library |

### Current Database (Development)
| Component | Technology | Notes |
|-----------|------------|-------|
| Database | SQLite | File-based, single-user |
| Location | `backend/app.db` | Local file |
| Driver | Built-in Python | No additional install |

### Hosting (Production)
| Component | Service | Notes |
|-----------|---------|-------|
| Backend | Google App Engine | Python 3.11 Standard |
| Frontend | Google App Engine | Static files |
| Database | Google Cloud SQL | MySQL 8.0 |

---

## Database Migration: SQLite → MySQL

### Why Migrate?

#### SQLite Limitations (Current)
| Issue | Impact |
|-------|--------|
| Single-user access | No concurrent writes |
| File-based | Data lost on App Engine redeploy |
| No network access | Can't share across instances |
| Limited scalability | Max ~100 concurrent readers |
| No user management | No role-based DB access |

#### MySQL Benefits (Target)
| Benefit | Description |
|---------|-------------|
| Multi-user | Handles concurrent read/write |
| Persistent | Data survives deployments |
| Scalable | Handles millions of records |
| Managed | Cloud SQL handles backups, updates |
| Secure | IAM integration, encryption at rest |

---

## Migration Requirements

### Google Cloud Resources

```
┌─────────────────────────────────────────────────────────────┐
│                    Google Cloud Project                      │
│                         (joitex)                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐        ┌──────────────────────────────┐   │
│  │  App Engine  │        │      Cloud SQL (MySQL)       │   │
│  │   (api)      │◄──────►│  Instance: joitex-mysql      │   │
│  │              │ Socket │  Database: joitex_db         │   │
│  └──────────────┘        │  User: joitex_user           │   │
│                          └──────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Required Configuration

#### 1. Cloud SQL Instance
```yaml
Instance Name: joitex-mysql
Region: asia-south1
Database Version: MySQL 8.0
Machine Type: db-f1-micro (start small)
Storage: 10GB SSD (auto-increase enabled)
```

#### 2. Database & User
```sql
-- Create database
CREATE DATABASE joitex_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user
CREATE USER 'joitex_user'@'%' IDENTIFIED BY 'YOUR_SECURE_PASSWORD';

-- Grant permissions
GRANT ALL PRIVILEGES ON joitex_db.* TO 'joitex_user'@'%';
FLUSH PRIVILEGES;
```

#### 3. App Engine Configuration (`app.yaml`)
```yaml
runtime: python311
service: api
entrypoint: gunicorn -b :$PORT run:app

env_variables:
  FLASK_ENV: "production"
  DB_USER: joitex_user
  DB_PASSWORD: YOUR_SECURE_PASSWORD
  DB_NAME: joitex_db
  DB_SOCKET: /cloudsql/PROJECT_ID:REGION:INSTANCE_NAME

beta_settings:
  cloud_sql_instances: PROJECT_ID:REGION:INSTANCE_NAME
```

#### 4. Flask Configuration (`config.py`)
```python
import os

# Cloud SQL Configuration
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")
DB_SOCKET = os.environ.get("DB_SOCKET")

SQLALCHEMY_DATABASE_URI = (
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@/"
    f"{DB_NAME}?unix_socket={DB_SOCKET}"
)
```

#### 5. Requirements (`requirements.txt`)
```
mysql-connector-python>=8.0.0
```

---

## Migration Steps

### Phase 1: Preparation
- [ ] Create Cloud SQL instance
- [ ] Create database and user
- [ ] Test connection from Cloud Shell
- [ ] Update `requirements.txt` with MySQL driver
- [ ] Update `config.py` with MySQL connection logic

### Phase 2: Configuration
- [ ] Update `app.yaml` with Cloud SQL settings
- [ ] Set environment variables securely
- [ ] Add `beta_settings` for Cloud SQL proxy

### Phase 3: Deployment
- [ ] Deploy updated backend to App Engine
- [ ] Verify no connection errors in logs
- [ ] Run database migrations/seed

### Phase 4: Data Migration (if needed)
- [ ] Export data from SQLite (if any exists)
- [ ] Import data to MySQL
- [ ] Verify data integrity

### Phase 5: Verification
- [ ] Test all API endpoints
- [ ] Verify CRUD operations
- [ ] Check data persistence after redeploy
- [ ] Monitor performance

---

## Cost Analysis

### Cloud SQL Pricing (asia-south1)

| Resource | Monthly Cost (Approx) |
|----------|----------------------|
| db-f1-micro (shared) | ~$7-10 |
| 10GB SSD Storage | ~$1.70 |
| Backups (7 days) | ~$0.08/GB |
| **Total Minimum** | **~$10-15/month** |

### Cost Optimization Tips
1. Use `db-f1-micro` for development/low traffic
2. Enable auto-pause during idle time (if available)
3. Set appropriate backup retention
4. Monitor and alert on unusual usage

---

## Comparison Summary

| Feature | SQLite | MySQL (Cloud SQL) |
|---------|--------|-------------------|
| **Setup** | Zero config | Requires setup |
| **Cost** | Free | ~$10-15/month |
| **Concurrency** | Single writer | Unlimited |
| **Persistence** | Lost on redeploy | Permanent |
| **Scalability** | Limited | High |
| **Backups** | Manual | Automatic |
| **Maintenance** | None | Managed by Google |
| **Production Ready** | ❌ No | ✅ Yes |

---

## Troubleshooting

### Common Errors

#### 1. "Access denied for user"
```
Solution: Check DB_USER and DB_PASSWORD in app.yaml
```

#### 2. "Can't connect to MySQL server"
```
Solution: Verify cloud_sql_instances in beta_settings matches your instance
Format: PROJECT_ID:REGION:INSTANCE_NAME
```

#### 3. "Unknown database"
```
Solution: Create the database in Cloud SQL first
gcloud sql databases create joitex_db --instance=joitex-mysql
```

#### 4. "No such file or directory: /cloudsql/..."
```
Solution: Ensure beta_settings.cloud_sql_instances is set correctly
```

### Useful Commands

```bash
# View logs
gcloud app logs read -s api --limit=50

# Connect to Cloud SQL from Cloud Shell
gcloud sql connect joitex-mysql --user=joitex_user

# List databases
gcloud sql databases list --instance=joitex-mysql

# Create database
gcloud sql databases create joitex_db --instance=joitex-mysql
```

---

## Rollback Plan

If migration fails:

1. **Revert `app.yaml`** to use SQLite config
2. **Redeploy** without Cloud SQL settings
3. **Data**: SQLite data will be empty (fresh start)

> ⚠️ **Note**: Rolling back means losing any data created in MySQL. Export important data before rollback.

---

## Next Steps

1. Review this document
2. Create Cloud SQL instance (if not done)
3. Update configuration files
4. Deploy and test
5. Run seed script to create admin user
