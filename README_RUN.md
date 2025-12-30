# Joitex Inventory System - Setup & Run Guide

## Prerequisites
- Python 3.8 or higher installed.

## Part 1: Backend Setup
The backend is a Flask API that powers the application.

1. **Navigate to the backend folder**:
   Open a terminal (Command Prompt or PowerShell) and run:
   ```powershell
   cd backend
   ```

2. **Set up Virtual Environment**:
   If you don't have a `venv` folder yet:
   ```powershell
   python -m venv venv
   ```
   
   Activate it:
   ```powershell
   .\venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Initialize Database**:
   This will create the database file and populate it with demo users and data.
   ```powershell
   python seed.py
   ```
   *Note: If you see "Database already contains users", it's already set up.*

5. **Run the Server**:
   ```powershell
   python run.py
   ```
   The backend will start at `http://127.0.0.1:5000`. Keep this terminal open.

## Part 2: Frontend Access
The frontend consists of static HTML files.

1. **Open the Application**:
   Go to the root folder `Joitex inventory Frontend only` and double-click `index.html` to open it in your browser.

## Login Credentials (Demo Accounts)
Use these credentials to log in to different portals:

| Role        | Email                  | Password   |
|-------------|------------------------|------------|
| **Admin**   | admin@joitex.com       | admin123   |
| **Sales**   | sales@joitex.com       | sales123   |
| **Engineer**| engineer@joitex.com    | eng123     |
| **Inventory**| inventory@joitex.com  | inv123     |
| **Network** | network@joitex.com     | net123     |
| **Finance** | finance@joitex.com     | fin123     |
| **Call Center**| callcenter@joitex.com | call123   |
