import re

# --- Skill Database ---
# IMPORTANT: These lists should be customized to match the key skills in your job_description.txt
# This provides the basis for the weighted skill score.

REQUIRED_SKILLS = [
    'python', 'django', 'flask', 'react', 'sql', 'git', 'aws'
]

PREFERRED_SKILLS = [
    'javascript', 'postgresql', 'docker', 'ci/cd', 'problem-solving', 'teamwork', 'communication'
]


def extract_skills(text, skill_list):
    """
    Extracts a list of skills from a body of text.

    Args:
        text (str): The text to search through (e.g., from a resume).
        skill_list (list): The list of skills to search for.

    Returns:
        list: A list of skills found in the text.
    """
    # Using a set for faster storage of found skills and to avoid duplicates
    found_skills = set()
    # Preprocess text to ensure consistent matching (lowercase, single spaces)
    cleaned_text = " ".join(text.lower().split())

    for skill in skill_list:
        # Use regex to match whole words only, preventing partial matches (e.g., 'git' in 'digital')
        # The `\b` asserts a word boundary.
        if re.search(r'\b' + re.escape(skill) + r'\b', cleaned_text):
            found_skills.add(skill)

    return list(found_skills)
