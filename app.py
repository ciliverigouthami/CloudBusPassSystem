from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random

app = Flask(__name__)

# =========================================================
# SECRET KEY
# =========================================================

app.secret_key = "cloud_bus_pass_secret_key"


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///buspass.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================================================
# USER TABLE
# =========================================================

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(100), unique=True, nullable=False)

    phone = db.Column(db.String(15), nullable=False)

    password = db.Column(db.String(100), nullable=False)

    address = db.Column(db.String(200), nullable=False)


# =========================================================
# BUS PASS TABLE
# =========================================================

class BusPass(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=False)

    name = db.Column(db.String(100), nullable=False)

    age = db.Column(db.Integer, nullable=False)

    gender = db.Column(db.String(20), nullable=False)

    source = db.Column(db.String(100), nullable=False)

    destination = db.Column(db.String(100), nullable=False)

    pass_type = db.Column(db.String(50), nullable=False)

    start_date = db.Column(db.String(20), nullable=False)

    status_record = db.relationship(
        "ApplicationStatus",
        backref="application",
        uselist=False,
        cascade="all, delete-orphan"
    )


# =========================================================
# APPLICATION STATUS TABLE
# =========================================================

class ApplicationStatus(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    application_id = db.Column(
        db.Integer,
        db.ForeignKey("bus_pass.id"),
        nullable=False,
        unique=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Submitted"
    )


# =========================================================
# ADMIN TABLE
# =========================================================

class Admin(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(100),
        nullable=False
    )


# =========================================================
# TICKET BOOKING TABLE
# =========================================================

class TicketBooking(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    booking_id = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        nullable=False
    )

    source = db.Column(
        db.String(100),
        nullable=False
    )

    destination = db.Column(
        db.String(100),
        nullable=False
    )

    travel_date = db.Column(
        db.String(20),
        nullable=False
    )

    bus = db.Column(
        db.String(100),
        nullable=False
    )

    passengers = db.Column(
        db.Integer,
        nullable=False
    )

    seat_type = db.Column(
        db.String(50),
        nullable=False
    )

    booking_status = db.Column(
        db.String(30),
        nullable=False,
        default="Confirmed"
    )

    booking_date = db.Column(
        db.String(30),
        nullable=False
    )


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

with app.app_context():

    db.create_all()

    existing_admin = Admin.query.filter_by(
        email="admin@buspass.com"
    ).first()

    if not existing_admin:

        default_admin = Admin(
            name="Bus Pass Administrator",
            email="admin@buspass.com",
            password="admin123"
        )

        db.session.add(default_admin)
        db.session.commit()


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        address = request.form["address"]

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            return render_template(
                "register.html",
                error="Email already registered. Please use another email."
            )

        new_user = User(
            name=name,
            email=email,
            phone=phone,
            password=password,
            address=address
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )


# =========================================================
# USER LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(
            email=email
        ).first()

        if user and user.password == password:

            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_email"] = user.email

            return redirect(
                url_for("dashboard")
            )

        return render_template(
            "login.html",
            error="Invalid email or password."
        )

    return render_template(
        "login.html"
    )


# =========================================================
# USER DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    user = User.query.get(
        session["user_id"]
    )

    applications = BusPass.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        BusPass.id.desc()
    ).all()

    bookings = TicketBooking.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        TicketBooking.id.desc()
    ).all()

    return render_template(
        "dashboard.html",
        user=user,
        applications=applications,
        bookings=bookings
    )


# =========================================================
# APPLY FOR BUS PASS
# =========================================================

@app.route("/apply", methods=["GET", "POST"])
def apply():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        source = request.form["source"]
        destination = request.form["destination"]
        pass_type = request.form["pass_type"]
        start_date = request.form["start_date"]

        new_pass = BusPass(
            user_id=session["user_id"],
            name=name,
            age=age,
            gender=gender,
            source=source,
            destination=destination,
            pass_type=pass_type,
            start_date=start_date
        )

        db.session.add(new_pass)
        db.session.commit()

        new_status = ApplicationStatus(
            application_id=new_pass.id,
            status="Submitted"
        )

        db.session.add(new_status)
        db.session.commit()

        return redirect(
            url_for(
                "application_success",
                application_id=new_pass.id
            )
        )

    user = User.query.get(
        session["user_id"]
    )

    return render_template(
        "apply.html",
        user=user
    )


# =========================================================
# APPLICATION SUCCESS
# =========================================================

