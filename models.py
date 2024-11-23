from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
class Course(db.Model):
    cid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    fees = db.Column(db.Integer, nullable=False)
    instructor = db.Column(db.String(100), nullable=False)
    videos = db.relationship('Video', backref='course', lazy=True)  # One-to-many relationship with Video

    def __repr__(self):
        return f"<Course {self.name}>"
class Video(db.Model):
    vid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(255), nullable=False)
    cid = db.Column(db.Integer, db.ForeignKey('course.cid'), nullable=False)  # Assuming you have a Course model
    # date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Video {self.title}>"