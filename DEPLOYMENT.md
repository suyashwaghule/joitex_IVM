# Google Cloud Deployment Guide

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud CLI** installed: https://cloud.google.com/sdk/docs/install
3. **Project Created** in Google Cloud Console

## Setup

### 1. Install and Initialize gcloud CLI

```bash
# Install gcloud (if not installed)
# Windows: Download from https://cloud.google.com/sdk/docs/install

# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

### 2. Enable Required APIs

```bash
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 3. Create App Engine Application

```bash
# Choose a region (e.g., us-central1, asia-south1)
gcloud app create --region=asia-south1
```

## Deployment

### Deploy Backend (API Service)

```bash
cd backend

# Set environment variables (IMPORTANT: Use strong, unique values!)
gcloud app deploy --set-env-vars="SECRET_KEY=your-secret-key-here,JWT_SECRET_KEY=your-jwt-secret-here,FLASK_ENV=production"

# Or just deploy (set env vars in GCP Console later)
gcloud app deploy
```

### Deploy Frontend (Default Service)

```bash
cd frontend
gcloud app deploy
```

### Deploy Both at Once

```bash
# From project root
gcloud app deploy backend/app.yaml frontend/app.yaml
```

## Post-Deployment

### 1. Initialize Database

After first deployment, you need to seed the database:

```bash
# SSH into the App Engine instance (or use Cloud Shell)
# Run the seed script
cd backend
python seed.py
```

Alternatively, set up Cloud SQL and run migrations.

### 2. Access Your Application

- **Frontend**: https://YOUR_PROJECT_ID.REGION.r.appspot.com
- **Backend API**: https://api-dot-YOUR_PROJECT_ID.REGION.r.appspot.com

### 3. View Logs

```bash
gcloud app logs tail -s api
gcloud app logs tail -s default
```

## Database Options

### Option 1: SQLite (Development Only)
- Already configured, works out of the box
- Data is lost on each deployment
- NOT recommended for production

### Option 2: Cloud SQL (Recommended for Production)

```bash
# Create a Cloud SQL instance
gcloud sql instances create joitex-db --tier=db-f1-micro --region=asia-south1 --database-version=POSTGRES_15

# Create database
gcloud sql databases create joitex --instance=joitex-db

# Create user
gcloud sql users create joitex-user --instance=joitex-db --password=YOUR_PASSWORD

# Update app.yaml env_variables:
# SQLALCHEMY_DATABASE_URI: postgresql+pg8000://joitex-user:YOUR_PASSWORD@/joitex?unix_sock=/cloudsql/PROJECT_ID:asia-south1:joitex-db/.s.PGSQL.5432
```

## Troubleshooting

### Common Issues

1. **502 Bad Gateway**: Check logs with `gcloud app logs tail -s api`
2. **CORS Errors**: Ensure CORS_ORIGINS is set correctly in backend config
3. **Database Errors**: Verify SQLALCHEMY_DATABASE_URI is correct

### Useful Commands

```bash
# List deployed services
gcloud app services list

# View specific service
gcloud app browse -s api
gcloud app browse -s default

# Delete a service
gcloud app services delete SERVICE_NAME

# View current configuration
gcloud app describe
```

## Cost Management

- App Engine Standard has a free tier
- Set `max_instances: 1` to limit costs
- Use `min_instances: 0` to scale to zero when idle
- Monitor usage in Cloud Console > Billing
