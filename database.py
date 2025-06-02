# D:\instagram_tracker\database.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# สร้าง instance ของ SQLAlchemy โดยยังไม่ได้ผูกกับ Flask app โดยตรงในไฟล์นี้
# เราจะผูกกับ app ในไฟล์ app.py
db = SQLAlchemy()

class Account(db.Model):
    """
    โมเดลสำหรับเก็บข้อมูลบัญชี Instagram ที่ต้องการติดตาม
    """
    __tablename__ = 'accounts'  # ชื่อตารางในฐานข้อมูล

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    ig_user_id = db.Column(db.String(120), unique=True, nullable=True) # Optional, but good to have
    profile_url = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # ความสัมพันธ์: หนึ่ง Account มีได้หลาย FollowerData
    # backref='account' จะสร้าง attribute ชื่อ 'account' ใน FollowerData model
    # เพื่อให้สามารถเข้าถึง Account object จาก FollowerData object ได้
    # lazy='dynamic' หมายความว่า SQLAlchemy จะคืนค่าเป็น query object แทนที่จะโหลดข้อมูลทั้งหมดทันที
    # ซึ่งมีประโยชน์เมื่อมีข้อมูล FollowerData จำนวนมากสำหรับ Account หนึ่งๆ
    follower_data = db.relationship('FollowerData', backref='account', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Account {self.username}>'

class FollowerData(db.Model):
    """
    โมเดลสำหรับเก็บข้อมูลจำนวนผู้ติดตามของแต่ละบัญชี ณ เวลาต่างๆ
    """
    __tablename__ = 'follower_data' # ชื่อตารางในฐานข้อมูล

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False) # Foreign Key ไปยังตาราง accounts
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    follower_count = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<FollowerData for Account ID {self.account_id} at {self.timestamp}: {self.follower_count} followers>'

def init_db(app):
    """
    ฟังก์ชันสำหรับ khởi tạo ฐานข้อมูลและสร้างตาราง
    จะถูกเรียกจาก app.py
    """
    with app.app_context():
        db.create_all()
    print("Database tables created (if they didn't exist).")