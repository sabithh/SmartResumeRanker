import streamlit as st
import pandas as pd
import nltk
from fpdf import FPDF

# --- Dependency Download ---
# Ensure the necessary NLTK data packages are available.
# This is a robust way to handle it directly within the app.
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    st.info("First-time setup: Downloading necessary NLTK data...")
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    st.success("Setup complete!")

# --- Custom Module Imports ---
# Import the functions from your other project files.
from extract_resume import extract_text_from_pdf
from preprocess import preprocess_text
from skill_matcher import extract_skills, REQUIRED_SKILLS, PREFERRED_SKILLS
from similarity_model import calculate_similarity


# --- PDF Report Generation Function ---
def generate_pdf_report(sorted_results):
    """Creates a PDF report from the ranked list of candidates."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)

    pdf.cell(0, 10, 'Smart Resume Ranker - Top Candidates Report', 0, 1, 'C')
    pdf.ln(10)

    for rank, result in enumerate(sorted_results, 1):
        pdf.set_font("Arial", 'B', 12)
        # Add a clickable link to the resume file (works best when files are organized)
        # Note: Direct local file links might be blocked by browser security.
        pdf.cell(0, 10, f"Rank {rank}: {result['Filename']} - Score: {result['Score (%)']}%", 0, 1)

        pdf.set_font("Arial", '', 10)
        # Use a consistent encoding and handle potential errors
        details = f"Details: {result['Explain Score']}\nMatched: {result['Matched Skills']}\nMissing: {result['Missing Skills']}"
        pdf.multi_cell(0, 5, details.encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(5)

    # Return the PDF content as a byte string for downloading
    # The .output() method can return a bytearray, which we convert to bytes.
    return bytes(pdf.output(dest='S'))


# --- Streamlit App UI ---
st.set_page_config(page_title="Smart Resume Ranker Pro", layout="wide")
st.title("💡 Smart Resume Ranker Pro")
st.write("Upload a Job Description and resumes to get an AI-powered ranking with skill analysis.")

# --- Main Logic ---
st.header("1. Upload Your Files")
job_desc_file = st.file_uploader("Upload Job Description (TXT file)", type=["txt"])
resume_files = st.file_uploader("Upload Resumes (PDF files)", type=["pdf"], accept_multiple_files=True)

if st.button("Rank Resumes"):
    if job_desc_file is not None and resume_files:
        with st.spinner("Analyzing... This may take a moment."):
            jd_text = job_desc_file.read().decode("utf-8")
            preprocessed_jd = preprocess_text(jd_text)

            results = []

            for resume_file in resume_files:
                # This now assumes you are using the pdfplumber version of the extractor
                resume_text = extract_text_from_pdf(resume_file)

                if not resume_text:
                    st.warning(f"Could not read text from '{resume_file.name}'. Skipping.")
                    continue

                # --- Scoring Logic ---
                # 1. Extract skills
                matched_required = extract_skills(resume_text, REQUIRED_SKILLS)
                matched_preferred = extract_skills(resume_text, PREFERRED_SKILLS)
                all_matched_skills = set(matched_required + matched_preferred)

                # 2. Calculate skill-based score
                skill_score = (len(matched_required) / len(REQUIRED_SKILLS)) * 100 if REQUIRED_SKILLS else 100

                # 3. Calculate semantic similarity score
                preprocessed_resume = preprocess_text(resume_text)
                semantic_score = calculate_similarity(preprocessed_jd, preprocessed_resume)

                # 4. Calculate final weighted score
                # Weighted at 60% for semantic context and 40% for required skills match
                final_score = (0.6 * semantic_score) + (0.4 * skill_score)

                # --- Reporting Details ---
                explain_score = f"{len(matched_required)} of {len(REQUIRED_SKILLS)} required skills found."
                all_jd_skills = set(REQUIRED_SKILLS + PREFERRED_SKILLS)
                missing_skills = list(all_jd_skills - all_matched_skills)

                results.append({
                    "Filename": resume_file.name,
                    "Score (%)": f"{final_score:.2f}",
                    "Explain Score": explain_score,
                    "Matched Skills": ", ".join(sorted(all_matched_skills)) if all_matched_skills else "None",
                    "Missing Skills": ", ".join(sorted(missing_skills)) if missing_skills else "None"
                })

        st.header("2. Ranked Results")
        if results:
            sorted_results = sorted(results, key=lambda x: float(x["Score (%)"]), reverse=True)

            # --- Display Detailed Results with Color Highlights ---
            for rank, result in enumerate(sorted_results, 1):
                st.subheader(f"Rank {rank}: {result['Filename']} - Score: {result['Score (%)']}%")

                with st.expander("View Skill Analysis"):
                    st.info(f"**Score Explanation:** {result['Explain Score']}")

                    # Format matched skills with green color
                    matched_skills_str = result['Matched Skills']
                    if matched_skills_str != "None":
                        html_matched = "".join([
                                                   f"<span style='background-color: #28a745; color: white; padding: 3px 8px; margin: 3px; border-radius: 5px; display: inline-block;'>{s.strip()}</span>"
                                                   for s in matched_skills_str.split(',')])
                        st.markdown(f"**Matched Skills:** {html_matched}", unsafe_allow_html=True)
                    else:
                        st.markdown("**Matched Skills:** None")

                    # Format missing skills with red color
                    missing_skills_str = result['Missing Skills']
                    if missing_skills_str != "None":
                        html_missing = "".join([
                                                   f"<span style='background-color: #dc3545; color: white; padding: 3px 8px; margin: 3px; border-radius: 5px; display: inline-block;'>{s.strip()}</span>"
                                                   for s in missing_skills_str.split(',')])
                        st.markdown(f"**Missing Skills:** {html_missing}", unsafe_allow_html=True)
                    else:
                        st.markdown("**Missing Skills:** None")

            # --- Download Buttons ---
            st.header("3. Download Reports")
            col1, col2 = st.columns(2)

            with col1:
                # Prepare CSV for download
                df_results = pd.DataFrame(sorted_results)
                csv = df_results.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Full Results as CSV",
                    data=csv,
                    file_name="ranked_results.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            with col2:
                # Prepare PDF for download
                pdf_bytes = generate_pdf_report(sorted_results)
                st.download_button(
                    label="Download Report as PDF",
                    data=pdf_bytes,
                    file_name="ranked_report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        else:
            st.warning("No resumes were processed successfully. Please ensure the PDFs are valid and readable.")
    else:
        st.error("Please upload a job description and at least one resume.")
