# 🚌 Cloud Bus Pass System

A web-based **Cloud Bus Pass Management System** developed using **Python Flask, SQLite, HTML, CSS, and JavaScript**. The system digitizes the traditional bus pass application and ticket booking process, allowing users to apply for bus passes, select routes, make payments, book tickets, and download approved passes.

Administrators can manage user applications, approve or reject bus pass requests, monitor bookings, and view system statistics through an admin dashboard.

---

## 📌 Project Overview

The **Cloud Bus Pass System** provides a convenient and efficient platform for managing bus transportation services digitally.

The system reduces manual paperwork and allows users to manage their bus pass and ticket-related activities from a web browser.

### 🎯 Objectives

* Digitize the bus pass application process.
* Reduce manual paperwork and processing time.
* Provide an easy-to-use interface for users.
* Allow administrators to manage applications efficiently.
* Provide online bus ticket booking.
* Provide bus route selection.
* Generate downloadable bus pass PDFs.
* Provide online payment functionality.
* Improve accessibility through a responsive web interface.

---

## ✨ Features

### 👤 User Features

* 🔐 User Registration and Login
* 👤 User Dashboard
* 📝 Online Bus Pass Application
* 🚌 Bus Route Selection
* 🔍 Search and Filter Bus Passes
* 💳 Online Payment
* 🎫 Bus Ticket Booking
* 📄 Download Bus Pass as PDF
* 📱 Mobile-Responsive Interface
* 🔔 User Notifications
* 📊 View Application Status
* ❌ Cancel Bookings
* 👤 User Profile
* 🔑 Forgot Password

### 👨‍💼 Admin Features

* 🔐 Secure Admin Login
* 📊 Admin Dashboard
* 📝 View Bus Pass Applications
* ✅ Approve Bus Pass Applications
* ❌ Reject Bus Pass Applications
* 🎫 View Ticket Bookings
* 🔍 Search and Filter Applications
* 🚌 Manage Bus Routes
* 📊 View Statistics
* 📈 Dashboard Charts
* 👥 Manage Users
* 📋 Monitor Application Status

---

## 🛠️ Technologies Used

| Technology    | Purpose                       |
| ------------- | ----------------------------- |
| 🐍 Python     | Backend Programming           |
| 🌐 Flask      | Web Application Framework     |
| 🗄️ SQLite    | Database                      |
| 🧩 SQLAlchemy | Database Management           |
| HTML5         | Web Page Structure            |
| CSS3          | Styling and Responsive Design |
| JavaScript    | Frontend Interactivity        |
| 📄 ReportLab  | PDF Generation                |
| 📊 Pandas     | Data Processing               |
| 🔢 Random     | Ticket/Reference Generation   |

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │       User          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Web Interface     │
                    │ HTML + CSS + JS     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Flask Backend    │
                    │      Python         │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       ┌────────────┐   ┌────────────┐   ┌────────────┐
       │   Users    │   │ Bus Passes │   │  Bookings  │
       └────────────┘   └────────────┘   └────────────┘
              │                │                │
              └────────────────┼────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │   SQLite Database   │
                    └─────────────────────┘
```

---

## 📂 Project Structure

```text
CloudBusPassSystem/
│
├── app.py
│
├── buspass.db
│
├── requirements.txt
│
├── README.md
│
├── templates/
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── apply_pass.html
│   ├── payment.html
│   ├── booking.html
│   ├── ticket.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   └── ...
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   ├── js/
│   │   └── script.js
│   │
│   └── images/
│
└── instance/
    └── ...
```

> The exact files and folders may vary depending on the latest version of the project.

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ciliverigouthami/CloudBusPassSystem.git
```

### 2. Open the Project Folder

```bash
cd CloudBusPassSystem
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

If you are using PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install Required Packages

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not available, install the main dependencies:

```bash
pip install flask flask-sqlalchemy reportlab pandas
```

---

## ▶️ Running the Application

Run the Flask application using:

```bash
python app.py
```

After the server starts, open the application in your browser:

```text
http://127.0.0.1:5000/
```

---

## 🔑 User Workflow

```text
Register
   ↓
Login
   ↓
User Dashboard
   ↓
Apply for Bus Pass
   ↓
Select Bus Route
   ↓
Make Payment
   ↓
Application Submitted
   ↓
Admin Reviews Application
   ↓
Approve / Reject
   ↓
User Receives Status
   ↓
Download Bus Pass PDF
```

---

## 🎫 Ticket Booking Workflow

```text
Login
   ↓
Book Your Ticket
   ↓
Select Source
   ↓
Select Destination
   ↓
Select Travel Date
   ↓
Enter Passenger Details
   ↓
Confirm Booking
   ↓
Booking Generated
   ↓
