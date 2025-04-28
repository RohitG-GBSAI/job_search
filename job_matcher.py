import logging
import requests
import os
import json
import uuid
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app import app

class JobMatcher:
    """Class for matching CVs with job listings"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or app.config.get('JOB_API_KEY')
        if not self.api_key or self.api_key == 'default_key':
            logging.warning("No job API key provided. Job matching may not work.")
    
    def search_jobs(self, query, location=None, limit=20):
        """
        Search for jobs using SerpApi Google Jobs API
        """
        try:
            api_url = "https://serpapi.com/search"
            
            params = {
                "engine": "google_jobs",
                "q": query,
                "api_key": self.api_key,
                "hl": "en"
            }
            
            if location:
                params["location"] = location
                
            logging.debug(f"Searching jobs with params: {params}")
            response = requests.get(api_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                jobs_list = []
                
                # Extract jobs from the SerpApi response
                if "jobs_results" in data:
                    for job in data["jobs_results"][:limit]:
                        job_data = {
                            "id": job.get("job_id", str(uuid.uuid4())),
                            "title": job.get("title", "Unknown Position"),
                            "company": job.get("company_name", "Unknown Company"),
                            "location": job.get("location", ""),
                            "description": job.get("description", ""),
                            "requirements": job.get("description", ""),  # Using description for requirements too
                            "url": job.get("apply_link", "") or job.get("apply_options", [{}])[0].get("link", "") if job.get("apply_options") else "",
                            "posted_time": job.get("detected_extensions", {}).get("posted_at", "")
                        }
                        jobs_list.append(job_data)
                
                logging.info(f"Found {len(jobs_list)} jobs")
                return {"jobs": jobs_list}
            else:
                logging.error(f"API error: {response.status_code} - {response.text}")
                return {"jobs": []}
                
        except Exception as e:
            logging.error(f"Error fetching jobs: {str(e)}")
            return {"jobs": []}
    
    def calculate_match_score(self, cv_data, job_data):
        """
        Calculate the match score between a CV and a job listing
        using TF-IDF and cosine similarity
        """
        try:
            # Create a corpus of documents
            cv_text = f"{cv_data.get('raw_text', '')} {cv_data.get('skills', '')} {cv_data.get('education', '')} {cv_data.get('experience', '')}"
            job_text = f"{job_data.get('title', '')} {job_data.get('description', '')} {job_data.get('requirements', '')}"
            
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(stop_words='english')
            
            # Fit and transform the texts
            tfidf_matrix = vectorizer.fit_transform([cv_text, job_text])
            
            # Calculate cosine similarity
            cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Convert to percentage and round to 2 decimal places
            match_score = round(cosine_sim * 100, 2)
            
            # Boost score based on skill matches
            if cv_data.get('skills') and job_data.get('requirements'):
                cv_skills = [skill.strip().lower() for skill in cv_data.get('skills').split(',')]
                job_req = job_data.get('requirements').lower()
                
                skill_matches = sum(1 for skill in cv_skills if skill and skill in job_req)
                skill_bonus = min(skill_matches * 2, 20)  # Max 20% bonus from skills
                
                match_score = min(match_score + skill_bonus, 100)
            
            return match_score
        
        except Exception as e:
            logging.error(f"Error calculating match score: {str(e)}")
            return 0.0
    
    def match_jobs_to_cv(self, cv_data, job_title=None, location=None, limit=10):
        """
        Find matching jobs for the given CV data
        """
        job_title = job_title or cv_data.get('job_title', '')
        
        # If no job title is provided, try to extract one from the CV
        if not job_title:
            # Get the first line that might contain a title
            first_lines = cv_data.get('raw_text', '').split('\n')[:5]
            for line in first_lines:
                if any(title in line.lower() for title in ['developer', 'engineer', 'designer', 'manager', 'analyst']):
                    job_title = line.strip()
                    break
            
            # If still no title, use a generic search
            if not job_title:
                job_title = "software"
        
        # Search for jobs
        job_results = self.search_jobs(job_title, location, limit=limit*3)  # Get more to filter by score
        jobs = job_results.get('jobs', [])
        
        # Calculate match scores
        matched_jobs = []
        for job in jobs:
            score = self.calculate_match_score(cv_data, job)
            job['match_score'] = score
            matched_jobs.append(job)
        
        # Sort by match score and limit results
        matched_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        top_matches = matched_jobs[:limit]
        
        return top_matches
