from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SessionFeed(db.Model):
    __tablename__ = 'sessions_feed'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, nullable=False)
    share_link = db.Column(db.Text, nullable=False)
    target_link = db.Column(db.Text, nullable=True)
    report_title = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=True)
    preview_image = db.Column(db.Text, nullable=True)
    thumbnail = db.Column(db.Text, nullable=True)
