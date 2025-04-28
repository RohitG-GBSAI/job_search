import logging
import requests
import uuid
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app import app

# ✅ Muse category and keyword mappings
MUSE_CATEGORIES = [
    "Data Science", "Data and Analytics", "Computer and IT",
    "Software Engineering", "Science and Engineering",
    "Project Management", "Product", "Design", "Writing and Editing",
    "Marketing and Communications", "Customer Service", "Finance",
    "Human Resources", "Sales", "Education", "Healthcare",
    "Operations", "Legal", "Transportation and Logistics",
]

CATEGORY_KEYWORDS = {
    "Data Science": {"python", "r", "pandas", "machine", "statistics", "scikit"},
    "Data and Analytics": {"excel", "sql", "tableau", "powerbi", "analytics"},
    "Software Engineering": {"java", "javascript", "react", "aws", "docker", "c++"},
    "Computer and IT": {"support", "network", "hardware", "it", "cloud"},
    "Science and Engineering": {"lab", "physics", "biology", "chemistry", "engineer"},
    "Project Management": {"jira", "scrum", "kanban", "pmp", "stakeholders"},
    "Product": {"roadmap", "requirements", "user research", "ux"},
    "Design": {"adobe", "photoshop", "illustrator", "figma"},
    "Writing and Editing": {"copywriting", "seo", "editing", "content"},
    "Marketing and Communications": {"social media", "branding", "marketing", "campaign"},
    "Finance": {"accounting", "tax", "audit", "financial", "budget"},
    "Human Resources": {"recruitment", "onboarding", "hr"},
    "Sales": {"salesforce", "pipeline", "crm", "quota"},
    "Customer Service": {"ticketing", "support", "helpdesk"},
    "Education": {"teaching", "curriculum", "lesson"},
    "Healthcare": {"nurse", "medical", "clinical"},
    "Operations": {"logistics", "supply chain", "ops"},
    "Legal": {"contract", "compliance", "regulation"},
    "Transportation and Logistics": {"fleet", "warehouse", "supply"},
}

class JobMatcher:
    """Class for matching CVs with job listings via The Muse API"""

    def __init__(self):
        pass  # No API key needed for Muse!

    def pick_muse_categories(self, cv_tokens, top_k=3):
        scores = []
        for cat, keywords in CATEGORY_KEYWORDS.items():
            overlap = len(cv_tokens & keywords)
            if overlap:
                scores.append((overlap, cat))
        return [c for _, c in sorted(scores, reverse=True)[:top_k]] or ["General"]

    def muse_search_jobs(self, categories, location="Remote", pages=2):
        jobs = []
        for cat in categories:
            for page in range(pages):
                params = {
                    "page": page,
                    "location": location,
                    "category": cat
                }
                try:
                    response = requests.get("https://www.themuse.com/api/public/jobs", params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        for job in data.get("results", []):
                            jobs.append({
                                "id": job.get("id", str(uuid.uuid4())),
                                "title": job.get("name", "Unknown Position"),
                                "company": job.get("company", {}).get("name", "Unknown Company"),
                                "location": job.get("locations", ""),
                                "description": job.get("contents", ""),
                                "requirements": job.get("contents", ""),
                                "url": job.get("refs", {}).get("landing_page", ""),
                                "posted_time": job.get("publication_date", "")
                            })
                    else:
                        logging.error(f"Muse API error: {response.status_code} - {response.text}")
                except Exception as e:
                    logging.error(f"Error fetching Muse jobs: {str(e)}")
        return {"jobs": jobs}

    def calculate_match_score(self, cv_data, job_data):
        try:
            cv_text = f"{cv_data.get('raw_text', '')} {cv_data.get('skills', '')} {cv_data.get('education', '')} {cv_data.get('experience', '')}"
            job_text = f"{job_data.get('title', '')} {job_data.get('description', '')} {job_data.get('requirements', '')}"
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([cv_text, job_text])
            cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            match_score = round(cosine_sim * 100, 2)
            if cv_data.get('skills') and job_data.get('requirements'):
                cv_skills = [skill.strip().lower() for skill in cv_data.get('skills').split(',')]
                job_req = job_data.get('requirements').lower()
                skill_matches = sum(1 for skill in cv_skills if skill and skill in job_req)
                skill_bonus = min(skill_matches * 2, 20)
                match_score = min(match_score + skill_bonus, 100)
            return match_score
        except Exception as e:
            logging.error(f"Error calculating match score: {str(e)}")
            return 0.0

    def match_jobs_to_cv(self, cv_data, location=None, limit=10):
        raw_text = cv_data.get('raw_text', '').lower()
        skills = set(word.strip() for word in cv_data.get('skills', '').lower().split(','))
        experiences = set(word.strip() for word in cv_data.get('experience', '').lower().split(','))
        education = set(word.strip() for word in cv_data.get('education', '').lower().split(','))
        
        cv_tokens = skills | experiences | education | set(raw_text.split())
        categories = self.pick_muse_categories(cv_tokens)
        
        job_results = self.muse_search_jobs(categories, location=location, pages=2)
        jobs = job_results.get('jobs', [])

        matched_jobs = []
        for job in jobs:
            score = self.calculate_match_score(cv_data, job)
            job['match_score'] = score
            matched_jobs.append(job)

        matched_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        top_matches = matched_jobs[:limit]

        return top_matches
