from flask import request, jsonify
from app import app
from cv_parser import CVParser
from job_matcher import JobMatcher
import os

# Initialize once
cv_parser = CVParser()
job_matcher = JobMatcher()

@app.route("/match_jobs", methods=["POST"])
def match_jobs():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Save uploaded file temporarily
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    try:
        # Parse CV
        text = cv_parser.parse_file(filepath)
        cv_data = cv_parser.extract_sections(text)

        # Match jobs
        matches = job_matcher.match_jobs_to_cv(cv_data, location="Remote", limit=10)

        return jsonify({"matches": matches}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)
