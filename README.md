# CV Job Matcher - AI-Powered Career Assistant

An AI-powered job assistant tool that processes CVs, extracts key information, and matches users with relevant job opportunities using SerpApi's Google Jobs API.

## Features

- Process uploaded CVs in common formats (PDF, DOCX)
- Extract text and identify key skills, experiences, and keywords
- Integrate with SerpApi to fetch real-time job opportunities
- Employ similarity-scoring algorithm to rank matches based on profile alignment
- Display personalized job recommendations with match scores

## Installation

1. Clone this repository to your local machine
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install the required dependencies (see dependencies.txt):
   ```
   pip install flask flask-sqlalchemy gunicorn werkzeug email-validator nltk numpy psycopg2-binary pypdf2 python-docx scikit-learn spacy requests
   ```
5. Download required NLTK data:
   ```
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```
6. Download spaCy model:
   ```
   python -m spacy download en_core_web_sm
   ```
7. Set up environment variables:
   - `JOB_API_KEY`: Your SerpApi API key (default: 166c7792d615bc4c30b784e0c5b7827a45b2e43fcd67b37e15d45d518b87afd2)
   - `SESSION_SECRET`: A random string for session security

## Usage

1. Run the application:
   ```
   python main.py
   ```
   or with gunicorn:
   ```
   gunicorn --bind 0.0.0.0:5000 main:app
   ```

2. Open your browser and navigate to `http://localhost:5000`

3. Upload your CV/resume (PDF or DOCX format)

4. Optionally specify desired job title and location

5. View matched job opportunities with relevance scores

## Project Structure

- `app.py`: Main Flask application configuration
- `models.py`: Database models for Resume and JobMatch
- `cv_parser.py`: CV parsing and information extraction
- `job_matcher.py`: Job matching algorithm and API integration
- `routes.py`: Application routes and request handling
- `templates/`: HTML templates for the web interface
- `static/`: CSS, JavaScript, and other static assets

## Technologies Used

- Python 3.11
- Flask & Flask-SQLAlchemy
- NLTK & spaCy for natural language processing
- scikit-learn for TF-IDF and cosine similarity
- SerpApi for job listings
- Bootstrap for responsive UI

## License

This project is licensed under the MIT License.