@app.route("/application-success/<int:application_id>")
def application_success(application_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    application = BusPass.query.filter_by(
        id=application_id,
        user_id=session["user_id"]
    ).first()

    if application is None:

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "success.html",
        application=application
    )


# =========================================================
# TICKET BOOKING
# =========================================================

@app.route("/book-ticket", methods=["GET", "POST"])
def book_ticket():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        source = request.form["source"]

        destination = request.form["destination"]

        travel_date = request.form["travel_date"]

        bus = request.form["bus"]

        passengers = request.form["passengers"]

        seat_type = request.form["seat_type"]

        booking_id = (
            "CBT-"
            + datetime.now().strftime("%Y%m%d")
            + "-"
            + str(random.randint(1000, 9999))
        )

        new_booking = TicketBooking(

            booking_id=booking_id,

            user_id=session["user_id"],

            source=source,

            destination=destination,

            travel_date=travel_date,

            bus=bus,

            passengers=int(passengers),

            seat_type=seat_type,

            booking_status="Confirmed",

            booking_date=datetime.now().strftime(
                "%d-%m-%Y %I:%M %p"
            )
        )

        db.session.add(new_booking)

        db.session.commit()

        return redirect(
            url_for(
                "booking_confirmation",
                booking_id=new_booking.booking_id
            )
        )

    user = User.query.get(
        session["user_id"]
    )

    return render_template(
        "book_ticket.html",
        user=user
    )


# =========================================================
# BOOKING CONFIRMATION
# =========================================================

@app.route("/booking-confirmation/<booking_id>")
def booking_confirmation(booking_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    booking = TicketBooking.query.filter_by(
        booking_id=booking_id,
        user_id=session["user_id"]
    ).first()

    if booking is None:

        return redirect(
            url_for("dashboard")
        )

    user = User.query.get(
        session["user_id"]
    )

    return render_template(
        "booking_confirmation.html",
        booking=booking,
        user=user
    )

# =========================================================
# CANCEL TICKET
# =========================================================

@app.route(
    "/cancel-ticket/<booking_id>"
)
def cancel_ticket(booking_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    booking = TicketBooking.query.filter_by(
        booking_id=booking_id,
        user_id=session["user_id"]
    ).first()

    if booking is None:

        return redirect(
            url_for("dashboard")
        )

    # Change booking status to Cancelled
    booking.booking_status = "Cancelled"

    db.session.commit()

    return redirect(
        url_for("dashboard")
    )
# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        email = request.form["email"]

        password = request.form["password"]

        admin = Admin.query.filter_by(
            email=email
        ).first()

        if admin and admin.password == password:

            session["admin_id"] = admin.id

            session["admin_name"] = admin.name

            return redirect(
                url_for("admin_dashboard")
            )

        return render_template(
            "admin_login.html",
            error="Invalid admin email or password."
        )

    return render_template(
        "admin_login.html"
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin-dashboard")
def admin_dashboard():

    if "admin_id" not in session:

        return redirect(
            url_for("admin_login")
        )

    applications = BusPass.query.order_by(
        BusPass.id.desc()
    ).all()

    bookings = TicketBooking.query.order_by(
        TicketBooking.id.desc()
    ).all()

    return render_template(
        "admin_dashboard.html",
        applications=applications,
        bookings=bookings
    )


# =========================================================
# APPROVE APPLICATION
# =========================================================

@app.route("/admin/approve/<int:application_id>")
def approve_application(application_id):

    if "admin_id" not in session:

        return redirect(
            url_for("admin_login")
        )

    application = BusPass.query.get_or_404(
        application_id
    )

    status = ApplicationStatus.query.filter_by(
        application_id=application.id
    ).first()

    if status:

        status.status = "Approved"

    else:

        status = ApplicationStatus(
            application_id=application.id,
            status="Approved"
        )

        db.session.add(status)

    db.session.commit()

    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# REJECT APPLICATION
# =========================================================

@app.route("/admin/reject/<int:application_id>")
def reject_application(application_id):

    if "admin_id" not in session:

        return redirect(
            url_for("admin_login")
        )

    application = BusPass.query.get_or_404(
        application_id
    )

    status = ApplicationStatus.query.filter_by(
        application_id=application.id
    ).first()

    if status:

        status.status = "Rejected"

    else:

        status = ApplicationStatus(
            application_id=application.id,
            status="Rejected"
        )

        db.session.add(status)

    db.session.commit()

    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/admin-logout")
def admin_logout():

    session.pop(
        "admin_id",
        None
    )

    session.pop(
        "admin_name",
        None
    )

    return redirect(
        url_for("home")
    )


# =========================================================
# USER LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )