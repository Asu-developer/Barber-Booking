from flask import Flask, render_template, request, redirect, url_for, session, make_response
import sqlite3
import uuid
import os
from werkzeug.utils import secure_filename
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)

app.secret_key = "change-this-secret-key"

DATABASE = "barber.db"

# Cihaz başına maksimum randevu
MAX_DEVICE_APPOINTMENTS = 3

# Limitin yenilenme süresi
DEVICE_LIMIT_HOURS = 24


# ==================================================
# BERBER BİLGİLERİ
# ==================================================

SHOP = {
    "name": "Elit Barber",
    "phone": "0555 555 55 55",
    "instagram": "@elit_barber",
    "address": "Kahramanmaraş, Türkiye",
    "description": "Profesyonel erkek kuaförü",
    "logo": "logo.png"
}

# ==================================================
# GALERİ RESİM YÜKLEME
# ==================================================

ALLOWED_EXTENSIONS = {"jpg", "jpeg"}

def allowed_file(filename):
    return (
        "." in filename
        and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route(
    "/admin/gallery/upload/<int:image_id>",
    methods=["POST"]
)
def upload_gallery_image(image_id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    # Sadece 1-4 arası kabul et
    if image_id not in [1, 2, 3, 4]:
        return redirect(url_for("admin"))

    if "image" not in request.files:
        return redirect(url_for("admin"))

    file = request.files["image"]

    if file.filename == "":
        return redirect(url_for("admin"))

    if file and allowed_file(file.filename):

        # Klasör yoksa oluştur
        upload_folder = os.path.join(
            app.static_folder,
            "images"
        )

        os.makedirs(upload_folder, exist_ok=True)

        # Dosya adı: 1.jpg, 2.jpg, 3.jpg, 4.jpg
        filename = f"{image_id}.jpg"
        filepath = os.path.join(upload_folder, filename)

        file.save(filepath)

    return redirect(url_for("admin"))

# ==================================================
# ADMIN
# ==================================================

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"


# ==================================================
# DATABASE
# ==================================================

def get_db():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


def column_exists(conn, table, column):

    columns = conn.execute(
        f"PRAGMA table_info({table})"
    ).fetchall()

    return any(
        row["name"] == column
        for row in columns
    )


def init_db():

    conn = get_db()

    # --------------------------------------------------
    # APPOINTMENTS
    # --------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS appointments (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            phone TEXT NOT NULL,

            service TEXT NOT NULL,

            date TEXT NOT NULL,

            time TEXT NOT NULL

        )
    """)

    # Eski database kullananlar için
    # yeni kolonları otomatik ekle.

    if not column_exists(
        conn,
        "appointments",
        "barber_id"
    ):

        conn.execute("""
            ALTER TABLE appointments
            ADD COLUMN barber_id INTEGER
        """)

    if not column_exists(
        conn,
        "appointments",
        "barber_name"
    ):

        conn.execute("""
            ALTER TABLE appointments
            ADD COLUMN barber_name TEXT
        """)

    if not column_exists(
        conn,
        "appointments",
        "device_id"
    ):

        conn.execute("""
            ALTER TABLE appointments
            ADD COLUMN device_id TEXT
        """)

    if not column_exists(
        conn,
        "appointments",
        "created_at"
    ):

        conn.execute("""
            ALTER TABLE appointments
            ADD COLUMN created_at TEXT
        """)

    # --------------------------------------------------
    # SERVICES
    # --------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS services (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            duration INTEGER NOT NULL,

            price REAL NOT NULL DEFAULT 0

        )
    """)

    # --------------------------------------------------
    # BARBERS
    # --------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS barbers (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL

        )
    """)

    # --------------------------------------------------
    # DEFAULT SERVICES
    # --------------------------------------------------

    service_count = conn.execute(
        "SELECT COUNT(*) FROM services"
    ).fetchone()[0]

    if service_count == 0:

        conn.execute("""
            INSERT INTO services
            (name, duration, price)
            VALUES (?, ?, ?)
        """, (
            "Saç Kesimi",
            30,
            0
        ))

        conn.execute("""
            INSERT INTO services
            (name, duration, price)
            VALUES (?, ?, ?)
        """, (
            "Sakal Kesimi",
            20,
            0
        ))

        conn.execute("""
            INSERT INTO services
            (name, duration, price)
            VALUES (?, ?, ?)
        """, (
            "Saç + Sakal",
            50,
            0
        ))

    # --------------------------------------------------
    # DEFAULT BARBER
    # --------------------------------------------------

    barber_count = conn.execute(
        "SELECT COUNT(*) FROM barbers"
    ).fetchone()[0]

    if barber_count == 0:

        conn.execute("""
            INSERT INTO barbers (name)
            VALUES (?)
        """, (
            "Usta 1",
        ))

    # --------------------------------------------------
    # ESKİ RANDEVULARA TARİH BİLGİSİ
    # --------------------------------------------------

    conn.execute("""
        UPDATE appointments

        SET created_at = ?

        WHERE created_at IS NULL
        OR created_at = ''
    """, (
        datetime.now().isoformat(),
    ))

    # Eski randevularda usta yoksa
    # ilk ustayı ata.

    first_barber = conn.execute("""
        SELECT id, name
        FROM barbers
        ORDER BY id
        LIMIT 1
    """).fetchone()

    if first_barber:

        conn.execute("""
            UPDATE appointments

            SET barber_id = ?,
                barber_name = ?

            WHERE barber_id IS NULL
        """, (
            first_barber["id"],
            first_barber["name"]
        ))

    conn.commit()

    conn.close()


# ==================================================
# HİZMETLER
# ==================================================

def get_services():

    conn = get_db()

    services = conn.execute("""
        SELECT *
        FROM services
        ORDER BY id
    """).fetchall()

    conn.close()

    return services


# ==================================================
# USTALAR
# ==================================================

def get_barbers():

    conn = get_db()

    barbers = conn.execute("""
        SELECT *
        FROM barbers
        ORDER BY id
    """).fetchall()

    conn.close()

    return barbers


# ==================================================
# SAATLER
# ==================================================

def generate_hours():

    hours = []

    start = datetime.strptime(
        "09:00",
        "%H:%M"
    )

    end = datetime.strptime(
        "19:00",
        "%H:%M"
    )

    current = start

    while current < end:

        hours.append(
            current.strftime("%H:%M")
        )

        current += timedelta(
            minutes=30
        )

    return hours


# ==================================================
# DATETIME
# ==================================================

def make_datetime(date, time):

    return datetime.strptime(
        date + " " + time,
        "%Y-%m-%d %H:%M"
    )


# ==================================================
# CİHAZ ID
# ==================================================

def get_device_id():

    device_id = request.cookies.get(
        "device_id"
    )

    if not device_id:

        device_id = str(
            uuid.uuid4()
        )

    return device_id


# ==================================================
# CİHAZ RANDEVU LİMİTİ
# ==================================================

def get_device_appointment_count(
    device_id
):

    limit_time = (
        datetime.now()
        - timedelta(
            hours=DEVICE_LIMIT_HOURS
        )
    )

    conn = get_db()

    count = conn.execute("""
        SELECT COUNT(*)

        FROM appointments

        WHERE device_id = ?

        AND created_at >= ?
    """, (
        device_id,
        limit_time.isoformat()
    )).fetchone()[0]

    conn.close()

    return count


# ==================================================
# SAAT ÇAKIŞMA KONTROLÜ
# ==================================================

def is_time_available(
    date,
    start_time,
    duration,
    barber_id,
    exclude_id=None
):

    requested_start = make_datetime(
        date,
        start_time
    )

    requested_end = (
        requested_start
        +
        timedelta(
            minutes=duration
        )
    )

    conn = get_db()

    query = """
        SELECT
            a.id,
            a.date,
            a.time,
            s.duration

        FROM appointments a

        LEFT JOIN services s
        ON a.service = s.name

        WHERE a.date = ?

        AND a.barber_id = ?
    """

    params = [
        date,
        barber_id
    ]

    if exclude_id is not None:

        query += """
            AND a.id != ?
        """

        params.append(
            exclude_id
        )

    appointments = conn.execute(
        query,
        params
    ).fetchall()

    conn.close()

    for appointment in appointments:

        existing_start = make_datetime(
            appointment["date"],
            appointment["time"]
        )

        existing_duration = (
            appointment["duration"]
            if appointment["duration"]
            else 30
        )

        existing_end = (
            existing_start
            +
            timedelta(
                minutes=existing_duration
            )
        )

        if (
            requested_start < existing_end
            and
            requested_end > existing_start
        ):

            return False

    return True


# ==================================================
# MÜSAİT SAATLER
# ==================================================

def get_available_hours(
    date,
    service_duration,
    barber_id
):

    result = []

    for hour in generate_hours():

        # Geçmiş saatleri kapat

        try:

            hour_datetime = make_datetime(
                date,
                hour
            )

            if hour_datetime < datetime.now():

                result.append({
                    "time": hour,
                    "available": False
                })

                continue

        except ValueError:

            pass

        available = is_time_available(
            date,
            hour,
            service_duration,
            barber_id
        )

        result.append({

            "time": hour,

            "available": available

        })

    return result


# ==================================================
# ANA SAYFA
# ==================================================

@app.route("/")
def index():

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    services = get_services()

    barbers = get_barbers()

    if services:

        default_duration = services[0]["duration"]

    else:

        default_duration = 30

    if barbers:

        default_barber = barbers[0]["id"]

        hours = get_available_hours(
            today,
            default_duration,
            default_barber
        )

    else:

        hours = []

    return render_template(
        "index.html",

        shop=SHOP,

        services=services,

        barbers=barbers,

        available_hours=hours,

        selected_date=today
    )


# ==================================================
# MÜSAİT SAATLER API
# ==================================================

@app.route(
    "/available-hours"
)
def available_hours():

    date = request.args.get(
        "date"
    )

    service_id = request.args.get(
        "service"
    )

    barber_id = request.args.get(
        "barber"
    )

    if not date:

        return {
            "hours": []
        }

    if not barber_id:

        return {
            "hours": []
        }

    duration = 30

    conn = get_db()

    service = None

    if service_id:

        service = conn.execute("""
            SELECT duration
            FROM services
            WHERE id = ?
        """, (
            service_id,
        )).fetchone()

    conn.close()

    if service:

        duration = service["duration"]

    try:

        barber_id = int(
            barber_id
        )

    except ValueError:

        return {
            "hours": []
        }

    hours = get_available_hours(
        date,
        duration,
        barber_id
    )

    return {
        "hours": hours
    }


# ==================================================
# RANDEVU OLUŞTUR
# ==================================================

@app.route(
    "/book",
    methods=["POST"]
)
def book():

    name = request.form.get(
        "name",
        ""
    ).strip()

    phone = request.form.get(
        "phone",
        ""
    ).strip()

    service_id = request.form.get(
        "service"
    )

    barber_id = request.form.get(
        "barber"
    )

    date = request.form.get(
        "date"
    )

    time = request.form.get(
        "time"
    )

    # --------------------------------------------------
    # TEMEL KONTROLLER
    # --------------------------------------------------

    if not name or not phone:

        return render_template(
            "error.html",
            error="Ad ve telefon bilgisi zorunludur."
        )

    if (
        not service_id
        or
        not barber_id
        or
        not date
        or
        not time
    ):

        return render_template(
            "error.html",
            error="Eksik bilgi gönderildi."
        )

    try:

        service_id = int(
            service_id
        )

        barber_id = int(
            barber_id
        )

    except ValueError:

        return render_template(
            "error.html",
            error="Geçersiz hizmet veya usta seçimi."
        )

    conn = get_db()

    # --------------------------------------------------
    # HİZMET
    # --------------------------------------------------

    service = conn.execute("""
        SELECT *
        FROM services
        WHERE id = ?
    """, (
        service_id,
    )).fetchone()

    # --------------------------------------------------
    # USTA
    # --------------------------------------------------

    barber = conn.execute("""
        SELECT *
        FROM barbers
        WHERE id = ?
    """, (
        barber_id,
    )).fetchone()

    conn.close()

    if not service:

        return render_template(
            "error.html",
            error="Seçilen hizmet bulunamadı."
        )

    if not barber:

        return render_template(
            "error.html",
            error="Seçilen usta bulunamadı."
        )

    # --------------------------------------------------
    # TARİH / SAAT
    # --------------------------------------------------

    try:

        appointment_datetime = make_datetime(
            date,
            time
        )

    except ValueError:

        return render_template(
            "error.html",
            error="Geçersiz tarih veya saat."
        )

    # Geçmiş saat

    if appointment_datetime < datetime.now():

        return render_template(
            "error.html",
            error="Geçmiş bir saate randevu alınamaz."
        )

    # --------------------------------------------------
    # CİHAZ LİMİTİ
    # --------------------------------------------------

    device_id = get_device_id()

    device_count = get_device_appointment_count(
        device_id
    )

    if device_count >= MAX_DEVICE_APPOINTMENTS:

        return render_template(
            "error.html",
            error=(
                "Bu cihazdan son 24 saat içinde "
                "en fazla 3 randevu alınabilir. "
                "Yeni randevu almak için limitin "
                "yenilenmesini bekleyin."
            )
        )

    # --------------------------------------------------
    # MÜSAİTLİK
    # --------------------------------------------------

    available = is_time_available(
        date,
        time,
        service["duration"],
        barber_id
    )

    if not available:

        return render_template(
            "error.html",
            error=(
                "Bu usta seçtiğiniz saatte müsait değil. "
                "Lütfen başka bir saat veya başka bir usta seçin."
            )
        )

    # --------------------------------------------------
    # SON KONTROL
    # --------------------------------------------------

    conn = get_db()

    # Aynı usta + tarih + saat

    existing = conn.execute("""
        SELECT id

        FROM appointments

        WHERE date = ?

        AND time = ?

        AND barber_id = ?
    """, (
        date,
        time,
        barber_id
    )).fetchone()

    if existing:

        conn.close()

        return render_template(
            "error.html",
            error=(
                "Bu usta için seçtiğiniz saat "
                "artık dolu."
            )
        )

    # --------------------------------------------------
    # RANDEVU EKLE
    # --------------------------------------------------

    conn.execute("""
        INSERT INTO appointments
        (
            name,
            phone,
            service,
            date,
            time,
            barber_id,
            barber_name,
            device_id,
            created_at
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        name,

        phone,

        service["name"],

        date,

        time,

        barber["id"],

        barber["name"],

        device_id,

        datetime.now().isoformat()

    ))

    conn.commit()

    conn.close()

    # --------------------------------------------------
    # SUCCESS
    # --------------------------------------------------

    response = make_response(
        render_template(
            "success.html",

            shop=SHOP,

            name=name,

            date=date,

            time=time,

            service=service["name"],

            barber=barber["name"]
        )
    )

    response.set_cookie(
        "device_id",
        device_id,

        max_age=60 * 60 * 24 * 365,

        httponly=True,

        samesite="Lax"
    )

    return response


