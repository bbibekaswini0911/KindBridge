# KindBridge – Community Donation and Support Platform

**Connecting Donors with Orphanages, Old Age Homes, and Care Centres.**

KindBridge is a web-based community donation and support platform developed using Python and Django. It aims to connect donors with orphanages, old age homes, and care centres so that people can contribute essential items and support communities in need.

The platform provides a common space where donors can explore care centres, view their requirements, publish donation offers, and manage their contributions.

---

## Project Overview

Many care centres depend on external donations to fulfil their daily requirements. However, connecting donors with the right organisations and managing donation activities can be challenging.

KindBridge aims to simplify this process by providing an organised digital platform where donors and care centres can connect, communicate, and coordinate donation activities.

## Key Features

### 1. User Authentication
- Donor registration and login.
- Care centre registration.
- Secure authentication.
- Password reset functionality.
- User profile management.

### 2. Care Centre Management
- Explore registered care centres.
- Search and view centre details.
- Display centre requirements.
- Care centre dashboard and profile management.

### 3. Donation Management
- Submit donation requests.
- Manage donation records.
- View donation history.
- Track donation activities.

### 4. Donation Needs and Offers
- Publish donation requirements.
- Browse available donation needs.
- Publish donation offers.
- Manage personal needs and offers.
- Coordinate donation-related activities.

### 5. Dashboards and Administration
- Donor dashboard.
- Care centre dashboard.
- Administrative management.
- Donation and activity records.

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Django | Web application framework |
| MySQL | Relational database |
| HTML5 | Web page structure |
| CSS3 | Styling and layout |
| JavaScript | Frontend interactivity |
| Bootstrap / CSS | Responsive interface components |
| Git | Version control |
| GitHub | Source code management |

---

## Project Structure

```text
KindBridge/
│
├── KindBridge/          # Main Django project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── accounts/            # User accounts and authentication
│
├── centers/             # Care centre management
│
├── donations/           # Donation management
│
├── market/              # Donation needs and offers
│
├── static/              # CSS, JavaScript and static assets
│   ├── css/
│   └── js/
│
├── templates/            # HTML templates
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Installation and Setup

Follow these steps to run KindBridge on your local machine.

### Prerequisites

Install the following:

- Python
- MySQL Server
- Git
- Visual Studio Code (recommended)

### Step 1: Clone the Repository

```bash
git clone https://github.com/bbibekaswini0911/KindBridge.git
```

Navigate into the project directory:

```bash
cd KindBridge
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the same directory as `manage.py`.

Add your local configuration:

```env
DJANGO_SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=kindbridge_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

**Important:** Replace the placeholder values with your own local configuration. Never upload your actual `.env` file or database credentials to GitHub.

### Step 5: Create the MySQL Database

Open MySQL and execute:

```sql
CREATE DATABASE kindbridge_db;
```

Make sure the database details in `.env` match your MySQL configuration.

### Step 6: Apply Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 7: Create an Administrator Account

```bash
python manage.py createsuperuser
```

Follow the instructions to create your administrator account.

### Step 8: Run the Development Server

```bash
python manage.py runserver
```

Open your browser and visit:

```text
http://127.0.0.1:8000/
```

---

## Database

KindBridge uses MySQL as its relational database management system.

The database stores information related to:

- User accounts
- Care centres
- Donations
- Donation requirements
- Donation offers and related records

---

## Future Enhancements

The following improvements can be considered for future development:

- Online email notifications.
- Enhanced donation tracking.
- Downloadable donation reports.
- Improved reporting and analytics.
- Additional security and performance improvements.
- Online deployment and accessibility.

---

## Project Purpose

KindBridge is developed as an academic MCA project to demonstrate the practical implementation of a database-driven web application using Python, Django, and MySQL.

The project focuses on using technology to encourage community participation and make donation coordination more organised and accessible.

---

## Repository

**GitHub:** https://github.com/bbibekaswini0911/KindBridge

---

## License

This project is developed for academic and educational purposes.
