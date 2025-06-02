# D:\instagram_tracker\database.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from urllib.parse import urlparse # Import เพิ่มเติม

db = SQLAlchemy()

class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    # username ตอนนี้จะเก็บ URL เต็มๆ หรือชื่อบัญชีก็ได้, แต่เราจะเน้นที่ profile_url
    username = db.Column(db.String(255), unique=True, nullable=False) # เพิ่มความยาวเผื่อ URL
    ig_user_id = db.Column(db.String(120), unique=True, nullable=True)
    profile_url = db.Column(db.String(255), nullable=True) # อาจจะซ้ำซ้อนกับ username ถ้า username คือ URL
    notes = db.Column(db.Text, nullable=True)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    follower_data = db.relationship('FollowerData', backref='account', lazy='dynamic', cascade="all, delete-orphan")

    @property
    def display_username(self):
        """
        พยายามดึงชื่อผู้ใช้จาก profile_url หรือ username
        ถ้า profile_url มีค่า จะใช้ profile_url ก่อน
        ถ้าไม่สำเร็จ จะคืนค่า username เดิม (ซึ่งอาจเป็น URL หรือชื่อผู้ใช้)
        """
        url_to_parse = None
        if self.profile_url:
            url_to_parse = self.profile_url
        elif self.username and ("/" in self.username and "." in self.username): # ตรวจสอบคร่าวๆ ว่า username อาจเป็น URL
            url_to_parse = self.username

        if url_to_parse:
            try:
                parsed_url = urlparse(url_to_parse)
                # 경로에서 '/'를 기준으로 나누고, 비어있지 않은 마지막 부분을 가져옴
                # เช่น https://www.instagram.com/username/ -> ['username']
                # หรือ https://www.instagram.com/username -> ['username']
                path_parts = [part for part in parsed_url.path.split('/') if part]
                if path_parts:
                    return path_parts[-1] # เอาส่วนสุดท้ายที่ไม่ใช่ค่าว่าง
            except Exception:
                # ถ้ามีปัญหาในการ parse URL ก็ให้คืนค่า username เดิมไปก่อน
                pass
        return self.username # ถ้าไม่มี profile_url หรือ parse ไม่ได้ ก็คืน username เดิม

    def __repr__(self):
        # แสดง display_username แทน username ปกติเพื่อให้ debug ง่ายขึ้น
        return f'<Account {self.display_username}>'

class FollowerData(db.Model):
    __tablename__ = 'follower_data'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    follower_count = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<FollowerData for Account ID {self.account_id} at {self.timestamp}: {self.follower_count} followers>'

def init_db(app):
    with app.app_context():
        db.create_all()
    print("Database tables created (if they didn't exist).")