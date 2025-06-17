import streamlit as st
import pandas as pd
import nltk

# Add the local NLTK data path
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True) # Download if not found

# Import your custom modules
from extract_resume import extract_text_from_pdf
from preprocess import preprocess_text
from skill_matcher import extract_skills, find_missing_skills
from similarity_model import calculate_similarity

# --- Streamlit App Configuration ---
st.set_page_config(page_title="Smart Resume Ranker Pro", layout="wide")

st.title("💡 Smart Resume Ranker Pro")
st.write("Upload a Job Description and multiple resumes to rank them.")

# --- Main Logic ---
st.header("1. Upload Your Files")
job_desc_file = st.file_uploader("Upload Job Description (TXT file)", type=["txt"])
resume_files = st.file_uploader("Upload Resumes (PDF files)", type=["pdf"], accept_multiple_files=True)

if st.button("Rank Resumes"):
    if job_desc_file is not None and resume_files:
        jd_text = job_desc_file.read().decode("utf-8")
        jd_skills = extract_skills(jd_text)
        preprocessed_jd = preprocess_text(jd_text)

        results = []
        progress_bar = st.progress(0)
        total_files = len(resume_files)

        for i, resume_file in enumerate(resume_files):
            # Pass the uploaded file object directly to the extractor
            resume_text = extract_text_from_pdf(resume_file)

            if not resume_text:
                st.warning(f"Could not read text from '{resume_file.name}'. Skipping.")
                progress_bar.progress((i + 1) / total_files)
                continue

            resume_skills = extract_skills(resume_text)
            preprocessed_resume = preprocess_text(resume_text)

            similarity_score = calculate_similarity(preprocessed_jd, preprocessed_resume)
            missing_skills = find_missing_skills(jd_skills, resume_skills)

            results.append({
                "Filename": resume_file.name,
                "Score (%)": f"{similarity_score:.2f}",
                "Matched Skills": ", ".join(resume_skills) if resume_skills else "None",
                "Missing Skills": ", ".join(missing_skills) if missing_skills else "None"
            })
            progress_bar.progress((i + 1) / total_files)

        st.header("2. Ranked Results")
        if results:
            df = pd.DataFrame(results)
            df['Score (%)'] = df['Score (%)'].astype(float)
            df = df.sort_values(by="Score (%)", ascending=False).reset_index(drop=True)
            st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Results as CSV",
                data=csv,
                file_name="ranked_results.csv",
                mime="text/csv",
            )
        else:
            st.warning("No resumes were processed successfully.")
    else:
        st.error("Please upload a job description and at least one resume.")