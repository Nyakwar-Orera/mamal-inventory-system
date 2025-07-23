# Mamal Inventory System - Technical Documentation

**Presented to:** HOD Supervisor  
**Prepared by:** Nyakwar Orera  
**Date:** [Submission Date]

---

## 1. Project Overview

### 1.1 Introduction

The **Mamal Inventory System** is a **Flask-based web application** developed to efficiently manage IT and office assets such as desktops, printers, servers, and stationery supplies in an organizational or institutional setting.

### 1.2 Key Features

- **Dashboard** – Summarizes key data, low-stock notifications, and maintenance reminders  
- **Asset Management** – Add, update, delete, and filter physical assets  
- **Stationery Tracking** – Monitors inventory and alerts on low stock  
- **Check-In/Check-Out** – Records asset allocations to staff/students  
- **Maintenance Logs** – Track service history and costs  
- **Reports** – Generate downloadable Excel and PDF reports  
- **QR Integration** – Quick actions via QR code scanning  
- **User Authentication** – Role-based access (Admin, Staff, Guest)

### 1.3 Technology Stack

| Category       | Technologies                                 |
| -------------- | -------------------------------------------- |
| Backend        | Python, Flask, Flask-SQLAlchemy, Flask-Login |
| Frontend       | HTML5, CSS3, Bootstrap 5, Chart.js           |
| Database       | SQLite (Dev), PostgreSQL (Prod)              |
| Reporting/QR   | Pandas, ReportLab, qrcode                    |
| Deployment     | Docker, Render, or Heroku                    |

---

## 2. System Architecture

### 2.1 High-Level Design

- **Frontend** → Bootstrap + JS  
- **Flask Backend** → Routing, Logic, Authentication  
- **Database** → Persistent asset data

### 2.2 Database Schema

- `Asset`  
- `Stationery`  
- `Checkout`  
- `Maintenance`  
- `User`  

---

## 3. Installation & Execution Guide

### 3.1 Prerequisites

- Python 3.8+  
- Pip  
- Git (optional)

### 3.2 Setup Instructions

**Step 1: Clone the Project**

```bash
git clone https://github.com/Nyakwar-Orera/Mamal-Inventory-System.git
cd Mamal-Inventory-System
```

**Step 2: Create and Activate Virtual Environment**

```bash
python -m venv venv
# Activate
source venv/bin/activate       # macOS/Linux
.env\Scriptsctivate        # Windows
```

**Step 3: Install Dependencies**

```bash
pip install -r requirements.txt
pip install email_validator
```

**Step 4: Configure Environment**

Create a `.env` file:

```env
FLASK_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///assets.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password
ADMIN_EMAIL=admin@example.com
```

**Step 5: Initialize Database**

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

**Step 6: Launch the App**

```bash
flask run --host=127.0.0.1 --port=5000
```

Then open: [http://localhost:5000](http://localhost:5000)

---

## 4. User Guide

### 4.1 Roles and Permissions

| Role   | Permissions                                   |
|--------|-----------------------------------------------|
| Admin  | Full access (users, assets, stationery)       |
| Staff  | Manage assets and checkouts                   |
| Guest  | View-only access                              |

### 4.2 Common Workflows

- **Add Asset**: Go to *Assets > Add Asset*, fill form, QR is auto-generated  
- **Checkout Asset**: *Checkout > Active*, assign to user with due date  
- **Low Stock Alerts**: Triggered email when stationery (e.g., paper) < 100  
- **Generate Report**: Navigate to *Reports*, choose Excel or PDF

---

## 5. Technical Insights

### 5.1 QR Code Support

- Built using `qrcode` library  
- Stored as base64 images and rendered in templates

### 5.2 Background Tasks

- Uses APScheduler for periodic tasks like email alerts

### 5.3 Report Generation

- Excel: `pandas`, `openpyxl`  
- PDF: `reportlab`

---

## 6. Deployment Options

### Option 1: Render (Recommended)

- Connect GitHub repo  
- Add `Procfile`:  
  ```
  web: gunicorn run:app
  ```
- Add your environment variables  
- Done!

### Option 2: Heroku

```bash
heroku create mamal-inventory
git push heroku main
heroku run flask db upgrade
```

### Option 3: Docker

**Dockerfile:**

```dockerfile
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
```

**Run it:**

```bash
docker build -t mamal-inventory .
docker run -p 5000:5000 mamal-inventory
```

---

## 7. Presentation Tips

### 7.1 Key Demo Points

- Show dashboard summary  
- Scan QR to view/check asset  
- Simulate low stock alert  
- Generate and download PDF report

### 7.2 Sample Questions

- **Can it scale?** → Yes, with PostgreSQL + Docker  
- **Is it secure?** → Yes, uses Flask-Login and role-based access  
- **Can it run offline?** → Yes, using SQLite and localhost

---

## 8. Conclusion & Future Enhancements

**Current Capabilities:**

- Role-based asset tracking  
- QR & report generation  
- Automated email alerts

**Planned Enhancements:**

- Mobile QR scanner app  
- Barcode integration  
- REST API for third-party integrations

---

## 9. References

- [Flask Documentation](https://flask.palletsprojects.com/)  
- [Bootstrap](https://getbootstrap.com/)  
- [GitHub Repo](https://github.com/Nyakwar-Orera/Mamal-Inventory-System)

---

> 💡 *Tip: Seed your database with demo data. Backup screenshots in case of live demo issues.*