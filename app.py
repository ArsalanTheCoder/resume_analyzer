"""Modern Streamlit UI for the AI Resume Analyzer."""

from __future__ import annotations

import html
import textwrap

import streamlit as st

from analyzer import AnalysisError, analyze_resume
from resume_parser import ResumeParseError, extract_resume_text


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# HTML HELPER
# ============================================================

def render_html(content: str) -> None:
    """Render multiline HTML safely without indentation issues."""
    st.markdown(
        textwrap.dedent(content).strip(),
        unsafe_allow_html=True,
    )


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       GLOBAL
    ====================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at top left,
                rgba(99, 102, 241, 0.07),
                transparent 28%
            ),
            #f8fafc;
    }

    .main .block-container {
        max-width: 1250px;
        padding-top: 2.2rem;
        padding-bottom: 4rem;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    footer {
        visibility: hidden;
    }


    /* ======================================================
       HERO
    ====================================================== */

    .hero {
        text-align: center;
        padding: 2rem 0 3rem;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.45rem 0.9rem;
        border-radius: 999px;
        background: #eef2ff;
        border: 1px solid #e0e7ff;
        color: #4f46e5;
        font-size: 0.8rem;
        font-weight: 750;
        letter-spacing: 0.02em;
        margin-bottom: 1rem;
    }

    .hero-title {
        margin: 0;
        font-size: 3.5rem;
        line-height: 1.05;
        font-weight: 850;
        letter-spacing: -0.055em;
        color: #101828;
    }

    .hero-title span {
        color: #4f46e5;
    }

    .hero-subtitle {
        max-width: 760px;
        margin: 1rem auto 0;
        color: #667085;
        font-size: 1.05rem;
        line-height: 1.75;
    }


    /* ======================================================
       SECTION TITLES
    ====================================================== */

    .section-heading {
        margin-top: 1.8rem;
        color: #101828;
        font-size: 1.25rem;
        line-height: 1.3;
        font-weight: 800;
    }

    .section-description {
        margin-top: 0.35rem;
        margin-bottom: 1rem;
        color: #667085;
        font-size: 0.9rem;
        line-height: 1.6;
    }


    /* ======================================================
       UPLOAD CARD
    ====================================================== */

    .upload-card {
        background: #ffffff;
        border: 1px solid #e4e7ec;
        border-radius: 20px;
        padding: 1.4rem;
        box-shadow:
            0 12px 30px rgba(16, 24, 40, 0.05),
            0 2px 6px rgba(16, 24, 40, 0.03);
    }

    .upload-card-header {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin-bottom: 0.4rem;
    }

    .upload-icon {
        width: 42px;
        height: 42px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        background: #eef2ff;
        font-size: 1.2rem;
    }

    .upload-title {
        color: #1d2939;
        font-size: 1rem;
        font-weight: 750;
    }

    .upload-description {
        color: #667085;
        font-size: 0.85rem;
        line-height: 1.55;
        margin-left: 3.2rem;
    }


    /* ======================================================
       FILE UPLOADER
    ====================================================== */

    [data-testid="stFileUploader"] {
        margin-top: 1rem;
    }

    [data-testid="stFileUploaderDropzone"] {
        border: 1px dashed #a5b4fc !important;
        border-radius: 16px !important;
        background: #fafaff !important;
    }


    /* ======================================================
       RESUME STATUS
    ====================================================== */

    .file-status {
        margin-top: 1rem;
        padding: 0.85rem 1rem;
        border-radius: 12px;
        background: #f8fafc;
        border: 1px solid #e4e7ec;
        color: #344054;
        font-size: 0.88rem;
    }


    /* ======================================================
       TEXT AREA
    ====================================================== */

    .stTextArea textarea {
        border-radius: 16px !important;
        border: 1px solid #d0d5dd !important;
        background: #ffffff !important;
        color: #101828 !important;
        padding: 1rem !important;
        line-height: 1.6 !important;
    }

    .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow:
            0 0 0 3px rgba(99, 102, 241, 0.10) !important;
    }


    /* ======================================================
       ANALYZE BUTTON
    ====================================================== */

    .stButton > button {
        width: 100%;
        min-height: 3.15rem;
        border-radius: 14px;
        font-size: 1rem;
        font-weight: 750;
        border: none;
        transition:
            transform 0.15s ease,
            box-shadow 0.15s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow:
            0 10px 24px rgba(79, 70, 229, 0.18);
    }


    /* ======================================================
       SCORE CARDS
    ====================================================== */

    .score-card {
        height: 100%;
        background: #ffffff;
        border: 1px solid #e4e7ec;
        border-radius: 18px;
        padding: 1.25rem;
        box-shadow:
            0 10px 25px rgba(16, 24, 40, 0.04),
            0 2px 6px rgba(16, 24, 40, 0.02);
    }

    .score-label {
        color: #667085;
        font-size: 0.82rem;
        font-weight: 650;
        margin-bottom: 0.6rem;
    }

    .score-value {
        color: #101828;
        font-size: 2.35rem;
        line-height: 1;
        font-weight: 850;
        letter-spacing: -0.05em;
        margin-bottom: 0.7rem;
    }

    .score-value span {
        color: #98a2b3;
        font-size: 0.95rem;
        font-weight: 650;
        letter-spacing: 0;
    }


    /* ======================================================
       RESULT CARDS
    ====================================================== */

    .result-card {
        background: #ffffff;
        border: 1px solid #e4e7ec;
        border-radius: 18px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow:
            0 8px 24px rgba(16, 24, 40, 0.035);
    }

    .result-card-title {
        color: #101828;
        font-size: 1rem;
        font-weight: 800;
        margin-bottom: 0.25rem;
    }

    .result-card-description {
        color: #667085;
        font-size: 0.84rem;
        line-height: 1.55;
    }


    /* ======================================================
       BADGES
    ====================================================== */

    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.28rem 0.65rem;
        border-radius: 999px;
        font-size: 0.74rem;
        font-weight: 750;
        border: 1px solid transparent;
    }

    .badge-high {
        color: #b42318;
        background: #fef3f2;
        border-color: #fecdca;
    }

    .badge-medium {
        color: #b54708;
        background: #fffaeb;
        border-color: #fedf89;
    }

    .badge-low {
        color: #027a48;
        background: #ecfdf3;
        border-color: #abefc6;
    }


    /* ======================================================
       KEYWORDS
    ====================================================== */

    .keyword-container {
        background: #ffffff;
        border: 1px solid #e4e7ec;
        border-radius: 18px;
        padding: 1.2rem;
        min-height: 150px;
        box-shadow:
            0 8px 24px rgba(16, 24, 40, 0.035);
    }

    .keyword-title {
        color: #344054;
        font-size: 0.86rem;
        font-weight: 800;
        margin-bottom: 0.7rem;
    }

    .keyword {
        display: inline-block;
        margin: 0.15rem 0.12rem;
        padding: 0.38rem 0.6rem;
        border-radius: 8px;
        background: #f8fafc;
        border: 1px solid #e4e7ec;
        color: #344054;
        font-size: 0.76rem;
        font-weight: 550;
    }


    /* ======================================================
       VERDICT
    ====================================================== */

    .verdict-card {
        margin-top: 0.5rem;
        margin-bottom: 1rem;
        padding: 1.7rem;
        border-radius: 22px;
        border: 1px solid #c7d2fe;
        background:
            linear-gradient(
                135deg,
                #eef2ff 0%,
                #ffffff 100%
            );
        box-shadow:
            0 12px 30px rgba(79, 70, 229, 0.08);
    }

    .verdict-label {
        color: #6366f1;
        font-size: 0.76rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    .verdict-title {
        margin: 0.4rem 0 0.7rem;
        color: #101828;
        font-size: 2.1rem;
        line-height: 1.15;
        font-weight: 850;
        letter-spacing: -0.04em;
    }

    .verdict-summary {
        color: #475467;
        font-size: 0.95rem;
        line-height: 1.7;
        max-width: 850px;
    }


    /* ======================================================
       FOOTER
    ====================================================== */

    .custom-footer {
        margin-top: 3rem;
        padding-top: 1.3rem;
        border-top: 1px solid #e4e7ec;
        text-align: center;
        color: #98a2b3;
        font-size: 0.78rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def show_score_card(
    label: str,
    score: int,
    explanation: str,
) -> None:
    """Display a score card with progress."""

    render_html(
        f"""
        <div class="score-card">
            <div class="score-label">
                {html.escape(label)}
            </div>

            <div class="score-value">
                {score}<span>/100</span>
            </div>
        </div>
        """
    )

    st.progress(
        score / 100,
        text=explanation,
    )


def get_badge_html(value: str) -> str:
    """Create a badge based on High/Medium/Low."""

    safe_value = html.escape(value)
    normalized = value.lower()

    badge_class = {
        "high": "badge-high",
        "medium": "badge-medium",
        "low": "badge-low",
    }.get(
        normalized,
        "badge-medium",
    )

    return (
        f'<span class="badge {badge_class}">'
        f"{safe_value}"
        f"</span>"
    )


def display_keywords(
    keywords: list[str],
) -> None:
    """Display keywords as pills."""

    if not keywords:
        st.caption("No keywords identified.")
        return

    keyword_html = ""

    for keyword in keywords:
        keyword_html += (
            f'<span class="keyword">'
            f"{html.escape(keyword)}"
            f"</span>"
        )

    st.markdown(
        keyword_html,
        unsafe_allow_html=True,
    )


# ============================================================
# HERO
# ============================================================

render_html(
    """
    <div class="hero">

        <div class="hero-badge">
            ✦ AI-Powered Resume Analysis
        </div>

        <h1 class="hero-title">
            AI Resume <span>Analyzer</span>
        </h1>

        <p class="hero-subtitle">
            Compare your resume against a specific job description
            and discover your strengths, skill gaps, ATS keywords,
            resume problems, and practical recommendations.
        </p>

    </div>
    """
)


# ============================================================
# RESUME UPLOAD
# ============================================================

render_html(
    """
    <div class="section-heading">
        1. Upload Your Resume
    </div>

    <div class="section-description">
        Upload your current resume in PDF or DOCX format.
    </div>

    <div class="upload-card">

        <div class="upload-card-header">

            <div class="upload-icon">
                📄
            </div>

            <div class="upload-title">
                Resume Document
            </div>

        </div>

        <div class="upload-description">
            Your resume is processed locally for text extraction
            before being analyzed against the job description.
        </div>

    </div>
    """
)


uploaded_file = st.file_uploader(
    "Upload Resume",
    type=["pdf", "docx"],
    label_visibility="collapsed",
    help="Supported formats: PDF and DOCX.",
)


resume_text = ""


if uploaded_file is not None:

    try:

        resume_text = extract_resume_text(
            uploaded_file.getvalue(),
            uploaded_file.name,
        )

        render_html(
            f"""
            <div class="file-status">
                ✅ <strong>{html.escape(uploaded_file.name)}</strong>
                &nbsp;·&nbsp;
                {len(resume_text.split())} words extracted successfully
            </div>
            """
        )

        with st.expander(
            "Preview extracted resume text"
        ):

            preview = resume_text[:5000]

            st.text(
                preview
                + (
                    "..."
                    if len(resume_text) > 5000
                    else ""
                )
            )

    except ResumeParseError as exc:

        st.error(str(exc))


# ============================================================
# JOB DESCRIPTION
# ============================================================

render_html(
    """
    <div class="section-heading">
        2. Job Description
    </div>

    <div class="section-description">
        Paste the complete job description for the position
        you want to apply for.
    </div>
    """
)


job_description = st.text_area(
    "Job Description",
    height=300,
    label_visibility="collapsed",
    placeholder=(
        "Paste the complete job description here...\n\n"
        "Example:\n"
        "We are looking for a Python Developer with experience "
        "in FastAPI, PostgreSQL, REST APIs, Git, and Docker..."
    ),
)


# ============================================================
# ANALYZE
# ============================================================

render_html(
    """
    <div class="section-heading">
        3. Analyze Your Resume
    </div>

    <div class="section-description">
        Groq will compare the extracted resume against the
        specific job description and generate an evidence-based report.
    </div>
    """
)


analyze_clicked = st.button(
    "🚀 Analyze Resume",
    type="primary",
    use_container_width=True,
)


# ============================================================
# RUN ANALYSIS
# ============================================================

if analyze_clicked:

    if uploaded_file is None:

        st.warning(
            "Please upload your resume first."
        )

    elif not resume_text.strip():

        st.warning(
            "Your resume could not be read. "
            "Please upload a readable PDF or DOCX file."
        )

    elif not job_description.strip():

        st.warning(
            "Please paste the job description first."
        )

    else:

        with st.spinner(
            "Analyzing your resume with AI..."
        ):

            try:

                analysis_result = analyze_resume(
                    resume_text,
                    job_description,
                )

                st.session_state[
                    "analysis_result"
                ] = analysis_result

                st.success(
                    "Analysis completed successfully!"
                )

            except AnalysisError as exc:

                st.error(str(exc))

            except Exception:

                st.error(
                    "Something unexpected happened while analyzing "
                    "your resume. Please try again."
                )


# ============================================================
# RESULTS
# ============================================================

if "analysis_result" in st.session_state:

    result = st.session_state[
        "analysis_result"
    ]

    st.divider()


    # --------------------------------------------------------
    # RESULTS HEADER
    # --------------------------------------------------------

    render_html(
        """
        <div class="section-heading">
            Resume Analysis Results
        </div>

        <div class="section-description">
            A recruiter-style analysis based specifically on
            your resume and the supplied job description.
        </div>
        """
    )


    # --------------------------------------------------------
    # SCORE DASHBOARD
    # --------------------------------------------------------

    score_columns = st.columns(4)

    with score_columns[0]:

        show_score_card(
            "Overall Score",
            result.overall_score,
            result.overall_explanation,
        )

    with score_columns[1]:

        show_score_card(
            "Job Match",
            result.job_match.score,
            result.job_match.explanation,
        )

    with score_columns[2]:

        show_score_card(
            "ATS Compatibility",
            result.ats_compatibility.score,
            result.ats_compatibility.explanation,
        )

    with score_columns[3]:

        show_score_card(
            "Resume Quality",
            result.resume_quality.score,
            result.resume_quality.explanation,
        )


    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # RESULT TABS
    # --------------------------------------------------------

    (
        skills_tab,
        experience_tab,
        problems_tab,
        recommendations_tab,
        ats_tab,
        verdict_tab,
    ) = st.tabs(
        [
            "💡 Skills",
            "💼 Experience",
            "⚠️ Problems",
            "🎯 Recommendations",
            "🔎 ATS Keywords",
            "🏆 Final Verdict",
        ]
    )


    # ========================================================
    # SKILLS
    # ========================================================

    with skills_tab:

        matching_column, missing_column = st.columns(2)

        with matching_column:

            render_html(
                """
                <div class="result-card">

                    <div class="result-card-title">
                        ✅ Matching Skills
                    </div>

                    <div class="result-card-description">
                        Skills present in your resume that
                        are relevant to this job.
                    </div>

                </div>
                """
            )

            if result.matching_skills:

                for item in result.matching_skills:

                    with st.expander(
                        item.skill,
                        expanded=False,
                    ):

                        st.write(
                            item.explanation
                        )

            else:

                st.info(
                    "No clearly matching skills were identified."
                )


        with missing_column:

            render_html(
                """
                <div class="result-card">

                    <div class="result-card-title">
                        ❌ Missing Skills
                    </div>

                    <div class="result-card-description">
                        Important job requirements that are
                        not clearly demonstrated in your resume.
                    </div>

                </div>
                """
            )

            if result.missing_skills:

                for item in result.missing_skills:

                    with st.expander(
                        item.skill,
                        expanded=False,
                    ):

                        st.markdown(
                            get_badge_html(
                                item.importance
                            ),
                            unsafe_allow_html=True,
                        )

                        st.write(
                            item.explanation
                        )

            else:

                st.success(
                    "No important missing skills were identified."
                )


    # ========================================================
    # EXPERIENCE
    # ========================================================

    with experience_tab:

        render_html(
            """
            <div class="result-card">

                <div class="result-card-title">
                    💼 Matching Experience
                </div>

                <div class="result-card-description">
                    Relevant experience from your resume
                    mapped to actual job requirements.
                </div>

            </div>
            """
        )

        if result.matching_experience:

            for item in result.matching_experience:

                with st.expander(
                    item.experience,
                    expanded=True,
                ):

                    st.markdown(
                        f"**Related job requirement:** "
                        f"{item.job_requirement}"
                    )

                    st.write(
                        item.explanation
                    )

        else:

            st.info(
                "No clearly matching experience was identified."
            )


    # ========================================================
    # PROBLEMS
    # ========================================================

    with problems_tab:

        render_html(
            """
            <div class="result-card">

                <div class="result-card-title">
                    ⚠️ Resume Problems
                </div>

                <div class="result-card-description">
                    Weaknesses that may reduce your match
                    for this specific position.
                </div>

            </div>
            """
        )

        if result.problems:

            for item in result.problems:

                with st.expander(
                    item.problem,
                    expanded=False,
                ):

                    st.markdown(
                        get_badge_html(
                            item.severity
                        ),
                        unsafe_allow_html=True,
                    )

                    st.write(
                        item.explanation
                    )

        else:

            st.success(
                "No major resume problems were identified "
                "for this position."
            )


    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    with recommendations_tab:

        render_html(
            """
            <div class="result-card">

                <div class="result-card-title">
                    🎯 Recommendations
                </div>

                <div class="result-card-description">
                    Practical improvements you can make
                    without exaggerating your qualifications.
                </div>

            </div>
            """
        )

        if result.recommendations:

            for item in result.recommendations:

                with st.expander(
                    item.recommendation,
                    expanded=False,
                ):

                    st.markdown(
                        get_badge_html(
                            item.priority
                        ),
                        unsafe_allow_html=True,
                    )

                    st.write(
                        item.explanation
                    )

                    st.markdown(
                        f"""
                        **Suggested Action**

                        {item.action}
                        """
                    )

        else:

            st.info(
                "No recommendations were generated."
            )


    # ========================================================
    # ATS KEYWORDS
    # ========================================================

    with ats_tab:

        keyword_columns = st.columns(2)

        with keyword_columns[0]:

            render_html(
                """
                <div class="keyword-container">

                    <div class="keyword-title">
                        ✅ Matched Keywords
                    </div>

                """
            )

            display_keywords(
                result.matched_keywords
            )

            render_html(
                """
                </div>
                """
            )


        with keyword_columns[1]:

            render_html(
                """
                <div class="keyword-container">

                    <div class="keyword-title">
                        ❌ Missing Keywords
                    </div>

                """
            )

            display_keywords(
                result.missing_keywords
            )

            render_html(
                """
                </div>
                """
            )


    # ========================================================
    # FINAL VERDICT
    # ========================================================

    with verdict_tab:

        render_html(
            f"""
            <div class="verdict-card">

                <div class="verdict-label">
                    Final Recruiter Verdict
                </div>

                <div class="verdict-title">
                    {html.escape(result.final_verdict)}
                </div>

                <div class="verdict-summary">
                    {html.escape(result.final_summary)}
                </div>

            </div>
            """
        )


        render_html(
            """
            <div class="result-card">

                <div class="result-card-title">
                    Overall Assessment
                </div>

            </div>
            """
        )

        st.write(
            result.overall_explanation
        )


        render_html(
            """
            <div class="result-card">

                <div class="result-card-title">
                    Score Breakdown
                </div>

            </div>
            """
        )

        breakdown = [
            (
                "Overall Score",
                result.overall_score,
            ),
            (
                "Job Match",
                result.job_match.score,
            ),
            (
                "ATS Compatibility",
                result.ats_compatibility.score,
            ),
            (
                "Resume Quality",
                result.resume_quality.score,
            ),
        ]

        for label, score in breakdown:

            st.markdown(
                f"**{label} — {score}/100**"
            )

            st.progress(
                score / 100
            )


# ============================================================
# FOOTER
# ============================================================

render_html(
    """
    <div class="custom-footer">
        AI Resume Analyzer · Powered by Groq · Built with Streamlit
    </div>
    """
)
