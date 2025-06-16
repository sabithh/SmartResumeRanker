# A predefined list of skills. You can expand this list extensively.
import re

SKILLS_DB = [
    'python', 'java', 'c++', 'javascript', 'typescript', 'sql', 'nosql', 'mongodb', 'postgresql',
    'react', 'angular', 'vue', 'node.js', 'express.js', 'django', 'flask', 'fastapi',
    'aws', 'azure', 'google cloud', 'gcp', 'docker', 'kubernetes', 'git', 'jenkins', 'ci/cd',
    'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
    'data analysis', 'data visualization', 'tableau', 'power bi', 'communication', 'teamwork', 'problem-solving'
]


def extract_skills(text):
    """Extracts skills from a text based on a predefined list."""
    # Preprocess text to match skill format (lowercase, simple words)
    cleaned_text = " ".join(text.lower().split())

    found_skills = set()
    for skill in SKILLS_DB:
        if re.search(r'\b' + re.escape(skill) + r'\b', cleaned_text):
            found_skills.add(skill)
    return list(found_skills)


def find_missing_skills(job_skills, resume_skills):
    """Finds skills that are in the job description but not in the resume."""
    return [skill for skill in job_skills if skill not in resume_skills]