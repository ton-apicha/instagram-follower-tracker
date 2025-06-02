# D:\instagram_tracker\app.py

from flask import Flask, render_template, request, redirect, url_for, flash
from database import db, Account, FollowerData, init_db # Import จาก database.py

# สร้าง Flask application instance
app = Flask(__name__)

# --- Configuration ---
# ตั้งค่า Secret Key: จำเป็นสำหรับการใช้งาน session, flash messages, etc.
# ควรเปลี่ยนเป็นค่า random ที่คาดเดายากใน production
app.config['SECRET_KEY'] = 'your_very_secret_key_here_change_me' # <<<< เปลี่ยนค่านี้!

# ตั้งค่า URI ของฐานข้อมูล SQLite
# 'sqlite:///instagram_tracker.db' หมายถึงไฟล์ฐานข้อมูลชื่อ instagram_tracker.db
# จะถูกสร้างขึ้นในโฟลเดอร์ instance/ ภายในโปรเจกต์ของคุณโดยอัตโนมัติ
# หรือคุณสามารถระบุ full path ได้ เช่น 'sqlite:///D:/instagram_tracker/instagram_tracker.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instagram_tracker.db'

# ปิดการ track modifications ของ SQLAlchemy เพื่อลด overhead (ถ้าไม่ต้องการก็ตั้งเป็น True ได้)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Database Initialization ---
# ผูก SQLAlchemy instance (db) ที่เราสร้างใน database.py เข้ากับ Flask app นี้
db.init_app(app)

# สร้างตารางในฐานข้อมูล (ถ้ายังไม่มี)
# เราจะใช้ Flask CLI command ในการสร้างตารางแทนการเรียก init_db() โดยตรงในโค้ดส่วนนี้
# เพื่อให้จัดการได้ง่ายขึ้น (จะอธิบายเพิ่มเติม)

# --- Routes (เส้นทาง URL ของเว็บ) ---

@app.route('/')
def index():
    """
    หน้าหลักของโปรแกรม แสดงรายการบัญชี IG ที่ติดตาม
    """
    try:
        accounts = Account.query.order_by(Account.date_added.desc()).all()
    except Exception as e:
        # ในกรณีที่ฐานข้อมูลยังไม่ได้ถูกสร้าง หรือมีปัญหาในการเชื่อมต่อ
        # เราจะแสดงข้อความแจ้งเตือน และอาจจะ redirect ไปหน้า setup หรือแสดงข้อผิดพลาด
        print(f"Error querying accounts: {e}") # Log error ไปที่ console
        flash(f"Error loading accounts: {e}. Please ensure the database is initialized.", "danger")
        accounts = [] # แสดงรายการว่างถ้ามีปัญหา

    return render_template('index.html', accounts=accounts, title="Instagram Tracker Dashboard")

@app.route('/add_account', methods=['GET', 'POST'])
def add_account():
    """
    หน้าสำหรับเพิ่มบัญชี IG ใหม่
    """
    if request.method == 'POST':
        username = request.form.get('username')
        profile_url = request.form.get('profile_url')
        notes = request.form.get('notes')

        if not username:
            flash('Username is required!', 'danger') # 'danger' เป็น category ของ bootstrap alert
            return redirect(url_for('add_account'))

        # ตรวจสอบว่า username ซ้ำหรือไม่
        existing_account = Account.query.filter_by(username=username).first()
        if existing_account:
            flash(f'Account with username "{username}" already exists!', 'warning')
            return redirect(url_for('add_account'))

        try:
            new_account = Account(
                username=username,
                profile_url=profile_url,
                notes=notes
            )
            db.session.add(new_account)
            db.session.commit()
            flash(f'Account "{username}" added successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback() # Rollback ถ้ามีปัญหาในการ commit
            flash(f'Error adding account: {e}', 'danger')
            print(f"Error adding account: {e}") # Log error
            return redirect(url_for('add_account'))

    return render_template('add_account.html', title="Add New IG Account")

# --- Flask CLI Command for Database Initialization ---
@app.cli.command("init-db")
def init_db_command():
    """Clear existing data and create new tables."""
    # db.drop_all() # ถ้าต้องการลบตารางเก่าทิ้งทั้งหมดก่อนสร้างใหม่ (ระวัง! ข้อมูลจะหาย)
    init_db(app) # เรียกฟังก์ชัน init_db จาก database.py
    print("Initialized the database.")

# --- Main execution ---
if __name__ == '__main__':
    # การใช้ app.app_context() ตรงนี้เพื่อให้แน่ใจว่า db.create_all() (ถ้าจะเรียกตรงนี้)
    # ทำงานภายใต้ application context ที่ถูกต้อง
    # แต่เราแนะนำให้ใช้ Flask CLI command "flask init-db" แทน
    # with app.app_context():
    #     init_db(app) # สร้างตารางเมื่อรัน app.py โดยตรง (ถ้ายังไม่มี)

    app.run(debug=True) # debug=True ทำให้ Flask auto-reload เมื่อมีการแก้โค้ด และแสดง error ที่ละเอียด