View / Cancel Booking
```

---

## 👨‍💼 Admin Workflow

```text
Admin Login
     ↓
Admin Dashboard
     ↓
View Applications
     ↓
Review User Details
     ↓
Approve / Reject Application
     ↓
View Bookings
     ↓
Monitor Users
     ↓
View Statistics
```

---

## 🗄️ Database

The system uses **SQLite** as its database.

The database stores information such as:

* User accounts
* User profiles
* Bus pass applications
* Bus routes
* Payment information
* Ticket bookings
* Application status
* Booking status
* Notifications

The database file is generated/used by the Flask application according to the configured SQLAlchemy database path.

---

## 📄 PDF Bus Pass

After a bus pass application is approved, the system can generate a **downloadable PDF bus pass**.

The PDF may contain:

* Passenger name
* Pass ID
* Source
* Destination
* Route information
* Validity information
* Pass status
* Other relevant passenger details

PDF generation is implemented using **ReportLab**.

---

## 💳 Payment Module

The system includes an online payment workflow for bus pass applications.

The payment module is designed to:

* Display the applicable pass amount.
* Collect payment information through the application interface.
* Process/record the payment status.
* Associate payment information with the relevant application.

> For a production deployment, a secure payment gateway such as Razorpay, Stripe, or another supported provider should be integrated instead of handling payment details directly.

---

## 🔔 Notifications

The system provides status-related notifications to users.

Examples include:

* Bus pass application submitted.
* Application approved.
* Application rejected.
* Booking confirmed.
* Booking cancelled.

---

## 🔍 Search and Filter

The admin/user interfaces can provide search and filtering functionality to make it easier to find:

* Bus pass applications
* Users
* Bookings
* Routes
* Application statuses

---

## 📊 Admin Dashboard

The admin dashboard provides an overview of system activity.

Possible statistics include:

```text
Total Users
     │
     ├── Total Applications
     │
     ├── Approved Passes
     │
     ├── Rejected Passes
     │
     └── Total Bookings
```

Charts and statistics help administrators monitor the system efficiently.

---

## 🔐 Security

The application includes basic security mechanisms such as:

* User authentication
* Admin authentication
* Session management
* Protected admin routes
* Database-backed user accounts
* Form validation

For production deployment, additional security measures such as password hashing, CSRF protection, secure cookies, HTTPS, and proper secret-key management should be implemented.

---

## 📱 Responsive Design

The system is designed to work across different screen sizes, including:

* 💻 Desktop
* 💻 Laptop
* 📱 Mobile
* 📲 Tablet

The frontend uses HTML5 and CSS3 to provide a responsive user interface.

---

## 🚀 Future Enhancements

The project can be further enhanced with:

* ☁️ Deployment on AWS / Azure / Google Cloud
* 💳 Real payment gateway integration
* 📧 Email notifications
* 📱 SMS notifications
* 🗺️ Live bus tracking
* 🚌 Real-time bus availability
* 🎟️ QR-code-based bus pass verification
* 🤖 AI-powered travel assistant
* 🔐 Two-factor authentication
* 📊 Advanced analytics
* 🌐 Multi-language support
* 📲 Progressive Web App (PWA)
* ☁️ Cloud database integration

---

## 🧪 Testing

The application should be tested for:

* User registration
* User login
* Admin login
* Bus pass application
* Route selection
* Payment workflow
* Application approval/rejection
* Ticket booking
* Ticket cancellation
* PDF generation
* Search and filtering
* Responsive design
* Database operations

---

## 🐛 Troubleshooting

### Flask-SQLAlchemy Error

If you see:

```text
ModuleNotFoundError: No module named 'flask_sqlalchemy'
```

Install the package:

```bash
pip install flask-sqlalchemy
```

### Flask Not Found

If Flask is missing:

```bash
pip install flask
```

### ReportLab Error

Install ReportLab:

```bash
pip install reportlab
```

### Check Installed Packages

```bash
pip list
```

---

## 👩‍💻 Developer

**Ciliveri Gouthami**

B.Tech – Artificial Intelligence & Machine Learning

Kakatiya Institute of Technology and Science for Women

---

## 📌 Project Type

**Academic / Educational Project**

**Domain:** Cloud Computing / Web Application / Transportation Management

**Backend:** Python Flask

**Database:** SQLite

---

## 📜 License

This project is developed for educational and academic purposes.

You are free to modify and improve the project for learning and demonstration purposes.

---

## ⭐ Acknowledgement

This project was developed as part of an academic/project learning initiative to demonstrate the practical implementation of:

* Python programming
* Flask web development
* Database management
* Cloud-based application concepts
* Frontend development
* Authentication
* Online booking
* PDF generation
* Admin management

---

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.

**GitHub Repository:**
https://github.com/ciliverigouthami/CloudBusPassSystem
