from datetime import datetime
from extensions import db
from enum import Enum

class UserType(Enum):
    JOB_SEEKER = "job_seeker"
    BUSINESS = "business"

class JobListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    employer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    employer = db.relationship('User', backref=db.backref('job_listings', lazy=True))

    def __repr__(self):
        return f'<JobListing {self.title}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.Enum(UserType), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    skills = db.Column(db.String(255), nullable=True)
    experience = db.Column(db.String(255), nullable=True)

    company_name = db.Column(db.String(120), nullable=True)
    company_description = db.Column(db.Text, nullable=True)
    company_website = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id], backref=db.backref('sent_messages', lazy='dynamic'))
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref=db.backref('received_messages', lazy='dynamic'))

    def __repr__(self):
        return f'<Message {self.id}, from {self.sender.username} to {self.recipient.username}>'

class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_seeker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_listing_id = db.Column(db.Integer, db.ForeignKey('job_listing.id'), nullable=False)
    application_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    job_seeker = db.relationship('User', foreign_keys=[job_seeker_id], backref=db.backref('job_applications', lazy=True))
    job_listing = db.relationship('JobListing', foreign_keys=[job_listing_id], backref=db.backref('job_applications', lazy=True))

    def __repr__(self):
        return f'<JobApplication {self.id}, from {self.job_seeker.username} to {self.job_listing.title}>'

class SavedJob(db.Model):
    __tablename__ = 'saved_jobs'
    id = db.Column(db.Integer, primary_key=True)
    job_seeker_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_listing_id = db.Column(db.Integer, db.ForeignKey('job_listings.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    job_seeker = db.relationship("User", backref="saved_jobs")
    job_listing = db.relationship("JobListing", backref="saved_by_users")

class TimeSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    day_of_week = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<TimeSlot {self.start_time} - {self.end_time} on {self.day_of_week}>'
