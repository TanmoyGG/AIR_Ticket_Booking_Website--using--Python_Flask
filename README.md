# ✈️ Horizon Airlines - Flight Booking System

> **Your Gateway to Seamless Air Travel** - A full-featured airline ticket booking platform built with Python Flask and MySQL

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://www.mysql.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)

---

## 📋 Table of Contents
- [Project Description](#-project-description)

- [Features](#-features)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Database Setup](#database-setup)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

---

## 📖 Project Description

**Horizon Airlines** is a modern, enterprise-grade flight booking web application that revolutionizes the way users search, book, and manage flight reservations. Built with Python Flask and MySQL, this platform delivers a seamless experience for both customers and administrators.

### Why This Project?

The airline industry requires robust, scalable booking systems that can handle complex operations like:
- **Real-time seat availability management** across multiple flights and dates
- **Dynamic pricing strategies** with early-bird discounts and seasonal promotions
- **Secure payment processing** with transaction integrity
- **Role-based access control** for customers and administrators
- **Business intelligence** through comprehensive reporting and analytics

This project demonstrates modern web development practices including:
- **MVC Architecture** with Flask Blueprints for modular design
- **Secure Authentication** using bcrypt password hashing
- **Database Transactions** for data consistency
- **PDF Generation** for professional booking receipts
- **Data Visualization** with matplotlib for business insights
- **Responsive Design** using Bootstrap 5

### What Does It Do?

**For Customers:**
- Search and filter flights by cities, dates, and preferences
- Book tickets with automatic discount calculation (10-25% for early bookings)
- Choose between Economy and Business class seating
- View and manage all bookings from a personal dashboard
- Cancel bookings with automatic refund calculation
- Download professional PDF receipts for bookings and cancellations

**For Administrators:**
- Comprehensive dashboard for system overview
- Complete user management (create, edit, delete users)
- Flight schedule management (add, edit, delete routes and timings)
- City and route management
- View and manage all customer bookings
- Generate business reports with visual charts (monthly sales, top routes, top customers)

---

## 🛠️ Tech Stack

### Backend Technologies
| Technology | Purpose |
|------------|---------|
| **Python 3.8+** | Core programming language |
| **Flask 2.0+** | Lightweight WSGI web framework |
| **Flask Blueprints** | Modular application architecture |
| **mysql-connector-python** | MySQL database driver |

### Database
| Technology | Purpose |
|------------|---------|
| **MySQL 8.0+** | Relational database management system |

### Security & Authentication
| Technology | Purpose |
|------------|---------|
| **bcrypt** | Secure password hashing (Blowfish cipher) |
| **Flask Sessions** | Secure session management |

### Data Processing & Visualization
| Technology | Purpose |
|------------|---------|
| **Pandas** | Data manipulation and analysis |
| **Matplotlib** | Chart and graph generation |
| **NetworkX** | Route network visualization |

### Document Generation
| Technology | Purpose |
|------------|---------|
| **ReportLab** | Professional PDF receipt generation |

### Frontend Technologies
| Technology | Purpose |
|------------|---------|
| **HTML5 & CSS3** | Semantic markup and styling |
| **Bootstrap 5.3** | Responsive UI framework |
| **Font Awesome 6.1** | Icon library |
| **jQuery 3.6** | DOM manipulation and AJAX |

---

## ✨ Features

### 👤 Customer Features

#### Authentication & Security
- 🔐 Secure user registration with bcrypt password hashing
- 🔑 Role-based login system (user/admin)
- 🛡️ Session-based authentication
- 🚪 Secure logout functionality

#### Flight Search & Booking
- 🔍 **Advanced Flight Search**
  - Filter by departure and arrival cities
  - Select travel dates (up to 90 days in advance)
  - Choose number of passengers
  - Select seat class (Economy/Business)
  
- 💰 **Smart Pricing System**
  - Base fare pricing per route
  - Business class: 2x Economy fare
  - **Early Bird Discounts:**
    - 🎉 25% OFF for bookings 80-90 days in advance
    - 🎊 15% OFF for bookings 60-79 days in advance
    - 🎁 10% OFF for bookings 45-59 days in advance
  
- ✅ **Real-time Seat Availability**
  - Dynamic capacity management (80% Economy, 20% Business)
  - Instant seat reservation upon booking
  - Prevents overbooking with database locks

#### Booking Management
- 📊 **Personal Dashboard**
  - View all active bookings
  - See flight details (departure, arrival, dates, times)
  - Track booking status
  - Quick access to booking actions
  
- ❌ **Flexible Cancellation Policy**
  - **60+ days before departure:** Full refund (0% fee)
  - **30-60 days before:** 60% refund (40% fee)
  - **Less than 30 days:** No refund (100% fee)
  - Automatic seat restoration to inventory
  - Instant cancellation receipt generation

#### Document Management
- 🧾 **Professional PDF Receipts**
  - Booking confirmation receipts with:
    - Booking ID and flight details
    - Passenger information
    - Itemized pricing breakdown
    - Discount calculations
    - Payment summary
  - Cancellation receipts with:
    - Cancellation details and dates
    - Refund calculation breakdown
    - Fee structure explanation
  - Enhanced styling with company branding

#### Account Management
- ⚙️ **Profile Customization**
  - Update username
  - Change email address
  - Reset password securely
  - Delete account (with booking constraint checks)

### 🔧 Administrator Features

#### Admin Dashboard
- 📈 **Command Center**
  - Quick access to all management modules
  - System overview cards
  - Navigation to key functionalities

#### User Management
- 👥 **Complete User Control**
  - View all registered users with details
  - Add new users (including admin accounts)
  - Edit user information (username, email, role)
  - Update passwords securely
  - Delete user accounts (with safety checks)
  - Role assignment (user/admin)

#### Flight Schedule Management
- 🗓️ **Timetable Operations**
  - View complete flight schedule
  - Display flight capacity breakdown (Economy/Business)
  - Show fare information
  - Add new flight schedules
  - Edit existing schedules:
    - Modify departure/arrival times
    - Update total capacity
    - Enable/disable schedules
  - Delete flight schedules
  - Route validation

#### City & Route Management
- 🌍 **Geographic Control**
  - View all cities in the system
  - Add new cities
  - Edit city names
  - Delete cities (with constraint handling)

#### Booking Oversight
- 📖 **Customer Booking Management**
  - View all customer bookings system-wide
  - Filter booking details:
    - User information
    - Flight details
    - Travel dates and times
    - Seat information
    - Payment amounts
  - Update booking status (Confirmed/Cancelled/Pending)
  - Track booking history

#### Business Intelligence
- 📊 **Reports & Analytics Dashboard**
  - **Monthly Sales Report**
    - Visual bar chart showing revenue trends over time
    - Total sales per month for confirmed bookings
  - **Top Routes by Revenue**
    - Horizontal bar chart of highest-earning routes
    - Top 10 most profitable flight paths
  - **Top Customers Report**
    - Bar chart showing highest-spending customers
    - Top 10 customers by total spending
  - All charts generated with Matplotlib
  - Base64-encoded inline image display

---

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed on your system:

#### Required Software

1. **Python 3.8 or higher**
   ```bash
   # Check Python version
   python --version
   # or
   python3 --version
   ```
   Download from: [https://www.python.org/downloads/](https://www.python.org/downloads/)

2. **MySQL Server 8.0 or higher**
   ```bash
   # Check MySQL version
   mysql --version
   ```
   Download from: [https://dev.mysql.com/downloads/mysql/](https://dev.mysql.com/downloads/mysql/)

3. **pip (Python Package Manager)**
   ```bash
   # Check pip version
   pip --version
   ```
   Usually comes with Python. If not, install from: [https://pip.pypa.io/en/stable/installation/](https://pip.pypa.io/en/stable/installation/)

4. **Git (Optional - for cloning)**
   ```bash
   # Check Git version
   git --version
   ```
   Download from: [https://git-scm.com/downloads](https://git-scm.com/downloads)

### Installation

Follow these steps to set up the project on your local machine:

#### Step 1: Clone the Repository

```bash
# Clone via HTTPS
git clone https://github.com/TanmoyGG/AIR_Ticket_Booking_Website--using--Python_Flask.git

# Or download ZIP and extract

# Navigate to project directory
cd AIR_Ticket_Booking_Website--using--Python_Flask
```

#### Step 2: Create Virtual Environment (Recommended)

Creating a virtual environment isolates project dependencies from your system Python.

**Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

**Linux/Mac:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

You should see `(venv)` prefix in your terminal when activated.

#### Step 3: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- Flask-Login (user session management)
- Flask-Bcrypt (password hashing)
- mysql-connector-python (MySQL driver)
- pandas (data analysis)
- matplotlib (data visualization)
- networkx (network graphs)
- bcrypt (password hashing)
- reportlab (PDF generation)

### Database Setup

#### Step 1: Start MySQL Server

Ensure your MySQL server is running on `localhost:3306`

**Windows:**
```bash
# Start MySQL service
net start MySQL80
```

**Linux:**
```bash
# Start MySQL service
sudo systemctl start mysql
```

**Mac:**
```bash
# Start MySQL service
brew services start mysql
```

#### Step 2: Configure Database Credentials

Open `app.py` and update the database configuration (lines 14-19):

```python
db_config = {
    'host': 'localhost',
    'user': 'root',           # Change to your MySQL username
    'password': '12345',      # Change to your MySQL password
    'database': 'horizonairlines'
}
```

#### Step 3: Create Database Schema

Create a file named `schema.sql` in the project root directory:

```bash
# Windows
type nul > schema.sql

# Linux/Mac
touch schema.sql
```

Add the following SQL schema to `schema.sql`:

```sql
-- ============================================
-- Horizon Airlines Database Schema
-- ============================================

-- Users Table: Store customer and admin accounts
CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_username (username),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Cities Table: Available flight destinations
CREATE TABLE IF NOT EXISTS Cities (
    city_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    INDEX idx_city_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Routes Table: Flight paths between cities
CREATE TABLE IF NOT EXISTS Routes (
    route_id INT AUTO_INCREMENT PRIMARY KEY,
    departure_city_id INT NOT NULL,
    arrival_city_id INT NOT NULL,
    standard_fare DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (departure_city_id) REFERENCES Cities(city_id) ON DELETE CASCADE,
    FOREIGN KEY (arrival_city_id) REFERENCES Cities(city_id) ON DELETE CASCADE,
    UNIQUE KEY unique_route (departure_city_id, arrival_city_id),
    INDEX idx_departure (departure_city_id),
    INDEX idx_arrival (arrival_city_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- FlightSchedules Table: Recurring flight timetables
CREATE TABLE IF NOT EXISTS FlightSchedules (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    route_id INT NOT NULL,
    departure_time TIME NOT NULL,
    arrival_time TIME NOT NULL,
    total_capacity INT DEFAULT 130,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (route_id) REFERENCES Routes(route_id) ON DELETE CASCADE,
    INDEX idx_route (route_id),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- FlightInstances Table: Specific date instances of flights
CREATE TABLE IF NOT EXISTS FlightInstances (
    flight_instance_id INT AUTO_INCREMENT PRIMARY KEY,
    schedule_id INT NOT NULL,
    departure_date DATE NOT NULL,
    available_economy_seats INT NOT NULL,
    available_business_seats INT NOT NULL,
    FOREIGN KEY (schedule_id) REFERENCES FlightSchedules(schedule_id) ON DELETE CASCADE,
    UNIQUE KEY unique_instance (schedule_id, departure_date),
    INDEX idx_schedule (schedule_id),
    INDEX idx_date (departure_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Bookings Table: Customer flight reservations
CREATE TABLE IF NOT EXISTS Bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    flight_instance_id INT NOT NULL,
    num_seats INT NOT NULL,
    seat_type ENUM('Economy', 'Business') NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    status ENUM('Confirmed', 'Cancelled', 'Pending') DEFAULT 'Confirmed',
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (flight_instance_id) REFERENCES FlightInstances(flight_instance_id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_instance (flight_instance_id),
    INDEX idx_status (status),
    INDEX idx_booking_date (booking_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### Step 4: Initialize Database

The application will automatically:
1. Create the `horizonairlines` database if it doesn't exist
2. Execute `schema.sql` to create all tables
3. Seed initial data with 21 pre-configured flight routes across UK cities

**Seeded Cities Include:**
- Newcastle, Bristol, Cardiff, Edinburgh
- Manchester, London, Glasgow, Portsmouth
- Dundee, Southampton, Birmingham, Aberdeen

**Sample Routes Include:**
- Newcastle ↔ Bristol (£90)
- Bristol ↔ Manchester (£80)
- Cardiff ↔ Edinburgh (£90)
- Portsmouth ↔ Dundee (£120)
- And 17 more routes!

---

## 💻 Usage

### Starting the Application

1. **Ensure virtual environment is activated:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Run the Flask application:**
   ```bash
   python app.py
   ```

3. **Expected output:**
   ```
   Database schema loaded from schema.sql (duplicates ignored)
    * Serving Flask app 'app'
    * Debug mode: on
    * Running on http://127.0.0.1:8080
   ```

4. **Access the application:**
   
   Open your web browser and navigate to:
   ```
   http://localhost:8080
   ```

### Creating Your First User Account

1. **Navigate to Signup Page:**
   - Click "Sign Up" on the login page
   - Or go directly to: `http://localhost:8080/signup`

2. **Fill in Registration Form:**
   ```
   First Name: John
   Last Name: Doe
   Username: johndoe
   Email: john.doe@example.com
   Password: YourSecurePassword123
   ```

3. **Submit and Login:**
   - After registration, you'll be redirected to the homepage
   - You can now search and book flights!

### Creating an Admin Account

#### Method 1: Direct Database Insertion

1. **Generate hashed password:**
   ```python
   import bcrypt
   
   password = "admin123"
   hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
   print(hashed.decode('utf-8'))
   ```

2. **Insert admin user via MySQL:**
   ```sql
   USE horizonairlines;
   
   INSERT INTO Users (username, email, password_hash, role) 
   VALUES (
       'admin',
       'admin@horizonairlines.com',
       '$2b$12$PASTE_YOUR_HASHED_PASSWORD_HERE',
       'admin'
   );
   ```

#### Method 2: Promote Existing User

```sql
USE horizonairlines;

-- Promote user to admin by email
UPDATE Users 
SET role = 'admin' 
WHERE email = 'your-email@example.com';
```

#### Method 3: Via Admin Panel (if you already have admin access)

1. Login as admin
2. Navigate to: `http://localhost:8080/admin/users`
3. Click "Add New User"
4. Fill form and select role as "admin"

### Accessing Features

#### Customer Features

| Feature | URL | Description |
|---------|-----|-------------|
| Login | `/login` | User authentication |
| Signup | `/signup` | New user registration |
| Flight Search | `/search-flights` | Search and book flights |
| My Bookings | `/homepage` | View and manage bookings |
| Account Settings | `/account` | Update profile |

#### Admin Features

| Feature | URL | Description |
|---------|-----|-------------|
| Admin Dashboard | `/admin/dashboard` | Admin control panel |
| User Management | `/admin/users` | Manage all users |
| Flight Schedules | `/admin/timetable` | Manage flight schedules |
| Cities | `/admin/cities` | Manage cities |
| All Bookings | `/admin/bookings` | View all bookings |
| Reports | `/admin/reports` | Business analytics |

### Example Booking Flow

1. **Login** → `/login`
2. **Search Flights** → Select cities, date, seats
3. **View Results** → See available flights with discounts
4. **Book Flight** → Click "Book Now"
5. **Confirm Payment** → Review details and confirm
6. **Download Receipt** → Automatic PDF download
7. **View Booking** → Check "My Bookings" dashboard

### Example Cancellation Flow

1. **Go to My Bookings** → `/homepage`
2. **Select Booking** → Find the booking to cancel
3. **Click Cancel** → Confirm cancellation
4. **View Refund** → See refund calculation
5. **Download Receipt** → Get cancellation PDF

---

## 📁 Project Structure

```
AIR_Ticket_Booking_Website--using--Python_Flask/
│
├── 📄 app.py                      # Main Flask application entry point
├── 📄 schema.sql                  # MySQL database schema (create this)
├── 📄 requirements.txt            # Python dependencies
├── 📄 LICENSE                     # MIT License
├── 📄 README.md                   # This file
│
├── 📁 routes/                     # Flask Blueprints (Modular Routes)
│   ├── __init__.py               # Package initializer
│   ├── homepage.py               # Dashboard, view bookings, cancel bookings
│   ├── flights.py                # Flight search, filtering, pricing logic
│   ├── login.py                  # User authentication, logout
│   ├── signup.py                 # User registration with bcrypt
│   ├── account.py                # Profile updates, password change, delete account
│   ├── payment.py                # Booking confirmation, PDF generation
│   ├── admin.py                  # Complete admin panel functionality
│   └── visualization.py          # Data visualization (legacy/optional)
│
├── 📁 templates/                  # Jinja2 HTML Templates
│   ├── login.html                # User login page
│   ├── signup.html               # Registration form
│   ├── homepage.html             # User dashboard with bookings
│   ├── flights.html              # Flight search interface
│   ├── account.html              # Account management page
│   ├── nav-bar.html              # Shared navigation bar
│   │
│   └── 📁 admin/                 # Admin Panel Templates
│       ├── dashboard.html        # Admin homepage
│       ├── nav.html              # Admin navigation
│       ├── users.html            # User list
│       ├── add_user.html         # Add user form
│       ├── edit_user.html        # Edit user form
│       ├── timetable.html        # Flight schedules list
│       ├── add_schedule.html     # Add schedule form
│       ├── edit_schedule.html    # Edit schedule form
│       ├── cities.html           # City management
│       ├── bookings.html         # All bookings view
│       └── reports.html          # Analytics dashboard
│
└── 📁 static/                     # Static Assets
    ├── 📁 CSS/                   # Stylesheets
    │   ├── login.css            # Login page styles
    │   ├── homepage.css         # Dashboard styles
    │   ├── flights.css          # Flight search styles
    │   ├── account.css          # Account page styles
    │   ├── navbar.css           # Navigation styles
    │   └── admin.css            # Admin panel styles
    │
    └── 📁 images/                # Images and icons
        └── (application images)
```

### Module Breakdown

#### `app.py` - Main Application
- Flask app initialization and configuration
- Database connection setup with context managers
- Blueprint registration for modular routing
- Database schema loading from `schema.sql`
- Initial data seeding (cities, routes, schedules)
- Request lifecycle management (`@before_request`, `@teardown_request`)

#### Routes Package (Blueprints)

**`homepage.py`** - User Dashboard
- Display all user bookings with details
- Cancel booking functionality
- Refund calculation based on cancellation policy
- Seat restoration to inventory
- PDF cancellation receipt generation

**`flights.py`** - Flight Search
- Search flights by departure/arrival cities
- Date-based filtering (up to 90 days ahead)
- Seat type selection (Economy/Business)
- Dynamic pricing with discounts
- Real-time availability checking
- Display all available routes

**`login.py`** - Authentication
- User login with bcrypt password verification
- Role-based redirect (user → homepage, admin → dashboard)
- Session management
- Secure logout with session cleanup

**`signup.py`** - User Registration
- New user registration form
- Password hashing with bcrypt
- Email/username uniqueness validation
- Automatic login after registration

**`account.py`** - Profile Management
- View current account details
- Update username and email
- Change password (with bcrypt rehashing)
- Delete account functionality
- Email availability checking

**`payment.py`** - Booking & Payments
- Display booking summary
- Price calculation with discounts
- Create flight instances dynamically
- Seat availability locking (FOR UPDATE)
- Booking confirmation
- Professional PDF receipt generation (ReportLab)
- Two booking flows: with payment page & direct booking

**`admin.py`** - Complete Admin Panel
- **Dashboard:** Overview with quick links
- **User Management:** CRUD operations for users
- **Schedule Management:** Add/edit/delete flight schedules
- **City Management:** Manage city database
- **Booking Management:** View and update all bookings
- **Reports & Analytics:** Visual charts with matplotlib
  - Monthly sales trends
  - Top revenue-generating routes
  - Highest-spending customers
- Admin authentication decorator (`@admin_required`)

**`visualization.py`** - Data Visualization (Optional/Legacy)
- Network graph of flight connections
- Route visualization using NetworkX

---

## 🗄️ Database Schema

### Entity Relationship Diagram

```
┌──────────────┐          ┌──────────────┐
│    Users     │          │   Bookings   │
├──────────────┤          ├──────────────┤
│ user_id (PK) │◄────────┤ booking_id   │
│ username     │          │ user_id (FK) │
│ email        │          │ flight_inst..│
│ password_hash│          │ num_seats    │
│ role         │          │ seat_type    │
│ first_name   │          │ total_price  │
│ last_name    │          │ status       │
│ created_at   │          │ booking_date │
└──────────────┘          └──────┬───────┘
                                 │
                                 │
                          ┌──────▼───────────┐
                          │ FlightInstances  │
┌──────────────┐          ├──────────────────┤
│   Cities     │          │ flight_inst.. PK │
├──────────────┤          │ schedule_id (FK) │
│ city_id (PK) │          │ departure_date   │
│ name         │          │ avail_economy_..│
└───┬──────┬───┘          │ avail_business..│
    │      │              └─────────┬────────┘
    │      │                        │
    │      │              ┌─────────▼──────────┐
    │      │              │  FlightSchedules   │
    │      │              ├────────────────────┤
    │      └─────────────►│ schedule_id (PK)   │
    │                     │ route_id (FK)      │
    │                     │ departure_time     │
    │                     │ arrival_time       │
    │                     │ total_capacity     │
    │                     │ is_active          │
    │                     └──────────┬─────────┘
    │                                │
    │                      ┌─────────▼─────────┐
    │                      │      Routes       │
    │                      ├───────────────────┤
    └─────────────────────►│ route_id (PK)     │
                           │ departure_city_id │
                           │ arrival_city_id   │
                           │ standard_fare     │
                           └───────────────────┘
```

### Table Descriptions

#### **Users Table**
Stores customer and administrator accounts.

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | INT (PK) | Unique user identifier |
| `first_name` | VARCHAR(100) | User's first name |
| `last_name` | VARCHAR(100) | User's last name |
| `username` | VARCHAR(100) | Unique username |
| `email` | VARCHAR(150) | Unique email address |
| `password_hash` | VARCHAR(255) | Bcrypt hashed password |
| `role` | ENUM | User role: 'user' or 'admin' |
| `created_at` | TIMESTAMP | Account creation time |

#### **Cities Table**
Available flight destinations.

| Column | Type | Description |
|--------|------|-------------|
| `city_id` | INT (PK) | Unique city identifier |
| `name` | VARCHAR(100) | City name (unique) |

#### **Routes Table**
Flight paths between two cities.

| Column | Type | Description |
|--------|------|-------------|
| `route_id` | INT (PK) | Unique route identifier |
| `departure_city_id` | INT (FK) | Starting city |
| `arrival_city_id` | INT (FK) | Destination city |
| `standard_fare` | DECIMAL(10,2) | Base economy fare in £ |

**Constraint:** Each route (departure + arrival pair) is unique.

#### **FlightSchedules Table**
Recurring flight timetables.

| Column | Type | Description |
|--------|------|-------------|
| `schedule_id` | INT (PK) | Unique schedule identifier |
| `route_id` | INT (FK) | Associated route |
| `departure_time` | TIME | Daily departure time |
| `arrival_time` | TIME | Daily arrival time |
| `total_capacity` | INT | Total seats (default: 130) |
| `is_active` | BOOLEAN | Schedule enabled/disabled |

**Capacity Split:** 80% Economy (104 seats), 20% Business (26 seats)

#### **FlightInstances Table**
Specific date instances of scheduled flights.

| Column | Type | Description |
|--------|------|-------------|
| `flight_instance_id` | INT (PK) | Unique instance identifier |
| `schedule_id` | INT (FK) | Parent schedule |
| `departure_date` | DATE | Specific flight date |
| `available_economy_seats` | INT | Remaining economy seats |
| `available_business_seats` | INT | Remaining business seats |

**Constraint:** Each schedule can have only one instance per date.

#### **Bookings Table**
Customer flight reservations.

| Column | Type | Description |
|--------|------|-------------|
| `booking_id` | INT (PK) | Unique booking identifier |
| `user_id` | INT (FK) | Customer who booked |
| `flight_instance_id` | INT (FK) | Booked flight instance |
| `num_seats` | INT | Number of seats booked |
| `seat_type` | ENUM | 'Economy' or 'Business' |
| `total_price` | DECIMAL(10,2) | Final price paid (£) |
| `status` | ENUM | 'Confirmed', 'Cancelled', or 'Pending' |
| `booking_date` | TIMESTAMP | When booking was made |

### Pricing Logic

**Base Fare:**
- Economy: Standard route fare
- Business: 2× Standard route fare

**Early Bird Discounts:**
- 80-90 days before departure: 25% OFF
- 60-79 days before departure: 15% OFF
- 45-59 days before departure: 10% OFF
- Less than 45 days: No discount

**Formula:**
```
Final Price = (Base Fare per Seat × Number of Seats) × (1 - Discount %)
```

### Cancellation Policy

**Refund Calculation:**
- 60+ days before departure: 100% refund (0% fee)
- 30-60 days before departure: 60% refund (40% fee)
- Less than 30 days: 0% refund (100% fee)

**Formula:**
```
Refund Amount = Total Paid - (Total Paid × Fee Percentage)
```

---



### Community Requested Features
Have an idea? [Open an issue](https://github.com/TanmoyGG/AIR_Ticket_Booking_Website--using--Python_Flask/issues) to suggest a feature!

---

## 🤝 Contributing

I welcome contributions from the community! Whether you're fixing bugs, improving documentation, or adding new features, your help is appreciated.

### How to Contribute

#### 1. Fork the Repository

Click the "Fork" button at the top right of the repository page to create your own copy.

#### 2. Clone Your Fork

```bash
git clone https://github.com/your-username/AIR_Ticket_Booking_Website--using--Python_Flask.git
cd AIR_Ticket_Booking_Website--using--Python_Flask
```

#### 3. Create a Feature Branch

```bash
# Create and switch to a new branch
git checkout -b feature/your-feature-name

# Examples:
# git checkout -b feature/add-email-notifications
# git checkout -b bugfix/fix-booking-cancel
# git checkout -b docs/improve-readme
```

#### 4. Make Your Changes

- Write clean, readable code
- Follow Python PEP 8 style guidelines
- Add comments for complex logic
- Update documentation if needed

#### 5. Test Your Changes

```bash
# Run the application
python app.py

# Test your changes thoroughly
# - Check if new features work as expected
# - Ensure existing features still work
# - Test edge cases
```

#### 6. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "Add: Brief description of your changes"

# Examples:
# git commit -m "Add: Email notification for booking confirmation"
# git commit -m "Fix: Booking cancellation refund calculation bug"
# git commit -m "Docs: Update installation instructions"
```

**Commit Message Guidelines:**
- `Add:` for new features
- `Fix:` for bug fixes
- `Update:` for changes to existing features
- `Remove:` for removing code/features
- `Docs:` for documentation changes
- `Style:` for formatting, missing semicolons, etc.
- `Refactor:` for code restructuring

#### 7. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

#### 8. Open a Pull Request

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill in the pull request template:
   - **Title:** Clear, descriptive title
   - **Description:** What changes you made and why
   - **Testing:** How you tested the changes
   - **Screenshots:** If applicable
5. Submit the pull request

### Contribution Guidelines

#### Code Style
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) Python style guide
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use descriptive variable names
- Add docstrings to functions and classes

#### Code Quality
- Write self-documenting code
- Add comments for complex algorithms
- Remove debug print statements
- Handle errors gracefully with try-except blocks
- Validate user inputs

#### Testing
- Test all new features thoroughly
- Check for edge cases
- Ensure backward compatibility
- Test on different browsers (for frontend changes)

#### Documentation
- Update README.md if needed
- Add docstrings to new functions
- Update API documentation
- Include code examples when helpful

### Reporting Bugs

Found a bug? Help us fix it!

1. **Search existing issues** to avoid duplicates
2. **Open a new issue** with:
   - **Title:** Clear, concise bug description
   - **Description:** Detailed explanation
   - **Steps to reproduce:**
     ```
     1. Go to '...'
     2. Click on '...'
     3. Scroll down to '...'
     4. See error
     ```
   - **Expected behavior:** What should happen
   - **Actual behavior:** What actually happens
   - **Screenshots:** If applicable
   - **Environment:**
     - OS: (e.g., Windows 11, Ubuntu 22.04)
     - Browser: (e.g., Chrome 120, Firefox 121)
     - Python version: (e.g., 3.10.5)
     - MySQL version: (e.g., 8.0.35)



## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.


---

## 📞 Contact

**Project Maintainer:** Tanmoy Das

- **Email:** tanmoydas180719@gmail.com
- **LinkedIn:** [Tanmoy Das](https://www.linkedin.com/in/tanmoy-das-3128a6259/)



## 🙏 Acknowledgments

This project was built with the help of amazing open-source technologies:

- **[Flask](https://flask.palletsprojects.com/)** - The Python micro web framework that made this possible
- **[Bootstrap](https://getbootstrap.com/)** - For beautiful, responsive UI components
- **[Font Awesome](https://fontawesome.com/)** - For the amazing icon library
- **[MySQL](https://www.mysql.com/)** - Reliable and robust database management
- **[bcrypt](https://pypi.org/project/bcrypt/)** - Secure password hashing
- **[ReportLab](https://www.reportlab.com/)** - Professional PDF generation
- **[Matplotlib](https://matplotlib.org/)** - Powerful data visualization
- **[jQuery](https://jquery.com/)** - Simplified DOM manipulation

---



<div align="center">

### ⭐ If you found this project helpful, please give it a star!

**Made with ❤️ and ☕ by Tanmoy Das**

*Happy Flying with Horizon Airlines!* ✈️🌍

---



</div>
