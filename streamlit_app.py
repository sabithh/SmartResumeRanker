import streamlit as st
import pandas as pd
import os
import nltk

# Add the local NLTK data path from our previous fix
nltk.data.path.append('./nltk_data/')

# Import your custom modules
from extract_resume import extract_text_from_pdf
from preprocess import preprocess_text
from skill_matcher import extract_skills, find_missing_skills
from similarity_model import calculate_similarity

# --- Streamlit App Configuration ---
st.set_page_config(page_title="Smart Resume Ranker Pro", layout="wide")

st.title("💡 Smart Resume Ranker Pro")
st.write("Upload a Job Description and multiple resumes to see the magic!")

# --- Main Logic ---

# 1. Input Section
st.header("1. Upload Your Files")
job_desc_file = st.file_uploader("Upload Job Description (TXT file)", type=["txt"])
resume_files = st.file_uploader("Upload Resumes (PDF files)", type=["pdf"], accept_multiple_files=True)

# 2. Processing and Ranking Button
if st.button("Rank Resumes"):
    if job_desc_file is not None and resume_files:
        # Read and preprocess Job Description
        jd_text = job_desc_file.read().decode("utf-8")
        jd_skills = extract_skills(jd_text)
        preprocessed_jd = preprocess_text(jd_text)

        results = []

        progress_bar = st.progress(0)
        total_files = len(resume_files)

        for i, resume_file in enumerate(resume_files):
            # Save the uploaded file temporarily to read with PyMuPDF
            with open(resume_file.name, "wb") as f:
                f.write(resume_file.getbuffer())

            # Extract and preprocess resume text
            resume_text = extract_text_from_pdf(resume_file.name)

            # --- THIS IS THE NEW DEBUGGING LINE ---
            st.info(f"Processing '{resume_file.name}': Content starts with '{resume_text[:100].strip()}'...")
            # -----------------------------------------

            resume_skills = extract_skills(resume_text)
            preprocessed_resume = preprocess_text(resume_text)

            # Calculate similarity score
            similarity_score = calculate_similarity(preprocessed_jd, preprocessed_resume)

            # Find missing skills
            missing_skills = find_missing_skills(jd_skills, resume_skills)

            results.append({
                "Filename": resume_file.name,
                "Score (%)": f"{similarity_score:.2f}",
                "Matched Skills": ", ".join(resume_skills) if resume_skills else "None",
                "Missing Skills": ", ".join(missing_skills) if missing_skills else "None"
            })

            os.remove(resume_file.name)
            progress_bar.progress((i + 1) / total_files)

        st.header("2. Ranked Results")

        if results:
            df = pd.DataFrame(results)
            df['Score (%)'] = df['Score (%)'].astype(float)
            df = df.sort_values(by="Score (%)", ascending=False).reset_index(drop=True)

            st.dataframe(df, use_container_width=True)

            @st.cache_data
            def convert_df_to_csv(df):
                return df.to_csv(index=False).encode('utf-8')

            csv = convert_df_to_csv(df)
            st.download_button(
                label="Download Results as CSV",
                data=csv,
                file_name="ranked_results.csv",
                mime="text/csv",
            )
        else:
            st.warning("No results to display.")
    else:
        st.error("Please upload a job description and at least one resume.")