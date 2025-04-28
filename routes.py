import os
import uuid
import logging
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from app import app, db
from models import Resume, JobMatch
from cv_parser import CVParser
from job_matcher import JobMatcher
import json

# Initialize parser and matcher
cv_parser = CVParser()
job_matcher = JobMatcher()

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    """Render the home page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_cv():
    """Handle CV upload and processing"""
    # Check if a file was uploaded
    if 'cv_file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('index'))
    
    file = request.files['cv_file']
    
    # Check if a file was actually selected
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    # Check if the file type is allowed
    if not allowed_file(file.filename):
        flash('File type not supported. Please upload a PDF or DOCX file.', 'error')
        return redirect(url_for('index'))
    
    try:
        # Generate a secure filename with unique ID
        filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file
        file.save(file_path)
        
        # Parse the CV
        parsed_text = cv_parser.parse_file(file_path)
        sections = cv_parser.extract_sections(parsed_text)
        
        # Get job search preferences
        job_title = request.form.get('job_title', '')
        location = request.form.get('location', '')
        
        # Store in database
        resume = Resume(
            filename=filename,
            original_filename=secure_filename(file.filename),
            raw_text=sections['raw_text'],
            skills=sections['skills'],
            education=sections['education'],
            experience=sections['experience'],
            job_title=job_title,
            location=location
        )
        
        db.session.add(resume)
        db.session.commit()
        
        # Store resume_id in session for later access
        session['resume_id'] = resume.id
        
        # Match jobs
        matched_jobs = job_matcher.match_jobs_to_cv(
            sections, 
            job_title=job_title, 
            location=location
        )
        
        # Store matches in database
        for job in matched_jobs:
            job_match = JobMatch(
                resume_id=resume.id,
                job_id=job.get('id', str(uuid.uuid4())),
                job_title=job.get('title', 'Unknown Position'),
                company=job.get('company', 'Unknown Company'),
                location=job.get('location', ''),
                description=job.get('description', ''),
                url=job.get('url', ''),
                score=job.get('match_score', 0)
            )
            db.session.add(job_match)
        
        db.session.commit()
        
        return redirect(url_for('results', resume_id=resume.id))
        
    except Exception as e:
        logging.error(f"Error processing CV: {str(e)}")
        flash('Error processing your CV. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/results/<int:resume_id>')
def results(resume_id):
    """Display job matching results"""
    resume = Resume.query.get_or_404(resume_id)
    job_matches = JobMatch.query.filter_by(resume_id=resume_id).order_by(JobMatch.score.desc()).all()
    
    return render_template(
        'results.html', 
        resume=resume, 
        job_matches=job_matches,
        skills=resume.skills_list()
    )

@app.route('/error')
def error():
    """Display error page"""
    return render_template('error.html')

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('error.html', error="Internal server error"), 500