# ==================================================
# ADMIN LOGIN
# ==================================================

@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("admin")
        )

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        )

        password = request.form.get(
            "password",
            ""
        )

        if (
            username == ADMIN_USERNAME
            and
            password == ADMIN_PASSWORD
        ):

            session[
                "admin_logged_in"
            ] = True

            return redirect(
                url_for("admin")
            )

        return render_template(
            "admin_login.html",
            error=(
                "Kullanıcı adı veya şifre yanlış."
            )
        )

    return render_template(
        "admin_login.html"
    )


# ==================================================
# ADMIN PANEL
# ==================================================

@app.route("/admin")
def admin():

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("admin_login")
        )

    conn = get_db()

    appointments = conn.execute("""
        SELECT *

        FROM appointments

        ORDER BY date, time
    """).fetchall()

    services = conn.execute("""
        SELECT *

        FROM services

        ORDER BY id
    """).fetchall()

    barbers = conn.execute("""
        SELECT *

        FROM barbers

        ORDER BY id
    """).fetchall()

    conn.close()

    now = datetime.now()

    upcoming_appointments = []

    past_appointments = []

    for appointment in appointments:

        appointment_datetime = make_datetime(
            appointment["date"],
            appointment["time"]
        )

        if appointment_datetime >= now:

            upcoming_appointments.append(
                appointment
            )

        else:

            past_appointments.append(
                appointment
            )

    return render_template(

        "admin.html",

        shop=SHOP,

        upcoming_appointments=
        upcoming_appointments,

        past_appointments=
        past_appointments,

        services=services,

        barbers=barbers
    )


