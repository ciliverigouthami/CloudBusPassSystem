from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    send_file
)

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
import random
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from dotenv import load_dotenv
from email_utils import send_email


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)

app.secret_key = "cloud_bus_pass_secret_key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///buspass.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================================================
# USER MODEL
# =========================================================

class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    phone = db.Column(
        db.String(15),
        nullable=False
    )

    password = db.Column(
        db.String(100),
        nullable=False
    )

    address = db.Column(
        db.String(200),
        nullable=False
    )


# =========================================================
# BUS PASS MODEL
# =========================================================

class BusPass(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        nullable=False
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    age = db.Column(
        db.Integer,
        nullable=False
    )

    gender = db.Column(
        db.String(20),
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

    pass_type = db.Column(
        db.String(50),
        nullable=False
    )

    start_date = db.Column(
        db.String(20),
        nullable=False
    )

    status_record = db.relationship(
        "ApplicationStatus",
        backref="application",
        uselist=False,
        cascade="all, delete-orphan"
    )

    payment = db.relationship(
        "Payment",
        backref="application",
        uselist=False,
        cascade="all, delete-orphan"
    )


# =========================================================
# APPLICATION STATUS MODEL
# =========================================================

class ApplicationStatus(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

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
# PAYMENT MODEL
# =========================================================

class Payment(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    application_id = db.Column(
        db.Integer,
        db.ForeignKey("bus_pass.id"),
        nullable=False,
        unique=True
    )

    user_id = db.Column(
        db.Integer,
        nullable=False
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    payment_method = db.Column(
        db.String(50),
        nullable=False
    )

    transaction_id = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    payment_status = db.Column(
        db.String(30),
        nullable=False,
        default="Success"
    )

    # IMPORTANT:
    # Existing database may contain formatted date strings.
    # String avoids SQLAlchemy ISO datetime conversion errors.
    payment_date = db.Column(
        db.String(30),
        nullable=False
    )


# =========================================================
# ADMIN MODEL
# =========================================================

class Admin(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

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
# TICKET BOOKING MODEL
# =========================================================

class TicketBooking(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

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

    # IMPORTANT:
    # Existing database contains values such as:
    # 24-08-2026 10:58 AM
    #
    # Therefore this MUST remain String.
    booking_date = db.Column(
        db.String(30),
        nullable=False
    )


# =========================================================
# INDIA-WIDE CITY COORDINATES
# =========================================================

CITY_COORDINATES = {

    # -------------------------
    # TELANGANA
    # -------------------------

    "hyderabad": (17.3850, 78.4867),
    "secunderabad": (17.4399, 78.4983),
    "warangal": (17.9784, 79.5941),
    "nizamabad": (18.6725, 78.0941),
    "karimnagar": (18.4386, 79.1288),
    "khammam": (17.2473, 80.1514),
    "nalgonda": (17.0575, 79.2684),
    "adilabad": (19.6641, 78.5320),
    "siddipet": (18.1018, 78.8520),
    "mahbubnagar": (16.7488, 77.9850),

    # -------------------------
    # ANDHRA PRADESH
    # -------------------------

    "vijayawada": (16.5062, 80.6480),
    "visakhapatnam": (17.6868, 83.2185),
    "tirupati": (13.6288, 79.4192),
    "guntur": (16.3067, 80.4365),
    "nellore": (14.4426, 79.9865),
    "kurnool": (15.8281, 78.0373),
    "kadapa": (14.4673, 78.8242),
    "rajahmundry": (16.9891, 81.2293),
    "ongole": (15.5057, 80.0499),
    "anantapur": (14.6819, 77.6006),

    # -------------------------
    # KARNATAKA
    # -------------------------

    "bengaluru": (12.9716, 77.5946),
    "mysuru": (12.2958, 76.6394),
    "mangaluru": (12.9141, 74.8560),
    "hubballi": (15.3647, 75.1240),
    "belagavi": (15.8497, 74.4977),
    "shivamogga": (13.9299, 75.5681),
    "ballari": (15.1394, 76.9214),
    "kalaburagi": (17.3297, 76.8343),
    "davangere": (14.4644, 75.9218),
    "tumakuru": (13.3379, 77.1173),

    # -------------------------
    # TAMIL NADU
    # -------------------------

    "chennai": (13.0827, 80.2707),
    "coimbatore": (11.0168, 76.9558),
    "madurai": (9.9252, 78.1198),
    "salem": (11.6643, 78.1460),
    "tiruchirappalli": (10.7905, 78.7047),
    "tirunelveli": (8.7139, 77.7567),
    "vellore": (12.9165, 79.1325),
    "erode": (11.3410, 77.7172),
    "thoothukudi": (8.7642, 78.1348),
    "thanjavur": (10.7870, 79.1378),

    # -------------------------
    # KERALA
    # -------------------------

    "kochi": (9.9312, 76.2673),
    "thiruvananthapuram": (8.5241, 76.9366),
    "kozhikode": (11.2588, 75.7804),
    "thrissur": (10.5276, 76.2144),
    "kollam": (8.8932, 76.6141),
    "kannur": (11.8745, 75.3704),
    "alappuzha": (9.4981, 76.3388),
    "palakkad": (10.7867, 76.6548),

    # -------------------------
    # MAHARASHTRA
    # -------------------------

    "mumbai": (19.0760, 72.8777),
    "pune": (18.5204, 73.8567),
    "nagpur": (21.1458, 79.0882),
    "nashik": (19.9975, 73.7898),
    "aurangabad": (19.8762, 75.3433),
    "solapur": (17.6599, 75.9064),
    "kolhapur": (16.7050, 74.2433),
    "amravati": (20.9374, 77.7796),
    "nanded": (19.1383, 77.3210),
    "thane": (19.2183, 72.9781),

    # -------------------------
    # GUJARAT
    # -------------------------

    "ahmedabad": (23.0225, 72.5714),
    "surat": (21.1702, 72.8311),
    "vadodara": (22.3072, 73.1812),
    "rajkot": (22.3039, 70.8022),
    "bhavnagar": (21.7645, 72.1519),
    "jamnagar": (22.4707, 70.0577),
    "gandhinagar": (23.2156, 72.6369),
    "anand": (22.5645, 72.9289),

    # -------------------------
    # RAJASTHAN
    # -------------------------

    "jaipur": (26.9124, 75.7873),
    "jodhpur": (26.2389, 73.0243),
    "udaipur": (24.5854, 73.7125),
    "kota": (25.2138, 75.8648),
    "ajmer": (26.4499, 74.6399),
    "bikaner": (28.0229, 73.3119),
    "alwar": (27.5530, 76.6346),

    # -------------------------
    # DELHI / NORTH INDIA
    # -------------------------

    "delhi": (28.6139, 77.2090),
    "chandigarh": (30.7333, 76.7794),
    "amritsar": (31.6340, 74.8723),
    "ludhiana": (30.9010, 75.8573),
    "jalandhar": (31.3260, 75.5762),
    "srinagar": (34.0837, 74.7973),
    "jammu": (32.7266, 74.8570),

    # -------------------------
    # UTTAR PRADESH
    # -------------------------

    "lucknow": (26.8467, 80.9462),
    "agra": (27.1767, 78.0081),
    "kanpur": (26.4499, 80.3319),
    "varanasi": (25.3176, 82.9739),
    "prayagraj": (25.4358, 81.8463),
    "meerut": (28.9845, 77.7064),
    "ghaziabad": (28.6692, 77.4538),
    "noida": (28.5355, 77.3910),
    "bareilly": (28.3670, 79.4304),
    "gorakhpur": (26.7606, 83.3732),

    # -------------------------
    # UTTARAKHAND
    # -------------------------

    "dehradun": (30.3165, 78.0322),
    "haridwar": (29.9457, 78.1642),
    "rishikesh": (30.0869, 78.2676),
    "haldwani": (29.2183, 79.5130),

    # -------------------------
    # WEST BENGAL
    # -------------------------

    "kolkata": (22.5726, 88.3639),
    "siliguri": (26.7271, 88.3953),
    "durgapur": (23.5204, 87.3119),
    "asansol": (23.6739, 86.9524),

    # -------------------------
    # ODISHA
    # -------------------------

    "bhubaneswar": (20.2961, 85.8245),
    "cuttack": (20.4625, 85.8830),
    "rourkela": (22.2604, 84.8536),
    "berhampur": (19.3150, 84.7941),

    # -------------------------
    # JHARKHAND
    # -------------------------

    "ranchi": (23.3441, 85.3096),
    "jamshedpur": (22.8046, 86.2029),
    "dhanbad": (23.7957, 86.4304),
    "bokaro": (23.6693, 86.1511),

    # -------------------------
    # BIHAR
    # -------------------------

    "patna": (25.5941, 85.1376),
    "gaya": (24.7914, 85.0002),
    "muzaffarpur": (26.1209, 85.3647),
    "bhagalpur": (25.2425, 86.9842),

    # -------------------------
    # MADHYA PRADESH
    # -------------------------

    "bhopal": (23.2599, 77.4126),
    "indore": (22.7196, 75.8577),
    "gwalior": (26.2183, 78.1828),
    "jabalpur": (23.1815, 79.9864),
    "ujjain": (23.1765, 75.7885),

    # -------------------------
    # CHHATTISGARH
    # -------------------------

    "raipur": (21.2514, 81.6296),
    "bilaspur": (22.0797, 82.1409),
    "durg": (21.1904, 81.2849),

    # -------------------------
    # ASSAM / NORTHEAST
    # -------------------------

    "guwahati": (26.1445, 91.7362),
    "dibrugarh": (27.4728, 94.9120),
    "silchar": (24.8333, 92.7789),

    # -------------------------
    # GOA
    # -------------------------

    "panaji": (15.4909, 73.8278),
    "margao": (15.2832, 73.9862),

    # -------------------------
    # PUNJAB / HARYANA
    # -------------------------

    "gurugram": (28.4595, 77.0266),
    "faridabad": (28.4089, 77.3178),
    "panipat": (29.3909, 76.9635),
    "rohtak": (28.8955, 76.6066),

    # -------------------------
    # HIMACHAL PRADESH
    # -------------------------

    "shimla": (31.1048, 77.1734),
    "dharamshala": (32.2190, 76.3234),

    # -------------------------
    # PUDUCHERRY
    # -------------------------

    "pondicherry": (11.9416, 79.8083)
}


# =========================================================
# ORIGINAL HYDERABAD ROUTE PRICES
# DO NOT CHANGE THESE VALUES
# =========================================================

ROUTE_PRICES = {

    ("hyderabad", "secunderabad"): {
        "Monthly": 300,
        "Quarterly": 800,
        "Yearly": 2800
    },

    ("hyderabad", "kukatpally"): {
        "Monthly": 350,
        "Quarterly": 950,
        "Yearly": 3200
    },

    ("hyderabad", "uppal"): {
        "Monthly": 350,
        "Quarterly": 950,
        "Yearly": 3200
    },

    ("hyderabad", "lb nagar"): {
        "Monthly": 400,
        "Quarterly": 1050,
        "Yearly": 3600
    },

    ("secunderabad", "kukatpally"): {
        "Monthly": 400,
        "Quarterly": 1050,
        "Yearly": 3600
    },

    ("secunderabad", "uppal"): {
        "Monthly": 300,
        "Quarterly": 800,
        "Yearly": 2800
    },

    ("secunderabad", "lb nagar"): {
        "Monthly": 450,
        "Quarterly": 1200,
        "Yearly": 4000
    },

    ("hyderabad", "gachibowli"): {
        "Monthly": 500,
        "Quarterly": 1300,
        "Yearly": 4800
    }
}


# Add local Hyderabad destinations to the city list.
# These don't need coordinates because they already have
# special route prices.
CITY_COORDINATES.update({

    "kukatpally": (17.4849, 78.4138),
    "uppal": (17.4065, 78.5591),
    "lb nagar": (17.3457, 78.5522),
    "gachibowli": (17.4401, 78.3489)

})


# =========================================================
# DISTANCE-BASED PRICE TIERS
# =========================================================

DISTANCE_PRICE_TIERS = [

    # maximum distance, monthly, quarterly, yearly

    (20, 300, 800, 2800),

    (50, 400, 1050, 3600),

    (100, 500, 1300, 4800),

    (200, 700, 1800, 6500),

    (400, 1000, 2700, 9500),

    (700, 1400, 3800, 13000),

    (1000, 1800, 4800, 16500),

    (1500, 2300, 6200, 21000),

    (float("inf"), 2800, 7500, 25000)

]


# =========================================================
# CALCULATE DISTANCE
# =========================================================

def calculate_distance(source, destination):

    source_key = source.strip().lower()
    destination_key = destination.strip().lower()

    if source_key not in CITY_COORDINATES:
        return None

    if destination_key not in CITY_COORDINATES:
        return None

    if source_key == destination_key:
        return 0

    from math import (
        radians,
        sin,
        cos,
        sqrt,
        atan2
    )

    lat1, lon1 = CITY_COORDINATES[source_key]

    lat2, lon2 = CITY_COORDINATES[destination_key]

    earth_radius = 6371

    lat1 = radians(lat1)
    lon1 = radians(lon1)

    lat2 = radians(lat2)
    lon2 = radians(lon2)

    difference_latitude = lat2 - lat1
    difference_longitude = lon2 - lon1

    a = (
        sin(difference_latitude / 2) ** 2
        +
        cos(lat1)
        *
        cos(lat2)
        *
        sin(difference_longitude / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    distance = earth_radius * c

    return round(distance, 2)


# =========================================================
# DISTANCE-BASED PRICE
# =========================================================

def get_distance_based_price(
    distance,
    pass_type
):

    if distance is None:
        return None

    for (
        maximum_distance,
        monthly_price,
        quarterly_price,
        yearly_price
    ) in DISTANCE_PRICE_TIERS:

        if distance <= maximum_distance:

            prices = {

                "Monthly": monthly_price,

                "Quarterly": quarterly_price,

                "Yearly": yearly_price

            }

            return prices.get(pass_type)

    return None


# =========================================================
# ROUTE PRICE
# =========================================================

def get_route_price(
    source,
    destination,
    pass_type
):

    source_key = source.strip().lower()

    destination_key = destination.strip().lower()

    # First check exact direction.
    existing_route = ROUTE_PRICES.get(
        (source_key, destination_key)
    )

    if existing_route is not None:

        return existing_route.get(
            pass_type
        )

    # Check reverse direction too.
    # This means:
    # Hyderabad -> Secunderabad
    # and
    # Secunderabad -> Hyderabad
    # use the same special price.

    reverse_route = ROUTE_PRICES.get(
        (destination_key, source_key)
    )

    if reverse_route is not None:

        return reverse_route.get(
            pass_type
        )

    if source_key == destination_key:

        return None

    distance = calculate_distance(
        source_key,
        destination_key
    )

    if distance is None:

        return None

    return get_distance_based_price(
        distance,
        pass_type
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

        db.session.add(
            default_admin
        )

        db.session.commit()


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        address = request.form.get(
            "address",
            ""
        ).strip()

        if not all([
            name,
            email,
            phone,
            password,
            address
        ]):

            return render_template(
                "register.html",
                error="Please fill in all fields."
            )

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

        db.session.add(
            new_user
        )

        db.session.commit()

        return redirect(
            url_for(
                "login",
                success="Registration successful. Please login."
            )
        )

    return render_template(
        "register.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

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

    success = request.args.get(
        "success"
    )

    return render_template(
        "login.html",
        success=success
    )


# =========================================================
# FORGOT PASSWORD
# =========================================================

@app.route(
    "/forgot-password",
    methods=["GET", "POST"]
)
def forgot_password():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        user = User.query.filter_by(
            email=email
        ).first()

        if not user:

            return render_template(
                "forgot_password.html",
                error="No account found with that email address."
            )

        otp = str(
            random.randint(
                100000,
                999999
            )
        )

        session["reset_email"] = user.email

        session["reset_otp"] = otp

        session["reset_otp_time"] = datetime.now().timestamp()

        email_subject = (
            "Cloud Bus Pass System - Password Reset OTP"
        )

        email_body = f"""
Hello {user.name},

Your password reset OTP is:

{otp}

This OTP is valid for 10 minutes.

If you did not request a password reset,
please ignore this email.

Regards,
Cloud Bus Pass System
"""

        try:

            send_email(

                application_user_email=user.email,

                subject=email_subject,

                body=email_body

            )

        except Exception as error:

            print(
                "Email sending error:",
                error
            )

        return redirect(
            url_for(
                "reset_password"
            )
        )

    return render_template(
        "forgot_password.html"
    )


# =========================================================
# RESET PASSWORD
# =========================================================

@app.route(
    "/reset-password",
    methods=["GET", "POST"]
)
def reset_password():

    if "reset_email" not in session:

        return redirect(
            url_for("forgot_password")
        )

    if request.method == "POST":

        otp = request.form.get(
            "otp",
            ""
        ).strip()

        new_password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        saved_otp = session.get(
            "reset_otp"
        )

        otp_time = session.get(
            "reset_otp_time"
        )

        if not saved_otp or not otp_time:

            return render_template(
                "reset_password.html",
                error="OTP session expired. Please request a new OTP."
            )

        current_time = datetime.now().timestamp()

        if current_time - otp_time > 600:

            session.pop(
                "reset_email",
                None
            )

            session.pop(
                "reset_otp",
                None
            )

            session.pop(
                "reset_otp_time",
                None
            )

            return render_template(
                "forgot_password.html",
                error="OTP expired. Please request a new OTP."
            )

        if otp != saved_otp:

            return render_template(
                "reset_password.html",
                error="Invalid OTP."
            )

        if len(new_password) < 6:

            return render_template(
                "reset_password.html",
                error="Password must contain at least 6 characters."
            )

        if new_password != confirm_password:

            return render_template(
                "reset_password.html",
                error="Passwords do not match."
            )

        user = User.query.filter_by(
            email=session["reset_email"]
        ).first()

        if not user:

            return redirect(
                url_for("forgot_password")
            )

        user.password = new_password

        db.session.commit()

        session.pop(
            "reset_email",
            None
        )

        session.pop(
            "reset_otp",
            None
        )

        session.pop(
            "reset_otp_time",
            None
        )

        return redirect(
            url_for(
                "login",
                success="Password reset successful. Please login."
            )
        )

    return render_template(
        "reset_password.html"
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

    if user is None:

        session.clear()

        return redirect(
            url_for("login")
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
# USER PROFILE
# =========================================================

@app.route(
    "/profile",
    methods=["GET", "POST"]
)
def profile():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    user = User.query.get(
        session["user_id"]
    )

    if user is None:

        session.clear()

        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        address = request.form.get(
            "address",
            ""
        ).strip()

        new_password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if not name or not phone or not address:

            return render_template(
                "profile.html",
                user=user,
                error="Please fill in all required fields."
            )

        if not phone.isdigit() or len(phone) != 10:

            return render_template(
                "profile.html",
                user=user,
                error="Phone number must contain exactly 10 digits."
            )

        if new_password:

            if len(new_password) < 6:

                return render_template(
                    "profile.html",
                    user=user,
                    error="Password must contain at least 6 characters."
                )

            if new_password != confirm_password:

                return render_template(
                    "profile.html",
                    user=user,
                    error="Passwords do not match."
                )

            user.password = new_password

        user.name = name

        user.phone = phone

        user.address = address

        db.session.commit()

        session["user_name"] = user.name

        session["user_email"] = user.email

        return render_template(
            "profile.html",
            user=user,
            success="Profile updated successfully."
        )

    return render_template(
        "profile.html",
        user=user
    )


# =========================================================
# APPLY FOR BUS PASS
# =========================================================

@app.route(
    "/apply",
    methods=["GET", "POST"]
)
def apply():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        age = request.form.get(
            "age",
            ""
        ).strip()

        gender = request.form.get(
            "gender",
            ""
        ).strip()

        source = request.form.get(
            "source",
            ""
        ).strip()

        destination = request.form.get(
            "destination",
            ""
        ).strip()

        pass_type = request.form.get(
            "pass_type",
            ""
        ).strip()

        start_date = request.form.get(
            "start_date",
            ""
        ).strip()

        if not all([
            name,
            age,
            gender,
            source,
            destination,
            pass_type,
            start_date
        ]):

            return render_template(
                "apply.html",
                cities=sorted(
                    CITY_COORDINATES.keys()
                ),
                error="Please fill in all fields."
            )

        try:

            age_value = int(age)

            if age_value <= 0:

                raise ValueError

        except ValueError:

            return render_template(
                "apply.html",
                cities=sorted(
                    CITY_COORDINATES.keys()
                ),
                error="Please enter a valid age."
            )

        try:

            datetime.strptime(
                start_date,
                "%Y-%m-%d"
            )

        except ValueError:

            return render_template(
                "apply.html",
                cities=sorted(
                    CITY_COORDINATES.keys()
                ),
                error="Please select a valid start date."
            )

        if source.lower() == destination.lower():

            return render_template(
                "apply.html",
                cities=sorted(
                    CITY_COORDINATES.keys()
                ),
                error="Source and destination cannot be the same."
            )

        amount = get_route_price(
            source,
            destination,
            pass_type
        )

        if amount is None:

            return render_template(
                "apply.html",
                cities=sorted(
                    CITY_COORDINATES.keys()
                ),
                error="Unable to calculate route price. Please select valid cities."
            )

        new_pass = BusPass(

            user_id=session["user_id"],

            name=name,

            age=age_value,

            gender=gender,

            source=source,

            destination=destination,

            pass_type=pass_type,

            start_date=start_date

        )

        db.session.add(
            new_pass
        )

        db.session.commit()

        new_status = ApplicationStatus(

            application_id=new_pass.id,

            status="Submitted"

        )

        db.session.add(
            new_status
        )

        db.session.commit()

        return redirect(
            url_for(
                "payment",
                application_id=new_pass.id
            )
        )

    return render_template(
        "apply.html",
        cities=sorted(
            CITY_COORDINATES.keys()
        )
    )


# =========================================================
# CALCULATE PASS VALID UNTIL DATE
# =========================================================

def calculate_valid_until(
    start_date,
    pass_type
):

    try:

        start = datetime.strptime(
            start_date,
            "%Y-%m-%d"
        ).date()

    except Exception:

        return ""

    if pass_type == "Monthly":

        valid_until = start + timedelta(
            days=30
        )

    elif pass_type == "Quarterly":

        valid_until = start + timedelta(
            days=90
        )

    elif pass_type == "Yearly":

        valid_until = start + timedelta(
            days=365
        )

    else:

        valid_until = start

    return valid_until.strftime(
        "%d-%m-%Y"
    )


# =========================================================
# PAYMENT
# =========================================================

@app.route(
    "/payment/<int:application_id>",
    methods=["GET", "POST"]
)
def payment(application_id):

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

    amount = get_route_price(

        application.source,

        application.destination,

        application.pass_type

    )

    if amount is None:

        return redirect(
            url_for("dashboard")
        )

    existing_payment = Payment.query.filter_by(
        application_id=application.id
    ).first()

    if request.method == "POST":

        payment_method = request.form.get(
            "payment_method",
            ""
        ).strip()

        if not payment_method:

            return render_template(
                "payment.html",
                application=application,
                amount=amount,
                error="Please select a payment method."
            )

        if existing_payment:

            return redirect(
                url_for(
                    "application_success",
                    application_id=application.id
                )
            )

        transaction_id = (
            "TXN"
            +
            datetime.now().strftime(
                "%Y%m%d%H%M%S"
            )
            +
            str(
                random.randint(
                    1000,
                    9999
                )
            )
        )

        new_payment = Payment(

            application_id=application.id,

            user_id=session["user_id"],

            amount=amount,

            payment_method=payment_method,

            transaction_id=transaction_id,

            payment_status="Success",

            payment_date=datetime.now().strftime(
                "%d-%m-%Y %I:%M %p"
            )

        )

        db.session.add(
            new_payment
        )

        db.session.commit()

        return redirect(
            url_for(
                "application_success",
                application_id=application.id
            )
        )

    return render_template(
        "payment.html",
        application=application,
        amount=amount
    )


# =========================================================
# APPLICATION SUCCESS
# =========================================================

@app.route(
    "/application-success/<int:application_id>"
)
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

    payment_record = Payment.query.filter_by(
        application_id=application.id
    ).first()

    amount = None

    if payment_record:

        amount = payment_record.amount

    else:

        amount = get_route_price(

            application.source,

            application.destination,

            application.pass_type

        )

    return render_template(
        "application_success.html",
        application=application,
        payment=payment_record,
        amount=amount
    )


# =========================================================
# DOWNLOAD BUS PASS PDF
# =========================================================

@app.route(
    "/download-pass/<int:application_id>"
)
def download_pass(application_id):

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

    status = ApplicationStatus.query.filter_by(
        application_id=application.id
    ).first()

    if not status or status.status != "Approved":

        return redirect(
            url_for("dashboard")
        )

    payment_record = Payment.query.filter_by(
        application_id=application.id
    ).first()

    if payment_record:

        amount = payment_record.amount

    else:

        amount = get_route_price(

            application.source,

            application.destination,

            application.pass_type

        )

    valid_until = calculate_valid_until(

        application.start_date,

        application.pass_type

    )

    buffer = BytesIO()

    document = SimpleDocTemplate(

        buffer,

        pagesize=A4,

        rightMargin=40,

        leftMargin=40,

        topMargin=40,

        bottomMargin=40

    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(

        "BusPassTitle",

        parent=styles["Title"],

        alignment=TA_CENTER,

        fontSize=20,

        spaceAfter=20

    )

    normal_style = ParagraphStyle(

        "BusPassNormal",

        parent=styles["Normal"],

        fontSize=11,

        leading=18

    )

    story = []

    story.append(
        Paragraph(
            "CLOUD BUS PASS",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Official Bus Pass",
            ParagraphStyle(
                "subtitle",
                parent=styles["Normal"],
                alignment=TA_CENTER,
                fontSize=12,
                spaceAfter=20
            )
        )
    )

    data = [

        ["Application ID", str(application.id)],

        ["Name", application.name],

        ["Age", str(application.age)],

        ["Gender", application.gender],

        ["Source", application.source],

        ["Destination", application.destination],

        ["Pass Type", application.pass_type],

        ["Start Date", application.start_date],

        ["Valid Until", valid_until],

        [
            "Amount",
            "₹" + str(amount)
        ],

        ["Status", "Approved"]

    ]

    table = Table(
        data,
        colWidths=[150, 300]
    )

    table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.lightgrey
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, -1),
                colors.black
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                1,
                colors.grey
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, -1),
                "Helvetica"
            ),

            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "PADDING",
                (0, 0),
                (-1, -1),
                8
            )

        ])
    )

    story.append(
        table
    )

    story.append(
        Spacer(
            1,
            20
        )
    )

    story.append(
        Paragraph(
            "This is a digitally generated bus pass.",
            normal_style
        )
    )

    document.build(
        story
    )

    buffer.seek(0)

    return send_file(

        buffer,

        as_attachment=True,

        download_name=(
            f"bus_pass_{application.id}.pdf"
        ),

        mimetype="application/pdf"

    )


# =========================================================
# BOOK TICKET
# =========================================================

@app.route(
    "/book-ticket",
    methods=["GET", "POST"]
)
def book_ticket():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        source = request.form.get(
            "source",
            ""
        ).strip()

        destination = request.form.get(
            "destination",
            ""
        ).strip()

        travel_date = request.form.get(
            "travel_date",
            ""
        ).strip()

        bus = request.form.get(
            "bus",
            ""
        ).strip()

        passengers = request.form.get(
            "passengers",
            ""
        ).strip()

        seat_type = request.form.get(
            "seat_type",
            ""
        ).strip()

        if not all([
            source,
            destination,
            travel_date,
            bus,
            passengers,
            seat_type
        ]):

            return render_template(
                "book_ticket.html",
                cities=sorted(
                    CITY_COORDINATES.keys()
                ),
                error="Please fill in all fields."
            )

        if source.lower() == destination.lower():

            return render_template(
                "book_ticket.html",
                cities=sorted(
                    CITY_COORDINATES.keys()
                ),
                error="Source and destination cannot be the same."
            )

        try:

            travel_date_value = datetime.strptime(
                travel_date,
                "%Y-%m-%d"
            ).date()

            if travel_date_value < date.today():

                return render_template(
                    "book_ticket.html",
                    cities=sorted(
                        CITY_COORDINATES.keys()
                    ),
                    error="Travel date cannot be in the past."
                )

        except ValueError:

            return render_template(
                "book_ticket.html",
                cities=sorted(
                    CITY_COORDINATES.keys()
                ),
                error="Please select a valid travel date."
            )

        try:

            passengers_value = int(
                passengers
            )

            if passengers_value <= 0:

                raise ValueError

        except ValueError:

            return render_template(
                "book_ticket.html",
                cities=sorted(
                    CITY_COORDINATES.keys()
                ),
                error="Number of passengers must be greater than zero."
            )

        booking_id = (

            "BUS"

            +
            datetime.now().strftime(
                "%Y%m%d%H%M%S"
            )

            +
            str(
                random.randint(
                    100,
                    999
                )
            )

        )

        new_booking = TicketBooking(

            booking_id=booking_id,

            user_id=session["user_id"],

            source=source,

            destination=destination,

            travel_date=travel_date,

            bus=bus,

            passengers=passengers_value,

            seat_type=seat_type,

            booking_status="Confirmed",

            booking_date=datetime.now().strftime(
                "%d-%m-%Y %I:%M %p"
            )

        )

        db.session.add(
            new_booking
        )

        db.session.commit()

        return redirect(
            url_for(
                "booking_confirmation",
                booking_id=new_booking.booking_id
            )
        )

    return render_template(
        "book_ticket.html",
        cities=sorted(
            CITY_COORDINATES.keys()
        )
    )


# =========================================================
# BOOKING CONFIRMATION
# =========================================================

@app.route(
    "/booking-confirmation/<booking_id>"
)
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

    if booking.booking_status == "Cancelled":

        return redirect(
            url_for("dashboard")
        )

    booking.booking_status = "Cancelled"

    db.session.commit()

    return redirect(
        url_for("dashboard")
    )


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route(
    "/admin-login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        admin = Admin.query.filter_by(
            email=email
        ).first()

        if admin and admin.password == password:

            session["admin_id"] = admin.id

            session["admin_name"] = admin.name

            return redirect(
                url_for(
                    "admin_dashboard"
                )
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

@app.route(
    "/admin-dashboard"
)
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

    payments = Payment.query.order_by(
        Payment.id.desc()
    ).all()

    return render_template(
        "admin_dashboard.html",
        applications=applications,
        bookings=bookings,
        payments=payments
    )


# =========================================================
# ADMIN APPROVE APPLICATION
# =========================================================

@app.route(
    "/admin/approve/<int:application_id>"
)
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

        db.session.add(
            status
        )

    db.session.commit()

    # Send approval email.
    try:

        user = User.query.get(
            application.user_id
        )

        if user:

            email_subject = (
                "Cloud Bus Pass - Application Approved"
            )

            email_body = f"""
Hello {user.name},

Your Cloud Bus Pass application has been approved.

Application ID: {application.id}

Route:
{application.source} → {application.destination}

Pass Type:
{application.pass_type}

Start Date:
{application.start_date}

You can login to your account and download your approved bus pass.

Regards,
Cloud Bus Pass System
"""

            send_email(

                application_user_email=user.email,

                subject=email_subject,

                body=email_body

            )

    except Exception as error:

        print(
            "Approval email error:",
            error
        )

    return redirect(
        url_for(
            "admin_dashboard"
        )
    )


# =========================================================
# ADMIN REJECT APPLICATION
# =========================================================

@app.route(
    "/admin/reject/<int:application_id>"
)
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

        db.session.add(
            status
        )

    db.session.commit()

    # Send rejection email.
    try:

        user = User.query.get(
            application.user_id
        )

        if user:

            email_subject = (
                "Cloud Bus Pass - Application Rejected"
            )

            email_body = f"""
Hello {user.name},

Unfortunately, your Cloud Bus Pass application has been rejected.

Application ID: {application.id}

Route:
{application.source} → {application.destination}

Pass Type:
{application.pass_type}

Please login to your account for more information.

Regards,
Cloud Bus Pass System
"""

            send_email(

                application_user_email=user.email,

                subject=email_subject,

                body=email_body

            )

    except Exception as error:

        print(
            "Rejection email error:",
            error
        )

    return redirect(
        url_for(
            "admin_dashboard"
        )
    )


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route(
    "/admin-logout"
)
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

@app.route(
    "/logout"
)
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )