from datetime import datetime
from app import db

class Resume(db.Model):
    """Model for storing parsed resume data"""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Parsed content
    raw_text = db.Column(db.Text)
    skills = db.Column(db.Text)
    education = db.Column(db.Text)
    experience = db.Column(db.Text)
    
    # Job search preferences
    job_title = db.Column(db.String(255))
    location = db.Column(db.String(255))
    
    def __repr__(self):
        return f"<Resume {self.original_filename}>"
    
    def skills_list(self):
        """Convert skills from string to list"""
        if self.skills:
            return [skill.strip() for skill in self.skills.split(',')]
        return []
    
class JobMatch(db.Model):
    """Model for storing job matches"""
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'), nullable=False)
    job_id = db.Column(db.String(255), nullable=False)
    job_title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255))
    location = db.Column(db.String(255))
    description = db.Column(db.Text)
    url = db.Column(db.String(512))
    score = db.Column(db.Float, nullable=False)  # Match score
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    resume = db.relationship('Resume', backref=db.backref('job_matches', lazy=True))
    
    def __repr__(self):
        return f"<JobMatch {self.job_title} - Score: {self.score}>"