# ==================================================
# TEKLİ RANDEVU SİL
# ==================================================

@app.route(
    "/admin/appointment/delete/<int:appointment_id>",
    methods=["POST"]
)
def delete_appointment(
    appointment_id
):

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("admin_login")
        )

    conn = get_db()

    conn.execute("""
        DELETE FROM appointments
        WHERE id = ?
    """, (
        appointment_id,
    ))

    conn.commit()

    conn.close()

    return redirect(
        url_for("admin")
    )


# ==================================================
# GEÇMİŞ RANDEVULARI SİL
# ==================================================

@app.route(
    "/admin/appointments/delete-past",
    methods=["POST"]
)
def delete_past_appointments():

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("admin_login")
        )

    now = datetime.now()

    conn = get_db()

    appointments = conn.execute("""
        SELECT id, date, time

        FROM appointments
    """).fetchall()

    for appointment in appointments:

        appointment_datetime = make_datetime(
            appointment["date"],
            appointment["time"]
        )

        if appointment_datetime < now:

            conn.execute("""
                DELETE FROM appointments
                WHERE id = ?
            """, (
                appointment["id"],
            ))

    conn.commit()

    conn.close()

    return redirect(
        url_for("admin")
    )


# ==================================================
# YAKLAŞAN RANDEVULARI SİL
# ==================================================

