import streamlit as st
import pymupdf
import os
from pathlib import Path
from utils import (
    CandidateEvaluation,
    ResumeEvaluationResults,
    call_groq_api,
    load_text_file,
)

# Page configuration
st.set_page_config(
    page_title="ShortlistIQ — AI Resume Shortlisting",
    page_icon="📄",
    layout="wide",
)

st.title("📄 ShortlistIQ — AI Resume Shortlisting System")
st.caption("Automated semantic screening powered by Groq LLM inference")

# Sidebar for configuration & API key
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input(
        "Groq API Key",
        value=os.getenv("GROQ_API_KEY", ""),
        type="password",
        help="Enter your Groq Cloud API Key (or set it in Streamlit Secrets)",
    )
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key

    st.markdown("---")
    st.info("💡 Supports PDF resumes. Upload 1 or more candidate files to evaluate.")

# Two-column layout: Inputs
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Job Description")
    # Load default if available
    default_jd = ""
    if Path("job_description.md").exists():
        default_jd = load_text_file("job_description.md")
    job_description = st.text_area(
        "Paste Job Description here:",
        value=default_jd,
        height=300,
    )

with col2:
    st.subheader("2. Candidate Resumes (PDF)")
    uploaded_files = st.file_uploader(
        "Upload Resume PDFs",
        type=["pdf"],
        accept_multiple_files=True,
    )

# Run evaluation button
if st.button("🚀 Run AI Evaluation", type="primary", use_container_width=True):
    if not os.getenv("GROQ_API_KEY"):
        st.error("Please provide a valid GROQ_API_KEY in the sidebar or environment.")
        st.stop()

    if not job_description.strip():
        st.warning("Please provide a Job Description.")
        st.stop()

    if not uploaded_files:
        st.warning("Please upload at least one PDF resume.")
        st.stop()

    # Load guidance prompt
    guidance_prompt = load_text_file("guidance_prompt.md")

    # Extract text from uploaded in-memory PDF files
    with st.spinner("Extracting text from uploaded PDFs..."):
        resume_inputs = []
        for file in uploaded_files:
            doc = pymupdf.open(stream=file.read(), filetype="pdf")
            text = "".join([page.get_text() for page in doc]).strip()
            doc.close()
            resume_inputs.append({"filename": file.name, "text": text})

    # Call AI evaluation
    with st.spinner(f"Evaluating {len(resume_inputs)} resume(s) with Groq LLM..."):
        try:
            results, _ = call_groq_api(guidance_prompt, job_description, resume_inputs)
            st.success("✅ Evaluation Complete!")

            # Top recommendation banner
            st.markdown(f"### 🏆 Top Recommendation: **{results.top_recommendation}**")
            st.write(f"**Ready for Interview:** {', '.join(results.ready_for_interview)}")

            # Display Rankings Table
            st.markdown("### 📊 Ranked Candidates")
            ranking_data = [
                {
                    "Rank": i + 1,
                    "Name": c.name,
                    "Total Score (out of 50)": c.score,
                    "Recommendation": c.recommendation,
                    "Reason": c.ranking_reason,
                }
                for i, c in enumerate(results.final_ranking)
            ]
            st.dataframe(ranking_data, use_container_width=True)

            # Detailed scorecards
            st.markdown("### 📝 Detailed Candidate Breakdowns")
            for cand in results.candidates:
                with st.expander(f"👤 {cand.name} ({cand.filename}) — Score: {cand.total_score}/50"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**Scores & Reasoning:**")
                        st.write(f"- **Tech Skills ({cand.technical_skills.score}/10):** {cand.technical_skills.reasoning}")
                        st.write(f"- **Experience ({cand.experience.score}/10):** {cand.experience.reasoning}")
                        st.write(f"- **Domain Relevance ({cand.industry_relevance.score}/10):** {cand.industry_relevance.reasoning}")
                        st.write(f"- **Education ({cand.education.score}/10):** {cand.education.reasoning}")
                        st.write(f"- **Overall Fit ({cand.overall_fit.score}/10):** {cand.overall_fit.reasoning}")
                    with c2:
                        st.markdown("**Key Strengths:**")
                        for s in cand.key_strengths:
                            st.write(f"✅ {s}")
                        st.markdown("**Concerns / Red Flags:**")
                        for c in cand.concerns:
                            st.write(f"⚠️ {c}")

        except Exception as e:
            st.error(f"Error during evaluation: {e}")
