from flask import Flask, request, redirect, url_for, session, render_template_string, send_from_directory, flash
import sqlite3
import os
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "tn_handicrafts.db")
UPLOAD_DIR = os.path.join(APP_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("TN_HANDICRAFTS_SECRET", "change-this-secret-in-production")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

ROLES = {
    "buyer": "Buyer",
    "farmer": "Farmer",
    "shg": "SHG / NGO",
    "bank": "Bank",
    "admin": "Admin",
}

BANK_DETAILS = {
    "bank_name": "State Bank of India",
    "branch": "Thanjavur Main Branch",
    "manager": "R. Prakash",
    "mobile": "9987654321",
    "address": "Medical College Road, Thanjavur",
    "email": "sbi.demo@bank.local",
}

PRODUCTS = [
    {
        "code": "GI-TN-008",
        "name": "Swamimalai Bronze Nataraja Idol",
        "category": "Swamimalai Bronze",
        "district": "Thanjavur",
        "price": 4800,
        "image": "https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?auto=format&fit=crop&w=900&q=80",
        "description": "Traditional lost-wax bronze craft associated with Swamimalai artisans.",
    },
    {
        "code": "GI-TN-001",
        "name": "Thanjavur 22K Gold Leaf Painting (Lord Ganesha)",
        "category": "Thanjavur Paintings",
        "district": "Thanjavur",
        "price": 6500,
        "image": "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?auto=format&fit=crop&w=900&q=80",
        "description": "Handcrafted Thanjavur painting with traditional relief and gold-leaf detailing.",
    },
    {
        "code": "GI-TN-003",
        "name": "Kanchipuram Pure Silk Korvai Handloom Saree",
        "category": "Kanchipuram Silk",
        "district": "Kanchipuram",
        "price": 7200,
        "image": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=900&q=80",
        "description": "Traditional mulberry silk handloom with Korvai weaving.",
    },
    {
        "code": "GI-TN-004",
        "name": "Athangudi Handcrafted Floor Tiles",
        "category": "Athangudi Tiles",
        "district": "Sivaganga",
        "price": 850,
        "image": "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=900&q=80",
        "description": "Handmade patterned tiles produced using traditional Athangudi techniques.",
    },
    {
        "code": "GI-TN-005",
        "name": "Chettinad Palm Basket",
        "category": "Chettinad Basketry",
        "district": "Sivaganga",
        "price": 1200,
        "image": "https://images.unsplash.com/photo-1523779917675-b6ed3a42a561?auto=format&fit=crop&w=900&q=80",
        "description": "Traditional woven basket made by artisan communities.",
    },
    {
        "code": "GI-TN-006",
        "name": "Pattamadai Fine Grass Mat",
        "category": "Pattamadai Grass Mats",
        "district": "Tirunelveli",
        "price": 1800,
        "image": "https://images.unsplash.com/photo-1604014237800-1c9102c219da?auto=format&fit=crop&w=900&q=80",
        "description": "Fine handwoven grass mat inspired by Pattamadai craft traditions.",
    },
]

T = {
    "en": {
        "government": "Government of Tamil Nadu",
        "infra": "State Digital Infrastructure for Artisans & SHGs",
        "title": "Tamil Nadu Handicrafts",
        "login": "Sign in",
        "signup": "Create account",
        "logout": "Logout",
        "username": "Username",
        "password": "Password",
        "role": "Stakeholder type",
        "buyer": "Buyer",
        "farmer": "Farmer",
        "shg": "SHG / NGO",
        "bank": "Bank",
        "admin": "Admin",
        "home": "Home",
        "marketplace": "Marketplace",
        "cart": "Cart",
        "track": "Track Order",
        "payment": "Payment",
        "orders": "Orders",
        "documents": "Documents",
        "notification": "Notifications",
        "language": "தமிழ்",
        "welcome": "Welcome back",
        "signin_text": "Sign in to access your stakeholder workspace.",
        "signup_text": "Create your account. Your stakeholder type controls which workspace you can access.",
        "no_account": "New here?",
        "have_account": "Already have an account?",
        "create": "Create account",
        "invalid": "Invalid username or password.",
        "account_created": "Account created. Please sign in.",
        "exists": "Username already exists.",
        "market_intro": "Discover GI-tagged Tamil Nadu heritage products.",
        "add_cart": "Add to cart",
        "quantity": "Quantity",
        "update": "Update",
        "remove": "Remove",
        "moq": "MOQ 1,000 • no maximum quantity",
        "cart_total": "Cart total",
        "items": "line item(s)",
        "proceed": "Proceed to payment",
        "empty_cart": "Your cart is empty.",
        "pay_now": "Confirm demo payment",
        "payment_demo": "Demo payment — no real money is charged.",
        "payment_success": "Payment confirmed. Your order has entered the government workflow.",
        "buyer_orders": "Your orders",
        "received": "Order received",
        "received_done": "Order completed. Thank you.",
        "pending": "Pending",
        "accepted": "Accepted",
        "rejected": "Rejected",
        "approved": "Approved",
        "disbursed": "Disbursed",
        "production": "Production",
        "production_done": "Production done",
        "travel": "Travel Assistance",
        "travel_provided": "Travel assistance provided",
        "delivery_days": "Expected delivery days",
        "submit": "Submit",
        "process_bank": "Process to bank",
        "upload": "Upload document",
        "reupload": "Re-upload document",
        "bank_desc": "Bank decision note",
        "save": "Save",
        "approve": "Approve loan",
        "reject": "Reject loan",
        "loan": "Loan",
        "loan_status": "Loan status",
        "accepted_projects": "Accepted projects",
        "new_projects": "New projects",
        "no_projects": "No projects at this stage.",
        "documents_locked": "Document upload is locked after processing to bank.",
        "reupload_allowed": "The bank has requested a re-upload. You can upload the document again.",
        "reupload_not_allowed": "The bank has rejected the loan. Re-upload is not available until the bank requests it.",
        "bank_note": "Bank note",
        "required_docs": "Documents",
        "no_documents": "No documents uploaded.",
        "admin": "Admin",
        "all_orders": "All orders",
        "stage": "Stage",
        "filter": "Filter",
        "all": "All",
        "shg_pending": "SHG approval pending",
        "bank_pending": "Bank loan pending",
        "reupload_pending": "Document re-upload requested",
        "production_pending": "Production pending",
        "travel_pending": "Travel assistance pending",
        "delivery_pending": "Delivery pending",
        "closed": "Closed",
        "farmer_dashboard": "Farmer production workspace",
        "shg_dashboard": "SHG / NGO project workspace",
        "bank_dashboard": "Bank lending workspace",
        "admin_dashboard": "Admin workflow dashboard",
        "buyer_dashboard": "Buyer marketplace",
        "select_language": "Language",
        "signout": "Logout",
    },
    "ta": {
        "government": "தமிழ்நாடு அரசு",
        "infra": "கைவினைஞர்கள் மற்றும் சுய உதவிக் குழுக்களுக்கான டிஜிட்டல் உள்கட்டமைப்பு",
        "title": "தமிழ்நாடு கைவினைப் பொருட்கள்",
        "login": "உள்நுழை",
        "signup": "கணக்கை உருவாக்கு",
        "logout": "வெளியேறு",
        "username": "பயனர் பெயர்",
        "password": "கடவுச்சொல்",
        "role": "பங்குதாரர் வகை",
        "buyer": "வாங்குபவர்",
        "farmer": "விவசாயி",
        "shg": "சுய உதவிக் குழு / NGO",
        "bank": "வங்கி",
        "admin": "நிர்வாகம்",
        "home": "முகப்பு",
        "marketplace": "சந்தை",
        "cart": "வண்டி",
        "track": "ஆர்டரை கண்காணி",
        "payment": "கட்டணம்",
        "orders": "ஆர்டர்கள்",
        "documents": "ஆவணங்கள்",
        "notification": "அறிவிப்புகள்",
        "language": "EN",
        "welcome": "மீண்டும் வரவேற்கிறோம்",
        "signin_text": "உங்கள் பங்குதாரர் பணியிடத்தை அணுக உள்நுழையுங்கள்.",
        "signup_text": "கணக்கை உருவாக்குங்கள். நீங்கள் தேர்வு செய்யும் பங்குதாரர் வகைக்கு ஏற்ப பணியிடம் காட்டப்படும்.",
        "no_account": "புதியவரா?",
        "have_account": "ஏற்கனவே கணக்கு உள்ளதா?",
        "create": "கணக்கை உருவாக்கு",
        "invalid": "பயனர் பெயர் அல்லது கடவுச்சொல் தவறாக உள்ளது.",
        "account_created": "கணக்கு உருவாக்கப்பட்டது. உள்நுழையுங்கள்.",
        "exists": "இந்த பயனர் பெயர் ஏற்கனவே உள்ளது.",
        "market_intro": "GI குறியீடு பெற்ற தமிழ்நாடு பாரம்பரியப் பொருட்களை கண்டறியுங்கள்.",
        "add_cart": "வண்டியில் சேர்",
        "quantity": "அளவு",
        "update": "புதுப்பி",
        "remove": "நீக்கு",
        "moq": "குறைந்தபட்சம் 1,000 • அதிகபட்ச வரம்பில்லை",
        "cart_total": "மொத்தம்",
        "items": "வரி உருப்படி(கள்)",
        "proceed": "கட்டணத்திற்கு செல்லவும்",
        "empty_cart": "உங்கள் வண்டி காலியாக உள்ளது.",
        "pay_now": "டெமோ கட்டணத்தை உறுதிசெய்",
        "payment_demo": "டெமோ கட்டணம் — உண்மையான பணம் வசூலிக்கப்படாது.",
        "payment_success": "கட்டணம் உறுதி செய்யப்பட்டது. ஆர்டர் அரசின் செயல்முறைக்கு சென்றுள்ளது.",
        "buyer_orders": "உங்கள் ஆர்டர்கள்",
        "received": "ஆர்டர் கிடைத்தது",
        "received_done": "ஆர்டர் முடிக்கப்பட்டது. நன்றி.",
        "pending": "நிலுவையில்",
        "accepted": "ஏற்றுக்கொள்ளப்பட்டது",
        "rejected": "நிராகரிக்கப்பட்டது",
        "approved": "ஒப்புதல்",
        "disbursed": "வழங்கப்பட்டது",
        "production": "உற்பத்தி",
        "production_done": "உற்பத்தி முடிந்தது",
        "travel": "போக்குவரத்து உதவி",
        "travel_provided": "போக்குவரத்து உதவி வழங்கப்பட்டது",
        "delivery_days": "எதிர்பார்க்கப்படும் விநியோக நாட்கள்",
        "submit": "சமர்ப்பி",
        "process_bank": "வங்கிக்கு அனுப்பு",
        "upload": "ஆவணத்தை பதிவேற்று",
        "reupload": "ஆவணத்தை மீண்டும் பதிவேற்று",
        "bank_desc": "வங்கி முடிவு குறிப்பு",
        "save": "சேமி",
        "approve": "கடனுக்கு ஒப்புதல்",
        "reject": "கடனை நிராகரி",
        "loan": "கடன்",
        "loan_status": "கடன் நிலை",
        "accepted_projects": "ஏற்றுக்கொண்ட திட்டங்கள்",
        "new_projects": "புதிய திட்டங்கள்",
        "no_projects": "இந்த நிலையில் திட்டங்கள் இல்லை.",
        "documents_locked": "வங்கிக்கு அனுப்பிய பிறகு ஆவணப் பதிவேற்றம் பூட்டப்படும்.",
        "reupload_allowed": "வங்கி மீண்டும் பதிவேற்றம் கோரியுள்ளது. ஆவணத்தை மீண்டும் பதிவேற்றலாம்.",
        "reupload_not_allowed": "வங்கி கடனை நிராகரித்துள்ளது. வங்கி மீண்டும் பதிவேற்றம் கோரும் வரை மீண்டும் பதிவேற்ற முடியாது.",
        "bank_note": "வங்கி குறிப்பு",
        "required_docs": "ஆவணங்கள்",
        "no_documents": "ஆவணங்கள் பதிவேற்றப்படவில்லை.",
        "admin": "நிர்வாகம்",
        "all_orders": "அனைத்து ஆர்டர்கள்",
        "stage": "நிலை",
        "filter": "வடிகட்டி",
        "all": "அனைத்தும்",
        "shg_pending": "SHG ஒப்புதல் நிலுவை",
        "bank_pending": "வங்கி கடன் நிலுவை",
        "reupload_pending": "ஆவண மீண்டும் பதிவேற்றம் கோரப்பட்டது",
        "production_pending": "உற்பத்தி நிலுவை",
        "travel_pending": "போக்குவரத்து உதவி நிலுவை",
        "delivery_pending": "விநியோகம் நிலுவை",
        "closed": "முடிந்தது",
        "farmer_dashboard": "விவசாயி உற்பத்தி பணியிடம்",
        "shg_dashboard": "SHG / NGO திட்ட பணியிடம்",
        "bank_dashboard": "வங்கி கடன் பணியிடம்",
        "admin_dashboard": "நிர்வாக செயல்முறை பணியிடம்",
        "buyer_dashboard": "வாங்குபவர் சந்தை",
        "select_language": "மொழி",
        "signout": "வெளியேறு",
    }
}

BASE = r"""
<!doctype html>
<html lang="{{ lang }}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ title }}</title>
<style>
:root{
 --maroon:#74130f; --maroon2:#941f19; --gold:#c49336; --cream:#f7f3ec;
 --ink:#171717; --muted:#6d625c; --line:#e6ddd2; --white:#fff;
 --green:#177245; --red:#b42318; --amber:#9b6a08; --shadow:0 12px 35px rgba(53,35,20,.08);
}
*{box-sizing:border-box}
body{margin:0;background:var(--cream);color:var(--ink);font-family:Inter,Segoe UI,Arial,sans-serif}
a{color:inherit}
.topbar{height:42px;background:linear-gradient(90deg,#5d0d0a,#851912);color:#fff;display:flex;justify-content:space-between;align-items:center;padding:0 5vw;font-size:13px}
.nav{background:#fff;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;padding:17px 5vw;position:sticky;top:0;z-index:10}
.brand{font-weight:900;color:var(--maroon);font-size:24px;letter-spacing:-.6px}
.brand small{display:block;color:var(--muted);font-size:11px;font-weight:600;letter-spacing:0}
.navlinks{display:flex;gap:8px;align-items:center;flex-wrap:wrap;justify-content:flex-end}
.navlinks a,.navlinks span{padding:9px 12px;border-radius:10px;text-decoration:none;font-weight:700;font-size:14px}
.navlinks a:hover{background:#f4eee6}
.role{background:#f0e8de;border-radius:999px!important}
.lang{border:1px solid var(--line);background:#fff}
.logout{background:var(--maroon)!important;color:#fff!important;min-width:96px;text-align:center;white-space:nowrap;border:1px solid var(--maroon);display:inline-flex!important;align-items:center;justify-content:center}
.container{width:min(1180px,92vw);margin:28px auto 70px}
.card{background:#fff;border:1px solid var(--line);border-radius:18px;box-shadow:var(--shadow);padding:24px}
.hero{padding:30px}
h1{font-size:34px;letter-spacing:-1px;margin:7px 0 12px}
h2{font-size:23px;margin:0 0 14px}
h3{margin:0 0 9px}
.muted{color:var(--muted)}
.pill{display:inline-flex;align-items:center;border-radius:999px;padding:6px 10px;background:#f0e9df;font-weight:800;font-size:12px}
.badge{display:inline-flex;border-radius:999px;padding:6px 10px;font-size:12px;font-weight:900}
.badge.green{background:#e5f5ec;color:#176b42}.badge.red{background:#fde9e7;color:#a3231b}.badge.amber{background:#fff2d8;color:#8a6005}.badge.gray{background:#eeeae5;color:#5f554e}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;border:0;border-radius:11px;padding:11px 16px;font-weight:850;cursor:pointer;text-decoration:none;background:#ece6df;color:var(--ink)}
.btn.primary{background:var(--maroon);color:#fff;box-shadow:0 5px 12px rgba(116,19,15,.18)}
.btn.gold{background:var(--gold);color:#fff}.btn.danger{background:#fde4e1;color:#9d251d}.btn.success{background:#e3f4eb;color:#176b42}.btn.receive{background:var(--maroon);color:#fff;box-shadow:0 5px 14px rgba(116,19,15,.20);padding:12px 20px;font-weight:900}.btn.receive:hover{filter:brightness(.94);transform:translateY(-1px)}
.btn:disabled{opacity:.45;cursor:not-allowed}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.grid2{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}
.product img{width:100%;height:205px;object-fit:cover;border-radius:14px}.product .price{font-size:21px;font-weight:900;color:var(--maroon)}
.product .meta{font-size:12px;color:var(--muted);font-weight:800;text-transform:uppercase;letter-spacing:.5px}
.form{display:grid;gap:13px;max-width:520px}.input,.select,.textarea{width:100%;padding:13px 14px;border:1px solid #d9cec2;border-radius:10px;background:#fff;font:inherit}.textarea{min-height:110px;resize:vertical}
label{font-size:13px;font-weight:800}.notice{border-left:4px solid var(--gold);background:#fff7e6;padding:13px;border-radius:9px}.successbox{border-left:4px solid var(--green);background:#edf8f1;padding:13px;border-radius:9px}.errorbox{border-left:4px solid var(--red);background:#fff0ee;padding:13px;border-radius:9px}
.actions{display:flex;gap:10px;flex-wrap:wrap}.row{display:flex;justify-content:space-between;gap:15px;align-items:center;flex-wrap:wrap}
table{width:100%;border-collapse:separate;border-spacing:0;overflow:hidden;border:1px solid var(--line);border-radius:14px;background:#fff}th,td{text-align:left;padding:13px;border-bottom:1px solid var(--line);vertical-align:top}th{background:#f4eee7;font-size:12px;text-transform:uppercase;letter-spacing:.4px}tr:last-child td{border-bottom:0}
.stagebar{display:flex;gap:7px;flex-wrap:wrap;margin:18px 0}.stagebar a{padding:9px 12px;border:1px solid var(--line);border-radius:10px;text-decoration:none;font-weight:800;background:#fff}.stagebar a.active{background:var(--maroon);color:#fff;border-color:var(--maroon)}
.timeline{display:grid;gap:10px;margin-top:14px}.step{display:flex;gap:12px;align-items:flex-start}.dot{width:13px;height:13px;border-radius:50%;background:#d6cec6;margin-top:5px;flex:0 0 13px}.dot.done{background:var(--green)}.dot.current{background:var(--gold)}
.file-box{border:1px dashed #cdbfb1;border-radius:12px;padding:14px;background:#fbfaf8}.file-box input{margin-top:9px}
.auth{min-height:calc(100vh - 42px);display:grid;place-items:center;padding:35px 20px;background:radial-gradient(circle at 20% 20%,#fff 0,#f7f3ec 40%,#efe7dc 100%)}
.auth-card{width:min(450px,94vw);background:#fff;border:1px solid var(--line);border-radius:22px;padding:34px;box-shadow:0 25px 70px rgba(50,25,15,.12)}
.toast{position:fixed;right:22px;bottom:22px;background:#171717;color:#fff;padding:13px 17px;border-radius:12px;box-shadow:var(--shadow);z-index:99}
.statgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.stat{background:#fff;border:1px solid var(--line);border-radius:15px;padding:17px}.stat b{display:block;font-size:28px;margin-top:4px}
@media(max-width:850px){.grid,.grid2,.statgrid{grid-template-columns:1fr}.nav{align-items:flex-start;gap:12px}.navlinks{justify-content:flex-start}.topbar{font-size:11px}.brand{font-size:20px}}
</style>
</head>
<body>
<div class="topbar"><span>{{ t.government }}</span><span>{{ t.infra }}</span></div>
<nav class="nav">
  <a class="brand" href="{{ url_for('buyer') }}">{{ t.title }}<small>GI • Digital Public Infrastructure</small></a>
  <div class="navlinks">
    <a href="{{ url_for('buyer') }}">{{ t.marketplace }}</a>
    {% if session.get('user_id') %}
      {% if role == 'buyer' %}
        <a href="{{ url_for('cart') }}">{{ t.cart }} ({{ cart_count }})</a>
        <a href="{{ url_for('buyer_orders') }}">{{ t.track }}</a>
      {% else %}
        <span class="role">{{ role_label }}</span>
        <a href="{{ url_for('dashboard') }}">{{ t.home }}</a>
      {% endif %}
      <a class="lang" href="{{ url_for('toggle_language') }}">{{ t.language }}</a>
      <a class="logout" href="{{ url_for('logout') }}">↪&nbsp; {{ t.logout }}</a>
    {% else %}
      <a class="lang" href="{{ url_for('toggle_language') }}">{{ t.language }}</a>
      <a class="btn primary" style="padding:8px 13px" href="{{ url_for('login') }}">{{ t.login }}</a>
      <a href="{{ url_for('signup') }}">{{ t.signup }}</a>
    {% endif %}
  </div>
</nav>
{% block content %}{% endblock %}
{% if get_flashed_messages() %}
<div class="toast">{% for m in get_flashed_messages() %}{{ m }}{% if not loop.last %}<br>{% endif %}{% endfor %}</div>
{% endif %}
</body>
</html>
"""

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('buyer','farmer','shg','bank','admin')),
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        district TEXT NOT NULL,
        price REAL NOT NULL,
        image TEXT NOT NULL,
        description TEXT NOT NULL,
        moq INTEGER NOT NULL DEFAULT 1000
    );
    CREATE TABLE IF NOT EXISTS cart_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL CHECK(quantity >= 1000),
        UNIQUE(user_id, product_id),
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        buyer_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        total REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'paid',
        shg_id INTEGER,
        farmer_id INTEGER,
        bank_id INTEGER,
        created_at TEXT NOT NULL,
        received_at TEXT,
        FOREIGN KEY(buyer_id) REFERENCES users(id),
        FOREIGN KEY(product_id) REFERENCES products(id),
        FOREIGN KEY(shg_id) REFERENCES users(id),
        FOREIGN KEY(farmer_id) REFERENCES users(id),
        FOREIGN KEY(bank_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS loans(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER UNIQUE NOT NULL,
        bank_id INTEGER,
        status TEXT NOT NULL DEFAULT 'pending',
        decision_note TEXT DEFAULT '',
        reupload_requested INTEGER NOT NULL DEFAULT 0,
        processed_at TEXT,
        FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
        FOREIGN KEY(bank_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS documents(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        uploaded_by INTEGER NOT NULL,
        original_name TEXT NOT NULL,
        stored_name TEXT NOT NULL,
        uploaded_at TEXT NOT NULL,
        version INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
        FOREIGN KEY(uploaded_by) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS travel(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER UNIQUE NOT NULL,
        provided INTEGER NOT NULL DEFAULT 0,
        delivery_days INTEGER,
        truck_arrival_date TEXT,
        expected_delivery_date TEXT,
        provided_at TEXT,
        FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE
    );
    """)
    # Schema migration for delivery/travel dates (safe for existing databases).
    existing_cols = {r[1] for r in conn.execute("PRAGMA table_info(travel)").fetchall()}
    if "truck_arrival_date" not in existing_cols:
        conn.execute("ALTER TABLE travel ADD COLUMN truck_arrival_date TEXT")
    if "expected_delivery_date" not in existing_cols:
        conn.execute("ALTER TABLE travel ADD COLUMN expected_delivery_date TEXT")

    for p in PRODUCTS:
        conn.execute("""
        INSERT OR IGNORE INTO products(code,name,category,district,price,image,description,moq)
        VALUES(?,?,?,?,?,?,?,1000)
        """, (p["code"],p["name"],p["category"],p["district"],p["price"],p["image"],p["description"]))
    seeds = [
        ("buyer","buyer","buyer"), ("farmer","farmer","farmer"),
        ("shg","shg","shg"), ("bank","bank","bank"), ("admin","admin","admin")
    ]
    for username,password,role in seeds:
        conn.execute("INSERT OR IGNORE INTO users(username,password_hash,role,created_at) VALUES(?,?,?,?)",
                     (username,generate_password_hash(password),role,datetime.now().isoformat(timespec="seconds")))
    conn.commit()
    conn.close()

def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    conn = db()
    u = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    conn.close()
    return u

def get_lang():
    return session.get("lang","en")

def render_page(body, **context):
    context["lang"] = get_lang()
    context["t"] = T[context["lang"]]
    context["title"] = T[context["lang"]]["title"]
    u = current_user()
    context["role"] = u["role"] if u else None
    context["role_label"] = ROLES.get(u["role"], "") if u else ""
    context["cart_count"] = 0
    if u and u["role"] == "buyer":
        conn = db()
        context["cart_count"] = conn.execute("SELECT COUNT(DISTINCT product_id) FROM cart_items WHERE user_id=?", (u["id"],)).fetchone()[0]
        conn.close()
    return render_template_string(BASE.replace("{% block content %}{% endblock %}", "{% block content %}"+body+"{% endblock %}"), **context)

def require_role(*roles):
    u = current_user()
    if not u:
        return redirect(url_for("login"))
    if u["role"] not in roles:
        return redirect(url_for("dashboard"))
    return u

@app.route("/")
def index():
    return redirect(url_for("buyer"))

@app.route("/toggle-language")
def toggle_language():
    session["lang"] = "ta" if get_lang() == "en" else "en"
    return redirect(request.referrer or url_for("dashboard"))

@app.route("/login", methods=["GET","POST"])
def login():
    if current_user():
        return redirect(url_for("dashboard"))
    next_url = request.args.get("next") or request.form.get("next")
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        conn = db()
        u = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if u and check_password_hash(u["password_hash"], password):
            pending = session.get("pending_cart")
            session.clear()
            session["user_id"] = u["id"]
            session["lang"] = "en"
            if u["role"] == "buyer" and pending:
                pid, qty = pending
                if int(qty) >= 1000 and conn.execute("SELECT id FROM products WHERE id=?", (pid,)).fetchone():
                    conn.execute("INSERT INTO cart_items(user_id,product_id,quantity) VALUES(?,?,?) ON CONFLICT(user_id,product_id) DO UPDATE SET quantity=excluded.quantity", (u["id"],pid,int(qty)))
                    conn.commit()
                session.pop("pending_cart", None)
            conn.close()
            if u["role"] == "buyer" and next_url == url_for("buyer"):
                return redirect(url_for("cart"))
            return redirect(url_for("dashboard"))
        conn.close()
        flash(T[get_lang()]["invalid"])
    body = r"""
    <div class="auth">
      <div class="auth-card">
        <div class="pill">TN HANDICRAFTS • DPI</div>
        <h1>{{ t.welcome }}</h1>
        <p class="muted">{{ t.signin_text }}</p>
        <form method="post" class="form">
          <div><label>{{ t.username }}</label><input class="input" name="username" required autocomplete="username"></div>
          <div><label>{{ t.password }}</label><input class="input" type="password" name="password" required autocomplete="current-password"></div>
          <button class="btn primary" type="submit">{{ t.login }} →</button>
        </form>
        <p class="muted" style="margin-top:22px">{{ t.no_account }} <a href="{{ url_for('signup') }}" style="font-weight:800;color:var(--maroon)">{{ t.signup }}</a></p>
        <p style="margin-top:14px"><a class="btn lang" href="{{ url_for('toggle_language') }}">{{ t.language }}</a></p>
      </div>
    </div>
    """
    return render_page(body)

@app.route("/signup", methods=["GET","POST"])
def signup():
    if current_user():
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        role = request.form.get("role","")
        if role not in ROLES:
            flash("Select a valid stakeholder type.")
        elif len(password) < 4:
            flash("Password must be at least 4 characters.")
        else:
            conn = db()
            try:
                conn.execute("INSERT INTO users(username,password_hash,role,created_at) VALUES(?,?,?,?)",
                             (username,generate_password_hash(password),role,datetime.now().isoformat(timespec="seconds")))
                conn.commit()
                flash(T[get_lang()]["account_created"])
                conn.close()
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                conn.close()
                flash(T[get_lang()]["exists"])
    body = r"""
    <div class="auth">
      <div class="auth-card">
        <div class="pill">TN HANDICRAFTS • DPI</div>
        <h1>{{ t.signup }}</h1>
        <p class="muted">{{ t.signup_text }}</p>
        <form method="post" class="form">
          <div><label>{{ t.username }}</label><input class="input" name="username" required></div>
          <div><label>{{ t.password }}</label><input class="input" type="password" name="password" minlength="4" required></div>
          <div><label>{{ t.role }}</label>
            <select class="select" name="role" required>
              <option value="">Select</option>
              {% for r,n in roles.items() %}<option value="{{ r }}">{{ t[r] }}</option>{% endfor %}
            </select>
          </div>
          <button class="btn primary" type="submit">{{ t.create }} →</button>
        </form>
        <p class="muted" style="margin-top:22px">{{ t.have_account }} <a href="{{ url_for('login') }}" style="font-weight:800;color:var(--maroon)">{{ t.login }}</a></p>
      </div>
    </div>
    """
    return render_page(body, roles=ROLES)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    u = current_user()
    if not u:
        return redirect(url_for("login"))
    return redirect(url_for({
        "buyer":"buyer", "farmer":"farmer", "shg":"shg", "bank":"bank", "admin":"admin"
    }[u["role"]]))

@app.route("/buyer")
def buyer():
    conn = db()
    products = conn.execute("SELECT * FROM products ORDER BY id").fetchall()
    conn.close()
    body = r"""
    <div class="container">
      <section class="card hero">
        <span class="pill">{{ t.buyer_dashboard }}</span>
        <h1>{{ t.marketplace }}</h1>
        <p class="muted">{{ t.market_intro }}</p>
      </section>
      <div class="grid" style="margin-top:20px">
      {% for p in products %}
        <article class="card product">
          <img src="{{ p.image }}" alt="{{ p.name }}">
          <div class="meta" style="margin-top:12px">{{ p.district }} • {{ p.category }}</div>
          <h3>{{ p.name }}</h3>
          <p class="muted">{{ p.description }}</p>
          <div class="row"><div class="price">₹{{ "{:,.0f}".format(p.price) }}</div><span class="badge gray">MOQ 1,000+</span></div>
          <form method="post" action="{{ url_for('add_cart', product_id=p.id) }}" class="actions" style="margin-top:14px">
            <input class="input" style="width:120px" type="number" name="quantity" value="1000" min="1000" required>
            <button class="btn primary" type="submit">{{ t.add_cart }}</button>
          </form>
        </article>
      {% endfor %}
      </div>
    </div>
    """
    return render_page(body, products=products)

@app.post("/buyer/cart/add/<int:product_id>")
def add_cart(product_id):
    u = current_user()
    try: q = int(request.form.get("quantity","1000"))
    except ValueError: q = 0
    if q < 1000:
        flash("Minimum order quantity is 1,000.")
        return redirect(url_for("buyer"))
    if not u:
        session["pending_cart"] = [product_id, q]
        return redirect(url_for("login", next=url_for("buyer")))
    if u["role"] != "buyer":
        return redirect(url_for("dashboard"))
    conn = db()
    if not conn.execute("SELECT id FROM products WHERE id=?", (product_id,)).fetchone():
        conn.close(); return redirect(url_for("buyer"))
    conn.execute("""INSERT INTO cart_items(user_id,product_id,quantity) VALUES(?,?,?)
                    ON CONFLICT(user_id,product_id) DO UPDATE SET quantity=excluded.quantity""",
                 (u["id"],product_id,q))
    conn.commit(); conn.close()
    flash("Product added to cart.")
    return redirect(url_for("cart"))

@app.route("/buyer/cart")
def cart():
    u = require_role("buyer")
    if not hasattr(u, "__getitem__"): return u
    conn = db()
    items = conn.execute("""SELECT c.*,p.name,p.code,p.price,p.image,(c.quantity*p.price) total
                            FROM cart_items c JOIN products p ON p.id=c.product_id
                            WHERE c.user_id=? ORDER BY c.id""",(u["id"],)).fetchall()
    total = sum(x["total"] for x in items)
    conn.close()
    body = r"""
    <div class="container">
      <section class="card hero"><span class="pill">{{ t.cart }}</span><h1>{{ t.cart_total }}</h1>
      <p class="muted">{{ t.moq }}</p></section>
      {% if items %}
      <div class="card" style="margin-top:20px">
        <div class="row" style="font-weight:900;margin-bottom:10px"><span>{{ items|length }} {{ t.items }}</span><span>₹{{ "{:,.0f}".format(total) }}</span></div>
        {% for i in items %}
        <div class="row" style="padding:17px 0;border-top:1px solid var(--line)">
          <div style="display:flex;gap:14px;align-items:center;min-width:260px"><img src="{{ i.image }}" style="width:75px;height:60px;object-fit:cover;border-radius:9px"><div><b>{{ i.name }}</b><div class="muted">{{ i.code }}</div></div></div>
          <form method="post" action="{{ url_for('update_cart', item_id=i.id) }}" class="actions">
            <label>{{ t.quantity }} <input class="input" style="width:120px;display:inline-block" type="number" name="quantity" min="1000" value="{{ i.quantity }}"></label>
            <button class="btn" type="submit">{{ t.update }}</button>
          </form>
          <b>₹{{ "{:,.0f}".format(i.total) }}</b>
          <a class="btn danger" href="{{ url_for('remove_cart', item_id=i.id) }}">{{ t.remove }}</a>
        </div>
        {% endfor %}
      </div>
      <div class="card" style="margin-top:18px">
        <div class="row"><div><div class="muted">{{ t.cart_total }}</div><h1 style="margin:2px 0">₹{{ "{:,.0f}".format(total) }}</h1></div>
        <a class="btn primary" href="{{ url_for('payment') }}">{{ t.proceed }} →</a></div>
        <p class="muted">{{ t.payment_demo }}</p>
      </div>
      {% else %}<div class="card" style="margin-top:20px">{{ t.empty_cart }}</div>{% endif %}
    </div>
    """
    return render_page(body, items=items, total=total)

@app.post("/buyer/cart/update/<int:item_id>")
def update_cart(item_id):
    u = require_role("buyer")
    if not hasattr(u, "__getitem__"): return u
    try: q = int(request.form.get("quantity","0"))
    except ValueError: q = 0
    if q < 1000:
        flash("Minimum order quantity is 1,000.")
    else:
        conn = db(); conn.execute("UPDATE cart_items SET quantity=? WHERE id=? AND user_id=?",(q,item_id,u["id"])); conn.commit(); conn.close()
        flash("Cart updated.")
    return redirect(url_for("cart"))

@app.route("/buyer/cart/remove/<int:item_id>")
def remove_cart(item_id):
    u = require_role("buyer")
    if not hasattr(u, "__getitem__"): return u
    conn=db(); conn.execute("DELETE FROM cart_items WHERE id=? AND user_id=?",(item_id,u["id"])); conn.commit(); conn.close()
    return redirect(url_for("cart"))

@app.route("/buyer/payment", methods=["GET","POST"])
def payment():
    u = require_role("buyer")
    if not hasattr(u, "__getitem__"): return u
    conn=db()
    items=conn.execute("""SELECT c.*,p.name,p.price FROM cart_items c JOIN products p ON p.id=c.product_id WHERE c.user_id=?""",(u["id"],)).fetchall()
    total=sum(i["quantity"]*i["price"] for i in items)
    if not items:
        conn.close(); return redirect(url_for("cart"))
    if request.method=="POST":
        now=datetime.now().isoformat(timespec="seconds")
        for i in items:
            cur=conn.execute("""INSERT INTO orders(buyer_id,product_id,quantity,unit_price,total,status,created_at)
                                VALUES(?,?,?,?,?,'paid',?)""",
                             (u["id"],i["product_id"],i["quantity"],i["price"],i["quantity"]*i["price"],now))
            oid=cur.lastrowid
            conn.execute("INSERT INTO loans(order_id,status) VALUES(?, 'pending')",(oid,))
        conn.execute("DELETE FROM cart_items WHERE user_id=?",(u["id"],))
        conn.commit(); conn.close()
        flash(T[get_lang()]["payment_success"])
        return redirect(url_for("buyer_orders"))
    conn.close()
    body=r"""
    <div class="container"><section class="card hero"><span class="pill">{{ t.payment }}</span><h1>Confirm order</h1><p class="muted">{{ t.payment_demo }}</p></section>
    <div class="card" style="margin-top:20px"><table><tr><th>Product</th><th>Qty</th><th>Total</th></tr>{% for i in items %}<tr><td>{{ i.name }}</td><td>{{ i.quantity }}</td><td>₹{{ "{:,.0f}".format(i.quantity*i.price) }}</td></tr>{% endfor %}</table>
    <div class="row" style="margin-top:20px"><h2>₹{{ "{:,.0f}".format(total) }}</h2><form method="post"><button class="btn primary">{{ t.pay_now }} →</button></form></div></div></div>
    """
    return render_page(body,items=items,total=total)

def order_rows(conn, where="", args=()):
    return conn.execute(f"""SELECT o.*,p.name,p.code,b.username buyer_name,s.username shg_name,f.username farmer_name,
                            bk.username bank_username,l.status loan_status,l.decision_note,l.reupload_requested,
                            t.provided travel_provided,t.delivery_days,t.truck_arrival_date,t.expected_delivery_date
                            FROM orders o JOIN products p ON p.id=o.product_id
                            JOIN users b ON b.id=o.buyer_id
                            LEFT JOIN users s ON s.id=o.shg_id LEFT JOIN users f ON f.id=o.farmer_id
                            LEFT JOIN users bk ON bk.id=o.bank_id
                            LEFT JOIN loans l ON l.order_id=o.id
                            LEFT JOIN travel t ON t.order_id=o.id {where} ORDER BY o.id DESC""",args).fetchall()

@app.route("/buyer/orders")
def buyer_orders():
    u=require_role("buyer")
    if not hasattr(u,"__getitem__"): return u
    conn=db(); orders=order_rows(conn,"WHERE o.buyer_id=?",(u["id"],)); conn.close()
    body=r"""
    <div class="container"><section class="card hero"><span class="pill">{{ t.track }}</span><h1>{{ t.buyer_orders }}</h1><p class="muted">Follow every stage from SHG allocation to delivery.</p></section>
    <div class="timeline">
    {% for o in orders %}
      <div class="card"><div class="row"><div><h2>Order #{{ o.id }} · {{ o.name }}</h2><p class="muted">{{ o.quantity }} units · ₹{{ "{:,.0f}".format(o.total) }}</p></div>
      {% if o.status=='closed' %}<span class="badge green">{{ t.closed }}</span>{% else %}<span class="badge gray">{{ o.status|upper }}</span>{% endif %}</div>
      <div class="timeline">
        <div class="step"><span class="dot done"></span><div><b>Order & payment</b><div class="muted">Confirmed</div></div></div>
        <div class="step"><span class="dot {{ 'done' if o.shg_id else 'current' }}"></span><div><b>SHG assignment</b><div class="muted">{{ o.shg_name or t.pending }}</div></div></div>
        <div class="step"><span class="dot {{ 'done' if o.loan_status in ['approved','disbursed'] else 'current' }}"></span><div><b>Bank loan</b><div class="muted">{{ o.loan_status|upper }}</div>{% if o.loan_status=='rejected' and o.decision_note %}<div class="errorbox" style="margin-top:7px">{{ o.decision_note }}</div>{% endif %}</div></div>
        <div class="step"><span class="dot {{ 'done' if production_done(o) else 'current' }}"></span><div><b>Production</b><div class="muted">{{ 'Done' if production_done(o) else t.pending }}</div></div></div>
        <div class="step"><span class="dot {{ 'done' if o.travel_provided else 'current' }}"></span><div><b>Delivery</b><div class="muted">{% if o.travel_provided %}<b>Truck arrival:</b> {{ o.truck_arrival_date or '—' }}<br><b>Expected delivery:</b> {{ o.expected_delivery_date or '—' }}{% if o.delivery_days %}<br><span class="muted">{{ o.delivery_days }} days</span>{% endif %}{% else %}{{ t.pending }}{% endif %}</div></div></div>
      </div>
      {% if o.travel_provided and o.status!='closed' %}<form method="post" action="{{ url_for('order_received', order_id=o.id) }}" style="margin-top:20px"><button class="btn receive" type="submit">✓ {{ t.received }}</button></form>{% endif %}
      {% if o.status=='closed' %}<div class="successbox" style="margin-top:15px">{{ t.received_done }}</div>{% endif %}
      </div>
    {% else %}<div class="card">{{ t.no_projects }}</div>{% endfor %}
    </div></div>
    """
    # Add computed field without altering schema.
    body = body.replace("{{ o.production_done }}","{{ o.loan_status in ['approved','disbursed'] and o.travel_provided }}")
    return render_page(body,orders=orders)

@app.post("/buyer/orders/<int:order_id>/received")
def order_received(order_id):
    u=require_role("buyer")
    if not hasattr(u,"__getitem__"): return u
    conn=db()
    o=conn.execute("""SELECT o.id FROM orders o JOIN travel t ON t.order_id=o.id
                      WHERE o.id=? AND o.buyer_id=? AND t.provided=1""",(order_id,u["id"])).fetchone()
    if o:
        conn.execute("UPDATE orders SET status='closed',received_at=? WHERE id=?",(datetime.now().isoformat(timespec="seconds"),order_id))
        conn.commit()
        flash(T[get_lang()]["received_done"])
    conn.close()
    return redirect(url_for("buyer_orders"))

@app.route("/shg")
def shg():
    u=require_role("shg")
    if not hasattr(u,"__getitem__"): return u
    conn=db()
    new_orders=order_rows(conn,"WHERE o.shg_id IS NULL AND o.status='paid'")
    accepted=order_rows(conn,"WHERE o.shg_id=?",(u["id"],))
    conn.close()
    body=r"""
    <div class="container">
      <section class="card hero"><span class="pill">{{ t.shg }}</span><h1>{{ t.shg_dashboard }}</h1><p class="muted">Accept buyer orders, manage the loan pack, then coordinate travel assistance.</p></section>
      <h2 style="margin-top:25px">{{ t.new_projects }}</h2>
      {% for o in new_orders %}
      <div class="card" style="margin-bottom:15px"><div class="row"><div><h2>{{ o.name }} · Order #{{ o.id }}</h2><p class="muted">{{ o.quantity }} units · Buyer: {{ o.buyer_name }}</p></div><span class="badge amber">{{ t.pending }}</span></div>
      <form method="post" action="{{ url_for('shg_claim',order_id=o.id) }}" class="actions"><button class="btn primary">Accept project</button><button class="btn danger" name="decline" value="1">Decline</button></form></div>
      {% else %}<div class="card">{{ t.no_projects }}</div>{% endfor %}
      <div class="row" style="margin-top:30px"><h2>{{ t.accepted_projects }}</h2><a class="btn" href="#travel">{{ t.travel }}</a></div>
      {% for o in accepted %}
      <div class="card" style="margin-bottom:15px">
        <div class="row"><div><h2>{{ o.name }} · Order #{{ o.id }}</h2><p class="muted">{{ o.quantity }} units · Farmer: {{ o.farmer_name or 'Pending allocation' }}</p></div>
        <span class="badge {{ 'green' if o.loan_status in ['approved','disbursed'] else 'amber' }}">{{ o.loan_status|upper }}</span></div>
        {% if not o.farmer_id %}<div class="notice">Farmer allocation will appear here when assigned.</div>{% endif %}
        <div style="margin-top:15px"><b>{{ t.loan_status }}</b><p class="muted">Bank: {{ o.bank_username or 'State Bank of India' }}</p>
        {% if o.loan_status=='rejected' %}
          {% if o.reupload_requested == 1 %}
            <div class="notice">{{ t.reupload_allowed }}</div>
            <form method="post" action="{{ url_for('shg_upload',order_id=o.id) }}" enctype="multipart/form-data" class="form" style="margin-top:10px">
              <div class="file-box"><b>{{ t.upload }}</b><input type="file" name="document" required></div>
              <button class="btn primary">{{ t.upload }}</button>
            </form>
            <form method="post" action="{{ url_for('shg_process_bank',order_id=o.id) }}" style="margin-top:10px"><button class="btn gold" onclick="return confirm('Please make sure all documents are uploaded. After processing to bank, you will not be able to make changes until the bank requests a re-upload. Continue?')">{{ t.process_bank }}</button></form>
          {% else %}
            <div class="errorbox"><b>{{ t.rejected }}</b><br>{{ o.decision_note or 'The bank rejected this loan application.' }}<br><span class="muted">{{ t.reupload_not_allowed }}</span></div>
          {% endif %}
        {% elif o.loan_status in ['pending','submitted'] %}
          <div class="file-box">
            <b>{{ t.documents }}</b>
            <ol>
            {% for d in o.docs %}<li>{{ d.original_name }} <span class="muted">· {{ d.uploaded_at }}</span></li>{% else %}<li>{{ t.no_documents }}</li>{% endfor %}
            </ol>
            {% if o.loan_status=='pending' %}
            <form method="post" action="{{ url_for('shg_upload',order_id=o.id) }}" enctype="multipart/form-data">
              <label class="btn" style="margin-top:8px;display:inline-flex">＋ {{ t.upload }}<input type="file" name="document" required style="display:none" onchange="this.form.submit()"></label>
            </form>
            <form method="post" action="{{ url_for('shg_process_bank',order_id=o.id) }}" style="margin-top:10px"><button class="btn gold" onclick="return confirm('Please make sure all documents are uploaded. After processing to bank, you will not be able to make changes until the bank requests a re-upload. Continue?')">{{ t.process_bank }}</button></form>
            {% else %}<div class="notice" style="margin-top:10px">{{ t.documents_locked }}</div>{% endif %}
          </div>
        {% else %}
          <div class="successbox">{{ o.decision_note or 'Loan approved/disbursed.' }}</div>
        {% endif %}
        </div>
      </div>
      {% endfor %}
      <h2 id="travel" style="margin-top:35px">{{ t.travel }}</h2>
      {% for o in accepted %}
        {% if o.status=='production_done' and not o.travel_provided %}
        <div class="card" style="margin-bottom:15px"><div class="row"><div><h3>{{ o.name }} · Order #{{ o.id }}</h3><p class="muted">Farmer: {{ o.farmer_name }} · Quantity: {{ o.quantity }}</p></div><span class="badge amber">Ready for travel</span></div>
        <p>Connect with the travel agency using the farmer and quantity details above.</p>
        <form method="post" action="{{ url_for('travel_provide',order_id=o.id) }}" class="form">
          <div class="grid-2">
            <div><label>Truck arrival date at farmer location</label><input class="input" type="date" name="truck_arrival_date" required></div>
            <div><label>Expected delivery date to buyer</label><input class="input" type="date" name="expected_delivery_date" required></div>
          </div>
          <div><label>{{ t.delivery_days }}</label><input class="input" type="number" name="days" min="1" required placeholder="e.g. 5"></div>
          <button class="btn primary">{{ t.travel_provided }}</button>
        </form></div>
        {% elif o.travel_provided %}
        <div class="card" style="margin-bottom:15px"><h3>{{ o.name }} · Order #{{ o.id }}</h3><p class="muted">Farmer: {{ o.farmer_name }} · Quantity: {{ o.quantity }}</p><div class="successbox">{{ t.travel_provided }} · {{ o.delivery_days }} days<br><b>Truck arrival at farmer:</b> {{ o.truck_arrival_date or '—' }}<br><b>Expected buyer delivery:</b> {{ o.expected_delivery_date or '—' }}</div></div>
        {% endif %}
      {% else %}<div class="card">{{ t.no_projects }}</div>{% endfor %}
    </div>
    """
    # Enrich orders with documents.
    conn=db()
    for o in accepted:
        docs=conn.execute("SELECT * FROM documents WHERE order_id=? ORDER BY id",(o["id"],)).fetchall()
        o = dict(o)
    # sqlite3.Row cannot be mutated, so build dicts.
    enriched=[]
    for row in accepted:
        d=dict(row); d["docs"]=conn.execute("SELECT * FROM documents WHERE order_id=? ORDER BY id",(row["id"],)).fetchall()
        enriched.append(d)
    conn.close()
    return render_page(body,new_orders=new_orders,accepted=enriched)

@app.post("/shg/claim/<int:order_id>")
def shg_claim(order_id):
    u=require_role("shg")
    if not hasattr(u,"__getitem__"): return u
    conn=db()
    if request.form.get("decline"):
        conn.execute("UPDATE orders SET status='shg_declined' WHERE id=? AND shg_id IS NULL",(order_id,))
    else:
        conn.execute("UPDATE orders SET shg_id=?,status='shg_accepted' WHERE id=? AND shg_id IS NULL",(u["id"],order_id))
        # Assign the first farmer account for this working prototype.
        farmer=conn.execute("SELECT id FROM users WHERE role='farmer' ORDER BY id LIMIT 1").fetchone()
        if farmer: conn.execute("UPDATE orders SET farmer_id=? WHERE id=?",(farmer["id"],order_id))
    conn.commit(); conn.close()
    return redirect(url_for("shg"))

@app.post("/shg/<int:order_id>/upload")
def shg_upload(order_id):
    u=require_role("shg")
    if not hasattr(u,"__getitem__"): return u
    f=request.files.get("document")
    conn=db()
    o=conn.execute("""SELECT o.*,l.status loan_status,l.reupload_requested FROM orders o JOIN loans l ON l.order_id=o.id
                      WHERE o.id=? AND o.shg_id=?""",(order_id,u["id"])).fetchone()
    if not o or not f or not f.filename:
        conn.close(); return redirect(url_for("shg"))
    allowed={"pdf","png","jpg","jpeg","doc","docx"}
    ext=f.filename.rsplit(".",1)[-1].lower() if "." in f.filename else ""
    if ext not in allowed:
        conn.close(); flash("Allowed files: PDF, PNG, JPG, JPEG, DOC, DOCX."); return redirect(url_for("shg"))
    # Upload is allowed only before first processing, or after an explicit bank re-upload request.
    if o["loan_status"] not in ("pending","rejected") or (o["loan_status"]=="rejected" and not o["reupload_requested"]):
        conn.close(); flash(T[get_lang()]["reupload_not_allowed"]); return redirect(url_for("shg"))
    stored=f"{uuid.uuid4().hex}_{secure_filename(f.filename)}"
    f.save(os.path.join(UPLOAD_DIR,stored))
    version=conn.execute("SELECT COALESCE(MAX(version),0)+1 FROM documents WHERE order_id=?",(order_id,)).fetchone()[0]
    conn.execute("INSERT INTO documents(order_id,uploaded_by,original_name,stored_name,uploaded_at,version) VALUES(?,?,?,?,?,?)",
                 (order_id,u["id"],f.filename,stored,datetime.now().isoformat(timespec="seconds"),version))
    # If this is a re-upload, reset request and make the pack pending again.
    conn.execute("UPDATE loans SET status='pending',reupload_requested=0,decision_note='' WHERE order_id=?",(order_id,))
    conn.commit(); conn.close()
    flash("Document stored successfully.")
    return redirect(url_for("shg"))

@app.post("/shg/<int:order_id>/process-bank")
def shg_process_bank(order_id):
    u=require_role("shg")
    if not hasattr(u,"__getitem__"): return u
    conn=db()
    o=conn.execute("""SELECT o.id,l.status FROM orders o JOIN loans l ON l.order_id=o.id WHERE o.id=? AND o.shg_id=?""",(order_id,u["id"])).fetchone()
    docs=conn.execute("SELECT COUNT(*) n FROM documents WHERE order_id=?",(order_id,)).fetchone()["n"]
    if o and docs:
        bank=conn.execute("SELECT id FROM users WHERE role='bank' ORDER BY id LIMIT 1").fetchone()
        conn.execute("UPDATE orders SET bank_id=? WHERE id=?",(bank["id"] if bank else None,order_id))
        conn.execute("UPDATE loans SET status='submitted',reupload_requested=0,processed_at=?,bank_id=? WHERE order_id=?",
                     (datetime.now().isoformat(timespec="seconds"),bank["id"] if bank else None,order_id))
        conn.commit(); flash("Loan pack processed to bank.")
    else: flash("Upload at least one document before processing to bank.")
    conn.close(); return redirect(url_for("shg"))

@app.route("/bank")
def bank():
    u=require_role("bank")
    if not hasattr(u,"__getitem__"): return u
    conn=db(); orders=order_rows(conn,"WHERE o.bank_id=? AND l.status IN ('submitted','pending','approved','disbursed','rejected')",(u["id"],))
    conn.close()
    body=r"""
    <div class="container"><section class="card hero"><span class="pill">{{ t.bank }}</span><h1>{{ t.bank_dashboard }}</h1><p class="muted">Review only loan packs routed to this bank.</p></section>
    <div class="card" style="margin-top:20px"><h2>{{ bank.bank_name }}</h2><p><b>Branch:</b> {{ bank.branch }} · <b>Manager:</b> {{ bank.manager }} · <b>Mobile:</b> {{ bank.mobile }}</p></div>
    <div class="grid2" style="margin-top:18px">
    {% for o in orders %}
      <div class="card"><div class="row"><h2>Order #{{ o.id }}</h2><span class="badge {{ 'green' if o.loan_status in ['approved','disbursed'] else 'red' if o.loan_status=='rejected' else 'amber' }}">{{ o.loan_status|upper }}</span></div>
      <h3>{{ o.name }}</h3><p class="muted">{{ o.quantity }} units · Buyer: {{ o.buyer_name }} · SHG: {{ o.shg_name }}</p>
      <p><b>{{ t.documents }}</b></p>
      <ol>{% for d in o.docs %}<li><a href="{{ url_for('download_document',stored_name=d.stored_name) }}">{{ d.original_name }}</a></li>{% else %}<li>{{ t.no_documents }}</li>{% endfor %}</ol>
      {% if o.loan_status=='submitted' %}
      <form method="post" action="{{ url_for('bank_decide',order_id=o.id) }}" class="form">
        <label>{{ t.bank_desc }}</label><textarea class="textarea" name="note" placeholder="Enter approval / rejection reason" required></textarea>
        <div class="actions"><button class="btn success" name="decision" value="approve">{{ t.approve }}</button><button class="btn danger" name="decision" value="reject">{{ t.reject }}</button></div>
      </form>
      {% elif o.loan_status=='rejected' %}
        <div class="errorbox"><b>{{ t.rejected }}</b><br>{{ o.decision_note or 'No description provided.' }}</div>
        {% if not o.reupload_requested %}
        <form method="post" action="{{ url_for('bank_reupload',order_id=o.id) }}" style="margin-top:12px"><button class="btn gold">{{ t.reupload }}</button></form>
        {% else %}<div class="notice" style="margin-top:12px">Re-upload requested. Waiting for SHG / NGO.</div>{% endif %}
      {% else %}<div class="successbox">{{ o.decision_note or o.loan_status|upper }}</div>{% endif %}
      </div>
    {% else %}<div class="card">{{ t.no_projects }}</div>{% endfor %}
    </div></div>
    """
    # Enrich with documents.
    conn=db(); enriched=[]
    for row in orders:
        d=dict(row); d["docs"]=conn.execute("SELECT * FROM documents WHERE order_id=? ORDER BY id",(row["id"],)).fetchall(); enriched.append(d)
    conn.close()
    return render_page(body,orders=enriched,bank=BANK_DETAILS)

@app.post("/bank/<int:order_id>/decide")
def bank_decide(order_id):
    u=require_role("bank")
    if not hasattr(u,"__getitem__"): return u
    decision=request.form.get("decision")
    note=request.form.get("note","").strip()
    if decision not in ("approve","reject"): return redirect(url_for("bank"))
    conn=db()
    if decision=="approve":
        conn.execute("UPDATE loans SET status='disbursed',decision_note=?,reupload_requested=0,processed_at=? WHERE order_id=? AND bank_id=?",
                     (note,datetime.now().isoformat(timespec="seconds"),order_id,u["id"]))
    else:
        conn.execute("UPDATE loans SET status='rejected',decision_note=?,reupload_requested=0,processed_at=? WHERE order_id=? AND bank_id=?",
                     (note,datetime.now().isoformat(timespec="seconds"),order_id,u["id"]))
    conn.commit(); conn.close()
    flash("Bank decision saved.")
    return redirect(url_for("bank"))

@app.post("/bank/<int:order_id>/reupload")
def bank_reupload(order_id):
    u=require_role("bank")
    if not hasattr(u,"__getitem__"): return u
    conn=db()
    conn.execute("UPDATE loans SET reupload_requested=1 WHERE order_id=? AND bank_id=? AND status='rejected'",(order_id,u["id"]))
    conn.commit(); conn.close()
    flash("Re-upload requested from SHG / NGO.")
    return redirect(url_for("bank"))

@app.route("/documents/<stored_name>")
def download_document(stored_name):
    u=current_user()
    if not u: return redirect(url_for("login"))
    # Access is role-controlled: only bank, SHG and admin can see documents.
    if u["role"] not in ("bank","shg","admin"): return redirect(url_for("dashboard"))
    return send_from_directory(UPLOAD_DIR,stored_name,as_attachment=True)

@app.route("/farmer")
def farmer():
    u=require_role("farmer")
    if not hasattr(u,"__getitem__"): return u
    conn=db(); orders=order_rows(conn,"WHERE o.farmer_id=?",(u["id"],)); conn.close()
    body=r"""
    <div class="container"><section class="card hero"><span class="pill">{{ t.farmer }}</span><h1>{{ t.farmer_dashboard }}</h1><p class="muted">Production becomes available only after the bank loan is disbursed.</p></section>
    {% for o in orders %}
    <div class="card" style="margin-top:18px"><div class="row"><div><h2>Order #{{ o.id }} · {{ o.name }}</h2><p class="muted">{{ o.quantity }} units · SHG: {{ o.shg_name }}</p></div><span class="badge {{ 'green' if o.loan_status=='disbursed' else 'amber' }}">{{ o.loan_status|upper }}</span></div>
      <div class="notice" style="margin:14px 0">Bank status: {{ o.loan_status|upper }}</div>
      {% if o.loan_status in ['approved','disbursed'] and not production_done(o) %}
      <form method="post" action="{{ url_for('production_done',order_id=o.id) }}"><button class="btn primary">{{ t.production_done }} ✓</button></form>
      {% elif production_done(o) %}<div class="successbox">{{ t.production_done }} — SHG / NGO has been notified for travel assistance.</div>
       {% if o.travel_provided %}<div class="notice" style="margin-top:12px"><b>Truck arrival at your location:</b> {{ o.truck_arrival_date or '—' }}<br><b>Expected delivery to buyer:</b> {{ o.expected_delivery_date or '—' }}</div>{% else %}<div class="notice" style="margin-top:12px">SHG will update the truck arrival date once travel assistance is arranged.</div>{% endif %}
      {% else %}<div class="muted">Production is locked until the loan is approved/disbursed.</div>{% endif %}
    </div>
    {% else %}<div class="card" style="margin-top:18px">{{ t.no_projects }}</div>{% endfor %}
    </div>
    """
    return render_page(body,orders=orders)

@app.post("/farmer/<int:order_id>/production-done")
def production_done(order_id):
    u=require_role("farmer")
    if not hasattr(u,"__getitem__"): return u
    conn=db()
    o=conn.execute("""SELECT o.id AS order_id, o.status AS order_status, l.status AS loan_status
                      FROM orders o JOIN loans l ON l.order_id=o.id
                      WHERE o.id=? AND o.farmer_id=?""",(order_id,u["id"])).fetchone()
    if o and o["loan_status"] in ("approved","disbursed") and o["order_status"] not in ("production_done","in_transit","closed"):
        # Mark production complete without changing the loan state.
        conn.execute("UPDATE orders SET status='production_done' WHERE id=?",(order_id,))
        conn.commit(); flash("Production marked as done.")
    conn.close(); return redirect(url_for("farmer"))

@app.post("/shg/<int:order_id>/travel")
def travel_provide(order_id):
    u=require_role("shg")
    if not hasattr(u,"__getitem__"): return u
    try: days=int(request.form.get("days","0"))
    except ValueError: days=0
    truck_arrival_date=request.form.get("truck_arrival_date","").strip()
    expected_delivery_date=request.form.get("expected_delivery_date","").strip()
    if days < 1 or not truck_arrival_date or not expected_delivery_date:
        flash("Please enter truck arrival date, expected delivery date and delivery days.")
        return redirect(url_for("shg"))
    conn=db()
    o=conn.execute("""SELECT o.id FROM orders o WHERE o.id=? AND o.shg_id=? AND o.status='production_done'""",(order_id,u["id"])).fetchone()
    if o:
        conn.execute("""INSERT INTO travel(order_id,provided,delivery_days,truck_arrival_date,expected_delivery_date,provided_at)
                        VALUES(?,1,?,?,?,?)
                        ON CONFLICT(order_id) DO UPDATE SET provided=1,delivery_days=excluded.delivery_days,
                        truck_arrival_date=excluded.truck_arrival_date,expected_delivery_date=excluded.expected_delivery_date,
                        provided_at=excluded.provided_at""",
                     (order_id,days,truck_arrival_date,expected_delivery_date,datetime.now().isoformat(timespec="seconds")))
        conn.execute("UPDATE orders SET status='in_transit' WHERE id=?",(order_id,))
        conn.commit(); flash("Travel assistance recorded and delivery dates sent to farmer and buyer.")
    conn.close(); return redirect(url_for("shg"))

@app.route("/admin")
def admin():
    u=require_role("admin")
    if not hasattr(u,"__getitem__"): return u
    flt=request.args.get("filter","all")
    conditions={"all":"","shg_pending":"WHERE o.shg_id IS NULL AND o.status='paid'","bank_pending":"WHERE l.status='submitted'",
                "reupload_pending":"WHERE l.reupload_requested=1","production_pending":"WHERE l.status='disbursed' AND o.status IN ('shg_accepted','paid')",
                "travel_pending":"WHERE o.status='production_done'","delivery_pending":"WHERE o.status='in_transit'","closed":"WHERE o.status='closed'"}
    conn=db(); orders=order_rows(conn,conditions.get(flt,"")); 
    counts={
        "shg_pending":conn.execute("SELECT COUNT(*) FROM orders o WHERE o.shg_id IS NULL AND o.status='paid'").fetchone()[0],
        "bank_pending":conn.execute("SELECT COUNT(*) FROM loans l WHERE l.status='submitted'").fetchone()[0],
        "reupload_pending":conn.execute("SELECT COUNT(*) FROM loans l WHERE l.reupload_requested=1").fetchone()[0],
        "production_pending":conn.execute("SELECT COUNT(*) FROM loans l JOIN orders o ON o.id=l.order_id WHERE l.status='disbursed' AND o.status IN ('shg_accepted','paid')").fetchone()[0],
        "travel_pending":conn.execute("SELECT COUNT(*) FROM orders o WHERE o.status='production_done'").fetchone()[0],
        "delivery_pending":conn.execute("SELECT COUNT(*) FROM orders o WHERE o.status='in_transit'").fetchone()[0],
        "closed":conn.execute("SELECT COUNT(*) FROM orders o WHERE o.status='closed'").fetchone()[0],
    }
    conn.close()
    body=r"""
    <div class="container"><section class="card hero"><span class="pill">{{ t.admin }}</span><h1>{{ t.admin_dashboard }}</h1><p class="muted">Single operational view. Each stakeholder still sees only their own workspace.</p></section>
    <div class="stagebar">
      <a class="{{ 'active' if flt=='all' else '' }}" href="{{ url_for('admin',filter='all') }}">{{ t.all }}</a>
      <a class="{{ 'active' if flt=='shg_pending' else '' }}" href="{{ url_for('admin',filter='shg_pending') }}">{{ t.shg_pending }} · {{ counts.shg_pending }}</a>
      <a class="{{ 'active' if flt=='bank_pending' else '' }}" href="{{ url_for('admin',filter='bank_pending') }}">{{ t.bank_pending }} · {{ counts.bank_pending }}</a>
      <a class="{{ 'active' if flt=='reupload_pending' else '' }}" href="{{ url_for('admin',filter='reupload_pending') }}">{{ t.reupload_pending }} · {{ counts.reupload_pending }}</a>
      <a class="{{ 'active' if flt=='production_pending' else '' }}" href="{{ url_for('admin',filter='production_pending') }}">{{ t.production_pending }} · {{ counts.production_pending }}</a>
      <a class="{{ 'active' if flt=='travel_pending' else '' }}" href="{{ url_for('admin',filter='travel_pending') }}">{{ t.travel_pending }} · {{ counts.travel_pending }}</a>
      <a class="{{ 'active' if flt=='delivery_pending' else '' }}" href="{{ url_for('admin',filter='delivery_pending') }}">{{ t.delivery_pending }} · {{ counts.delivery_pending }}</a>
      <a class="{{ 'active' if flt=='closed' else '' }}" href="{{ url_for('admin',filter='closed') }}">{{ t.closed }} · {{ counts.closed }}</a>
    </div>
    <div class="card"><table><tr><th>Order</th><th>Product / Qty</th><th>Buyer</th><th>SHG</th><th>Farmer</th><th>Loan</th><th>Workflow</th></tr>
    {% for o in orders %}<tr><td>#{{ o.id }}</td><td><b>{{ o.name }}</b><br>{{ o.quantity }}</td><td>{{ o.buyer_name }}</td><td>{{ o.shg_name or '—' }}</td><td>{{ o.farmer_name or '—' }}</td><td><span class="badge {{ 'green' if o.loan_status in ['approved','disbursed'] else 'red' if o.loan_status=='rejected' else 'amber' }}">{{ o.loan_status|upper }}</span>{% if o.decision_note %}<br><small>{{ o.decision_note }}</small>{% endif %}</td><td>{{ o.status|upper }}{% if o.travel_provided %}<br>{{ o.delivery_days }} days<br><small>Truck: {{ o.truck_arrival_date or '—' }}<br>Delivery: {{ o.expected_delivery_date or '—' }}</small>{% endif %}</td></tr>
    {% else %}<tr><td colspan="7">{{ t.no_projects }}</td></tr>{% endfor %}</table></div></div>
    """
    return render_page(body,orders=orders,counts=counts,flt=flt)

@app.context_processor
def helpers():
    # A Jinja-safe helper to determine production completion from order status.
    return {"production_done": lambda o: o["status"] in ("production_done","in_transit","closed")}

@app.errorhandler(413)
def too_large(_):
    flash("File too large. Maximum file size is 10 MB.")
    return redirect(request.referrer or url_for("dashboard"))

# Initialize a clean demo database on first startup.
# The packaged project intentionally contains NO runtime database/data.
init_db()

if __name__ == "__main__":
    print("Tamil Nadu Handicrafts DPI running at http://127.0.0.1:8010")
    app.run(host="127.0.0.1", port=8010, debug=False)