@app.route(
    "/admin/appointments/delete-upcoming",
    methods=["POST"]
)
def delete_upcoming_appointments():

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("admin_login")
        )

    now = datetime.now()

    conn = get_db()

    appointments = conn.execute("""
        SELECT id, date, time

        FROM appointments
    """).fetchall()

    for appointment in appointments:

        appointment_datetime = make_datetime(
            appointment["date"],
            appointment["time"]
        )

        if appointment_datetime >= now:

            conn.execute("""
                DELETE FROM appointments
                WHERE id = ?
            """, (
                appointment["id"],
            ))

    conn.commit()

    conn.close()

    return redirect(
        url_for("admin")
    )


# ==================================================
# TÜM RANDEVULARI SİL
# ==================================================

@app.route(
    "/admin/appointments/delete-all",
    methods=["POST"]
)
def delete_all_appointments():

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("admin_login")
        )

    conn = get_db()

    conn.execute(
        "DELETE FROM appointments"
    )

    conn.commit()

    conn.close()

    return redirect(
        url_for("admin")
    )


# ==================================================
# HİZMET EKLE
# ==================================================

@app.route(
    "/admin/service/add",
    methods=["POST"]
)
def add_service():

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("admin_login")
        )

    name = request.form.get(
        "name",
        ""
    ).strip()

    duration = request.form.get(
        "duration",
        ""
    )

    price = request.form.get(
        "price",
        "0"
    )

    if not name:

        return redirect(
            url_for("admin")
        )

    try:

        duration = int(duration)

    except ValueError:

        return redirect(
            url_for("admin")
        )

    try:

        price = float(price)

    except ValueError:

        price = 0

    conn = get_db()

    conn.execute("""
        INSERT INTO services
        (
            name,
            duration,
            price
        )

        VALUES (?, ?, ?)
    """, (
        name,
        duration,
        price
    ))

    conn.commit()

    conn.close()

    return redirect(
        url_for("admin")
    )


