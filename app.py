"""Streamlit UI for the AI Resume Analyzer."""

from __future__ import annotations

import streamlit as st

from analyzer import AnalysisError, analyze_resume
from resume_parser import ResumeParseError, extract_resume_text


st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.6rem;
            font-weight: 750;
            margin-bottom: 0.2rem;
        }
        .subtitle {
            color: #6b7280;
            font-size: 1.05rem;
            margin-bottom: 1.6rem;
        }
        .score-card {
            border: 1px solid #e5e7eb;
            border-radius: 16px;
            padding: 1rem 1.1rem 0.9rem;
            background: #ffffff;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
        }
        .score-label {
            color: #6b7280;
            font-size: 0.9rem;
            margin-bottom: 0.25rem;
        }
        .score-value {
            font-size: 2rem;
            font-weight: 750;
            margin: 0;
        }
        .pill {
            display: inline-block;
            padding: 0.25rem 0.6rem;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 650;
            border: 1px solid #d1d5db;
            margin-right: 0.4rem;
        }
        .section-title {
            margin-top: 1.6rem;
            margin-bottom: 0.4rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def show_score_card(label: str, score: int, explanation: str) -> None:
    """Render one score card with a progress bar and explanation."""
    st.markdown(
        f"""
        <div class="score-card">
            <div class="score-label">{label}</div>
            <p class="score-value">{score}/100</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(score / 100)
    st.caption(explanation)


def show_priority_pill(value: str) -> None:
    """Render a lightweight text badge."""
    st.markdown(f'<span class="pill">{value}</span>', unsafe_allow_html=True)


def render_results(result) -> None:
    """Render the complete analysis dashboard."""
    st.markdown("## Resume Analysis Results")

    scores = result.model_dump()

    columns = st.columns(4)
    with columns[0]:
        show_score_card(
            "Overall Score",
            scores["overall_score"],
            result.overall_explanation,
        )
    with columns[1]:
        show_score_card(
            "Job Match",
            result.job_match.score,
            result.job_match.explanation,
        )
    with columns[2]:
        show_score_card(
            "ATS Compatibility",
            result.ats_compatibility.score,
            result.ats_compatibility.explanation,
        )
    with columns[3]:
        show_score_card(
            "Resume Quality",
            result.resume_quality.score,
            result.resume_quality.explanation,
        )

    st.markdown('<div class="section-title"></div>', unsafe_allow_html=True)

    st.subheader("1. Matching Skills")
    if result.matching_skills:
        for item in result.matching_skills:
            with st.expander(item.skill, expanded=True):
                st.write(item.explanation)
    else:
        st.info("No clearly matching skills were identified.")

    st.subheader("2. Missing Skills")
    if result.missing_skills:
        for item in result.missing_skills:
            with st.expander(f"{item.skill} — {item.importance}", expanded=False):
                show_priority_pill(item.importance)
                st.write(item.explanation)
    else:
        st.success("No important missing skills were identified.")

    st.subheader("3. Matching Experience")
    if result.matching_experience:
        for item in result.matching_experience:
            with st.expander(item.experience, expanded=True):
                st.markdown(f"**Related job requirement:** {item.job_requirement}")
                st.write(item.explanation)
    else:
        st.info("No clearly matching experience was identified.")

    st.subheader("4. Resume Problems")
    if result.problems:
        for item in result.problems:
            with st.expander(f"{item.problem} — {item.severity}", expanded=False):
                show_priority_pill(item.severity)
                st.write(item.explanation)
    else:
        st.success("No major resume problems were identified for this job.")

    st.subheader("5. Recommendations")
    if result.recommendations:
        for item in result.recommendations:
            with st.expander(f"{item.recommendation} — {item.priority}", expanded=False):
                show_priority_pill(item.priority)
                st.write(item.explanation)
                st.markdown(f"**Suggested action:** {item.action}")
    else:
        st.info("No recommendations were generated.")

    st.subheader("6. ATS Keywords")
    left, right = st.columns(2)
    with left:
        st.markdown("**Matched Keywords**")
        if result.matched_keywords:
            st.write(", ".join(result.matched_keywords))
        else:
            st.info("None identified.")
    with right:
        st.markdown("**Missing Keywords**")
        if result.missing_keywords:
            st.write(", ".join(result.missing_keywords))
        else:
            st.info("None identified.")

    st.subheader("7. Final Verdict")
    st.success(result.final_verdict)

    st.subheader("8. Final Summary")
    st.write(result.final_summary)


st.markdown('<div class="main-title">AI Resume Analyzer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Analyze your resume against a specific job description using AI.</div>',
    unsafe_allow_html=True,
)

st.header("1. Upload Your Resume")
uploaded_file = st.file_uploader(
    "Upload Your Resume",
    type=["pdf", "docx"],
    help="Accepted formats: PDF and DOCX.",
)

resume_text = ""
if uploaded_file is not None:
    st.caption(f"Selected file: **{uploaded_file.name}**")
    try:
        resume_text = extract_resume_text(uploaded_file.getvalue(), uploaded_file.name)
        st.success("Resume text extracted successfully.")
        with st.expander("Preview extracted resume text"):
            preview = resume_text[:5000]
            st.text(preview + ("..." if len(resume_text) > 5000 else ""))
    except ResumeParseError as exc:
        st.error(str(exc))

st.header("2. Paste Job Description")
job_description = st.text_area(
    "Paste Job Description",
    height=300,
    placeholder="Paste the complete job description here...",
)

st.header("3. Analyze")
analyze_clicked = st.button("Analyze Resume", type="primary", use_container_width=True)

if analyze_clicked:
    if uploaded_file is None:
        st.warning("Please upload a PDF or DOCX resume first.")
    elif not resume_text.strip():
        st.warning("The resume text could not be extracted. Please upload a readable file.")
    elif not job_description.strip():
        st.warning("Please paste the job description before analyzing.")
    else:
        with st.spinner("Grok is analyzing your resume against the job description..."):
            try:
                result = analyze_resume(resume_text, job_description)
            except AnalysisError as exc:
                st.error(str(exc))
            except Exception:
                st.error("Something unexpected happened while analyzing the resume. Please try again.")
            else:
                st.session_state["analysis_result"] = result

if "analysis_result" in st.session_state:
    st.divider()
    render_results(st.session_state["analysis_result"])
