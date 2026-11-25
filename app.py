import os, sqlite3
from datetime import date, timedelta
from flask import Flask, request, redirect, url_for, render_template_string, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "queueflow-dev-key")
DB = os.environ.get("DATABASE_PATH", "queueflow.db")

def connect():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    os.makedirs(os.path.dirname(DB), exist_ok=True) if os.path.dirname(DB) else None
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT, customer TEXT NOT NULL,
            phone TEXT NOT NULL, service TEXT NOT NULL, booking_date TEXT NOT NULL,
            booking_time TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(booking_date, booking_time)
        )""")

PAGE = """
<!doctype html><html lang="{{ 'az' if lang == 'az' else 'en' }}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>QueueFlow — {{ 'Onlayn görüş təyini' if lang=='az' else 'Simple appointment booking' }}</title>
<style>
:root{--ink:#17231f;--muted:#6d7973;--line:#e5eae6;--green:#176b50;--bg:#f5f8f5}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 Inter,system-ui,Arial}
header{height:76px;background:white;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;padding:0 max(6%,calc((100% - 1120px)/2))}
.logo{font-weight:800;font-size:22px;letter-spacing:-1px}.logo span{color:var(--green)}a{color:var(--green);text-decoration:none}
nav{display:flex;gap:20px;align-items:center}.wrap{max-width:1120px;margin:48px auto;padding:0 22px}
.hero{display:grid;grid-template-columns:1.1fr .9fr;gap:55px;align-items:center;margin-bottom:38px}
h1{font-size:clamp(36px,5vw,58px);line-height:1.04;letter-spacing:-2.5px;margin:10px 0 18px}
.lead{color:var(--muted);font-size:17px;max-width:490px}.eyebrow{color:var(--green);font-weight:700;text-transform:uppercase;letter-spacing:1.6px;font-size:12px}
.card{background:white;border:1px solid var(--line);border-radius:18px;padding:26px;box-shadow:0 14px 40px #173a2410}
h2{margin:0 0 18px;font-size:22px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
label{display:block;font-size:13px;font-weight:650;margin:0 0 6px}input,select{width:100%;padding:12px;border:1px solid #dce4de;border-radius:9px;background:white;font:inherit;color:var(--ink)}
.field{margin-bottom:14px}.full{grid-column:1/-1}button,.btn{border:0;border-radius:9px;background:var(--green);color:white;padding:12px 17px;font:inherit;font-weight:700;cursor:pointer}
button:hover,.btn:hover{background:#10543e}.muted{color:var(--muted)}.notice{padding:11px 14px;background:#eaf5ed;border-radius:9px;margin-bottom:16px;color:#17553a}
.stats{display:flex;gap:12px;margin:20px 0}.stat{background:#f4f8f5;border:1px solid var(--line);padding:13px 17px;border-radius:12px;flex:1}.stat b{display:block;font-size:23px}
table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;padding:13px 10px;border-bottom:1px solid var(--line)}th{color:var(--muted);font-weight:600}
.pill{font-size:12px;padding:5px 9px;border-radius:20px;background:#f0f2ef}.actions{display:flex;gap:6px}.actions button{padding:7px 9px;font-size:12px}.danger{background:#a33d37}.empty{text-align:center;padding:35px;color:var(--muted)}
footer{text-align:center;color:var(--muted);padding:35px;font-size:13px}
@media(max-width:760px){.hero{grid-template-columns:1fr;gap:25px}.wrap{margin:28px auto}.grid{grid-template-columns:1fr}.full{grid-column:auto}header{padding:0 20px}.stats{flex-direction:column}.table-wrap{overflow:auto}table{min-width:650px}}
</style></head><body>
<header><div class="logo">Queue<span>Flow</span></div><nav><a href="/?lang=en">EN</a><a href="/?lang=az">AZ</a><a href="/admin">{{ 'İdarəetmə' if lang=='az' else 'Dashboard' }}</a></nav></header>
<main class="wrap">
{% if admin %}
<div class="eyebrow">{{ 'Biznes paneli' if lang=='az' else 'BUSINESS DASHBOARD' }}</div><h1 style="font-size:42px">{{ 'Görüşlər' if lang=='az' else 'Appointments' }}</h1>
<div class="stats"><div class="stat"><span class="muted">{{ 'Cəmi' if lang=='az' else 'Total' }}</span><b>{{ bookings|length }}</b></div><div class="stat"><span class="muted">{{ 'Gözləyən' if lang=='az' else 'Pending' }}</span><b>{{ bookings|selectattr('status','equalto','Pending')|list|length }}</b></div><div class="stat"><span class="muted">{{ 'Təsdiqlənən' if lang=='az' else 'Confirmed' }}</span><b>{{ bookings|selectattr('status','equalto','Confirmed')|list|length }}</b></div></div>
<section class="card"><h2>{{ 'Bütün rezervasiyalar' if lang=='az' else 'All bookings' }}</h2>
{% if bookings %}<div class="table-wrap"><table><thead><tr><th>{{ 'Müştəri' if lang=='az' else 'Customer' }}</th><th>{{ 'Xidmət' if lang=='az' else 'Service' }}</th><th>{{ 'Tarix və saat' if lang=='az' else 'Date & time' }}</th><th>{{ 'Telefon' if lang=='az' else 'Phone' }}</th><th>{{ 'Status' if lang=='az' else 'Status' }}</th><th></th></tr></thead><tbody>
{% for b in bookings %}<tr><td><b>{{ b.customer }}</b></td><td>{{ b.service }}</td><td>{{ b.booking_date }} · {{ b.booking_time }}</td><td>{{ b.phone }}</td><td><span class="pill">{{ b.status }}</span></td><td><div class="actions"><form method="post" action="/status/{{b.id}}"><input type="hidden" name="status" value="Confirmed"><button>{{ 'Təsdiq' if lang=='az' else 'Confirm' }}</button></form><form method="post" action="/status/{{b.id}}"><input type="hidden" name="status" value="Cancelled"><button class="danger">{{ 'Ləğv' if lang=='az' else 'Cancel' }}</button></form></div></td></tr>{% endfor %}
</tbody></table></div>{% else %}<div class="empty">{{ 'Hələ rezervasiya yoxdur.' if lang=='az' else 'No bookings yet.' }}</div>{% endif %}</section>
{% else %}
<section class="hero"><div><div class="eyebrow">{{ 'Görüşlərinizi asanlıqla idarə edin' if lang=='az' else 'LESS ADMIN. MORE BUSINESS.' }}</div><h1>{{ 'Rezervasiyalar artıq daha sadədir.' if lang=='az' else 'Appointments, made simple.' }}</h1><p class="lead">{{ 'Müştəriləriniz onlayn vaxt seçsin. Siz isə bütün görüşləri bir paneldən idarə edin.' if lang=='az' else 'Let customers book a time online. Manage every appointment from one simple dashboard.' }}</p><p class="muted">✓ {{ 'Sürətli onlayn rezervasiya' if lang=='az' else 'Fast online booking' }}<br>✓ {{ 'Aydın görüş cədvəli' if lang=='az' else 'Clear appointment schedule' }}<br>✓ {{ 'Kiçik bizneslər üçün yaradılıb' if lang=='az' else 'Built for small businesses' }}</p></div>
<section class="card"><h2>{{ 'Görüş təyin edin' if lang=='az' else 'Book an appointment' }}</h2>
{% with messages=get_flashed_messages() %}{% for message in messages %}<div class="notice">{{ message }}</div>{% endfor %}{% endwith %}
<form method="post" action="/book"><input type="hidden" name="lang" value="{{lang}}"><div class="grid">
<div class="field full"><label>{{ 'Ad və soyad' if lang=='az' else 'Full name' }}</label><input name="customer" required maxlength="80" placeholder="{{ 'Adınız' if lang=='az' else 'Your name' }}"></div>
<div class="field full"><label>{{ 'Telefon' if lang=='az' else 'Phone number' }}</label><input name="phone" required maxlength="30" placeholder="+994 50 000 00 00"></div>
<div class="field full"><label>{{ 'Xidmət' if lang=='az' else 'Service' }}</label><select name="service"><option>Haircut / Saç kəsimi</option><option>Styling / Saç düzümü</option><option>Manicure / Manikür</option><option>Consultation / Məsləhət</option><option>Other / Digər</option></select></div>
<div class="field"><label>{{ 'Tarix' if lang=='az' else 'Date' }}</label><input type="date" name="booking_date" min="{{today}}" required></div>
<div class="field"><label>{{ 'Saat' if lang=='az' else 'Time' }}</label><select name="booking_time" required>{% for t in times %}<option>{{t}}</option>{% endfor %}</select></div>
<div class="field full"><button style="width:100%">{{ 'Rezervasiya et' if lang=='az' else 'Book now' }}</button></div></div></form><p class="muted" style="font-size:12px;margin-bottom:0">{{ 'Rezervasiyanız təsdiq gözləyəcək.' if lang=='az' else 'Your booking will be marked as pending confirmation.' }}</p></section></section>
{% endif %}</main><footer>QueueFlow · {{ 'Kiçik bizneslər üçün sadə rezervasiya' if lang=='az' else 'Simple booking for small businesses' }}</footer></body></html>
"""

@app.route("/")
def home():
    lang = request.args.get("lang", "en")
    return render_template_string(PAGE, lang=lang, admin=False, today=date.today().isoformat(),
                                  times=[f"{h:02d}:{m:02d}" for h in range(9,19) for m in (0,30)])

@app.post("/book")
def book():
    lang = request.form.get("lang", "en")
    customer, phone = request.form.get("customer","").strip(), request.form.get("phone","").strip()
    day, time, service = request.form.get("booking_date",""), request.form.get("booking_time",""), request.form.get("service","")
    if not customer or not phone or day < date.today().isoformat():
        flash("Məlumatları yoxlayın." if lang=="az" else "Please check your details and choose a valid date.")
        return redirect(url_for("home", lang=lang))
    try:
        with connect() as db:
            db.execute("INSERT INTO bookings(customer,phone,service,booking_date,booking_time) VALUES(?,?,?,?,?)",(customer,phone,service,day,time))
        flash("Rezervasiyanız qəbul edildi!" if lang=="az" else "Your appointment request has been received!")
    except sqlite3.IntegrityError:
        flash("Bu saat artıq tutulub. Başqa vaxt seçin." if lang=="az" else "That time is already booked. Please choose another.")
    return redirect(url_for("home", lang=lang))

@app.route("/admin")
def admin():
    with connect() as db: bookings = db.execute("SELECT * FROM bookings ORDER BY booking_date,booking_time").fetchall()
    lang = request.args.get("lang", "en")
    return render_template_string(PAGE, lang=lang, admin=True, bookings=bookings)

@app.post("/status/<int:booking_id>")
def status(booking_id):
    value = request.form.get("status")
    if value in ("Confirmed","Cancelled"):
        with connect() as db: db.execute("UPDATE bookings SET status=? WHERE id=?", (value,booking_id))
    return redirect(url_for("admin"))

init_db()