# ==================================================
# HİZMET GÜNCELLE (Süre + Fiyat)
# ==================================================

@app.route(
    "/admin/service/update",
    methods=["POST"]
)
def update_service():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    service_id = request.form.get("id")
    duration = request.form.get("duration")
    price = request.form.get("price")

    try:
        service_id = int(service_id)
        duration = int(duration)
        price = float(price)
    except (ValueError, TypeError):
        return redirect(url_for("admin"))

    if duration < 1:
        return redirect(url_for("admin"))

    conn = get_db()

    conn.execute("""
        UPDATE services
        SET duration = ?,
            price = ?
        WHERE id = ?
    """, (
        duration,
        price,
        service_id
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


# ==================================================
# HİZMET SİL
# ==================================================

@app.route(
    "/admin/service/delete/<int:service_id>",
    methods=["POST"]
)
def delete_service(service_id):

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("admin_login")
        )

    conn = get_db()

    conn.execute("""
        DELETE FROM services

        WHERE id = ?
    """, (
        service_id,
    ))

    conn.commit()

    conn.close()

    return redirect(
        url_for("admin")
    )


# ==================================================
# USTA EKLE
# ==================================================

@app.route(
    "/admin/barber/add",
    methods=["POST"]
)
def add_barber():

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("admin_login")
        )

    name = request.form.get(
        "name",
        ""
    ).strip()

    if not name:

        return redirect(
            url_for("admin")
        )

    conn = get_db()

    conn.execute("""
        INSERT INTO barbers
        (name)

        VALUES (?)
    """, (
        name,
    ))

    conn.commit()

    conn.close()

    return redirect(
        url_for("admin")
    )


# ==================================================
# USTA SİL
# ==================================================

@app.route(
    "/admin/barber/delete/<int:barber_id>",
    methods=["POST"]
)
def delete_barber(barber_id):

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("admin_login")
        )

    conn = get_db()

    # Bu ustaya ait eski randevuların
    # geçmiş bilgisi bozulmasın.

    conn.execute("""
        UPDATE appointments

        SET barber_id = NULL

        WHERE barber_id = ?
    """, (
        barber_id,
    ))

    conn.execute("""
        DELETE FROM barbers

        WHERE id = ?
    """, (
        barber_id,
    ))

    conn.commit()

    conn.close()

    return redirect(
        url_for("admin")
    )


# ==================================================
# LOGOUT
# ==================================================

@app.route(
    "/admin/logout"
)
def admin_logout():

    session.pop(
        "admin_logged_in",
        None
    )

    return redirect(
        url_for("admin_login")
    )


# ==================================================
# PROGRAM
# ==================================================

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True
    )