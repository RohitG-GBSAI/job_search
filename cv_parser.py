import os
import re
import logging
import PyPDF2
import docx
import spacy
from spacy.matcher import PhraseMatcher
import nltk
from nltk.corpus import stopwords
from app import app

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Load spaCy model (small English model)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Try using a simpler model if the specific one isn't available
    try:
        nlp = spacy.load("en")
    except OSError:
        logging.warning("SpaCy model not available. Using basic NLP processing instead.")
        nlp = None

class CVParser:
    """Class for parsing and extracting information from CVs"""
    
    def __init__(self):
        # Common skills to look for in CVs
        self.common_skills = [
            # Programming Languages
            "Python", "Java", "JavaScript", "C++", "C#", "Ruby", "PHP", "Swift", "Kotlin", "Go",
            # Web Development
            "HTML", "CSS", "React", "Angular", "Vue.js", "Node.js", "Express", "Django", "Flask", "Spring",
            # Data Science & ML
            "Machine Learning", "Data Science", "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas", "NumPy",
            # Database
            "SQL", "MySQL", "PostgreSQL", "MongoDB", "Oracle", "SQLite", "NoSQL", "Firebase",
            # DevOps
            "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Jenkins", "Git", "CI/CD", "Linux",
            # Other Technical
            "REST API", "GraphQL", "Microservices", "Agile", "Scrum", "Jira", "Confluence", "Tableau", "Power BI",
            # Soft Skills
            "Project Management", "Team Leadership", "Communication", "Problem Solving", "Critical Thinking"
        ]
        
        if nlp:
            # Create skill matcher
            self.skill_matcher = PhraseMatcher(nlp.vocab)
            skill_patterns = [nlp(skill) for skill in self.common_skills]
            self.skill_matcher.add("SKILLS", None, *skill_patterns)
        
        self.education_keywords = ["education", "degree", "university", "college", "bachelor", "master", "phd", "diploma"]
        self.experience_keywords = ["experience", "employment", "work history", "job history", "professional experience"]
    
    def parse_file(self, file_path):
        """Parse the CV file and extract text based on file type"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.pdf':
                return self.parse_pdf(file_path)
            elif file_ext == '.docx':
                return self.parse_docx(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
        except Exception as e:
            logging.error(f"Error parsing file {file_path}: {str(e)}")
            raise
    
    def parse_pdf(self, file_path):
        """Extract text from PDF file"""
        text = ""
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
        return text
    
    def parse_docx(self, file_path):
        """Extract text from DOCX file"""
        doc = docx.Document(file_path)
        return '\n'.join([p.text for p in doc.paragraphs])
    
    def extract_sections(self, text):
        """Extract key sections from the CV"""
        # Get the raw text in lowercase for section detection
        text_lower = text.lower()
        
        # Extract skills
        skills = self.extract_skills(text)
        
        # Extract education section
        education_section = ""
        for keyword in self.education_keywords:
            if keyword in text_lower:
                # Find the section that starts with the education keyword
                match = re.search(r'(?i)(' + keyword + r'.*?)(?:\n\s*\n|\Z)', text, re.DOTALL)
                if match:
                    education_section = match.group(1).strip()
                    break
        
        # Extract experience section
        experience_section = ""
        for keyword in self.experience_keywords:
            if keyword in text_lower:
                # Find the section that starts with the experience keyword
                match = re.search(r'(?i)(' + keyword + r'.*?)(?:\n\s*\n|\Z)', text, re.DOTALL)
                if match:
                    experience_section = match.group(1).strip()
                    break
        
        return {
            "skills": ", ".join(skills),
            "education": education_section,
            "experience": experience_section,
            "raw_text": text
        }
    
    def extract_skills(self, text):
        """Extract skills from the CV text"""
        if nlp:
            # Use spaCy for better skill extraction
            doc = nlp(text)
            skill_matches = self.skill_matcher(doc)
            skills = set()
            
            for match_id, start, end in skill_matches:
                skill = doc[start:end].text
                skills.add(skill)
                
            # Add additional skills by looking for common patterns like "Proficient in X"
            for token in doc:
                if token.text.lower() in ["proficient", "experienced", "skilled", "expert", "knowledge"]:
                    # Look ahead for potential skills
                    for i in range(1, 5):  # Look at the next few tokens
                        if token.i + i < len(doc) and doc[token.i + i].text in self.common_skills:
                            skills.add(doc[token.i + i].text)
            
            return list(skills)
        else:
            # Fallback to simpler extraction using regex
            skills = []
            for skill in self.common_skills:
                if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
                    skills.append(skill)
            return skills
