"""Streamlit UI for the AI Resume Analyzer."""

from __future__ import annotations

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
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* --------------------------------------------------------
       GLOBAL
    -------------------------------------------------------- */

    .stApp {
        background: #f7f9fc;
    }

    .main .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* Remove unnecessary top padding */
    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* --------------------------------------------------------
       HERO SECTION
    -------------------------------------------------------- */

    .hero {
        padding: 2.2rem 0 1.7rem 0;
    }

    .hero-badge {
        display: inline-block;
        background: #eef2ff;
        color: #4f46e5;
        border: 1px solid #e0e7ff;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 650;
        margin-bottom: 0.9rem;
    }

    .hero-title {
        font-size: 3rem;
        line-height: 1.05;
        font-weight: 800;
        letter-spacing: -0.04em;
        color: #111827;
        margin: 0;
    }

    .hero-title span {
        color: #4f46e5;
    }

    .hero-subtitle {
        max-width: 760px;
        font-size: 1.1rem;
        line-height: 1.7;
        color: #667085;
        margin-top: 0.9rem;
    }


    /* --------------------------------------------------------
       SECTION HEADER
    -------------------------------------------------------- */

    .section-heading {
        font-size: 1.35rem;
        font-weight: 750;
        color: #111827;
        margin-top: 2rem;
        margin-bottom: 0.3rem;
    }

    .section-description {
        color: #667085;
        font-size: 0.94rem;
        margin-bottom: 1rem;
    }


    /* --------------------------------------------------------
       INPUT CARDS
    -------------------------------------------------------- */

    .input-card {
        background: white;
        border: 1px solid #e4e7ec;
        border-radius: 18px;
        padding: 1.3rem;
        box-shadow: 0 4px 18px rgba(16, 24, 40, 0.04);
        margin-bottom: 1rem;
    }

    .input-card-title {
        font-size: 1rem;
        font-weight: 700;
        color: #1d2939;
        margin-bottom: 0.25rem;
    }

    .input-card-text {
        color: #667085;
        font-size: 0.88rem;
        margin-bottom: 0.8rem;
    }


    /* --------------------------------------------------------
       UPLOADER
    -------------------------------------------------------- */

    [data-testid="stFileUploader"] {
        background: #fafbff;
        border: 1px dashed #c7d2fe;
        border-radius: 14px;
        padding: 0.4rem;
    }

    [data-testid="stFileUploaderDropzone"] {
        border-radius: 12px;
    }


    /* --------------------------------------------------------
       TEXT AREA
    -------------------------------------------------------- */

    .stTextArea textarea {
        border-radius: 14px !important;
        border: 1px solid #d0d5dd !important;
        background: #ffffff !important;
        min-height: 260px !important;
    }

    .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
    }


    /* --------------------------------------------------------
       BUTTON
    -------------------------------------------------------- */

    .stButton > button {
        border-radius: 12px;
        min-height: 3rem;
        font-weight: 700;
        font-size: 1rem;
        border: none;
        box-shadow: 0 5px 14px rgba(79, 70, 229, 0.18);
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 18px rgba(79, 70, 229, 0.22);
    }


    /* --------------------------------------------------------
       SCORE CARDS
    -------------------------------------------------------- */

    .score-card {
        background: #ffffff;
        border: 1px solid #e4e7ec;
        border-radius: 18px;
        padding: 1.15rem;
        min-height: 145px;
        box-shadow: 0 4px 18px rgba(16, 24, 40, 0.04);
    }

    .score-label {
        color: #667085;
        font-size: 0.88rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .score-number {
        color: #111827;
        font-size: 2.25rem;
        line-height: 1;
        font-weight: 800;
        letter-spacing: -0.04em;
        margin-bottom: 0.55rem;
    }

    .score-number span {
        color: #98a2b3;
        font-size: 1rem;
        font-weight: 600;
    }


    /* --------------------------------------------------------
       RESULT SECTIONS
    -------------------------------------------------------- */

    .result-card {
        background: #ffffff;
        border: 1px solid #e4e7ec;
        border-radius: 18px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 18px rgba(16, 24, 40, 0.04);
    }

    .result-title {
        color: #111827;
        font-size: 1.05rem;
        font-weight: 750;
        margin-bottom: 0.2rem;
    }

    .result-description {
        color: #667085;
        font-size: 0.88rem;
        margin-bottom: 0.8rem;
    }


    /* --------------------------------------------------------
       BADGES
    -------------------------------------------------------- */

    .badge {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 999px;
        font-size: 0.76rem;
        font-weight: 700;
        border: 1px solid transparent;
    }

    .badge-high {
        background: #fef3f2;
        color: #b42318;
        border-color: #fecdca;
    }

    .badge-medium {
        background: #fffaeb;
        color: #b54708;
        border-color: #fedf89;
    }

    .badge-low {
        background: #ecfdf3;
        color: #027a48;
        border-color: #abefc6;
    }


    /* --------------------------------------------------------
       VERDICT
    -------------------------------------------------------- */

    .verdict-card {
        background: linear-gradient(
            135deg,
            #eef2ff,
            #ffffff
        );
        border: 1px solid #c7d2fe;
        border-radius: 20px;
        padding: 1.5rem;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    .verdict-label {
        color: #6366f1;
        font-size: 0.82rem;
        font-weight: 750;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .verdict-title {
        color: #111827;
        font-size: 2rem;
        font-weight: 800;
        margin: 0.35rem 0;
    }

    .verdict-summary {
        color: #475467;
        line-height: 1.7;
    }


    /* --------------------------------------------------------
       KEYWORDS
    -------------------------------------------------------- */

    .keyword-box {
        background: #f8fafc;
        border: 1px solid #e4e7ec;
        border-radius: 14px;
        padding: 1rem;
        min-height: 120px;
    }

    .keyword-title {
        font-size: 0.86rem;
        font-weight: 750;
        color: #344054;
        margin-bottom: 0.65rem;
    }

    .keyword {
        display: inline-block;
        background: #ffffff;
        border: 1px solid #d0d5dd;
        color: #344054;
        padding: 0.35rem 0.55rem;
        border-radius: 8px;
        margin: 0.15rem;
        font-size: 0.78rem;
    }


    /* --------------------------------------------------------
       FOOTER
    -------------------------------------------------------- */

    .footer {
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid #e4e7ec;
        text-align: center;
        color: #98a2b3;
        font-size: 0.82rem;
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
    """Display a professional score card."""

    st.markdown(
        f"""
        <div class="score-card">
            <div class="score-label">{label}</div>

            <div class="score-number">
                {score}<span>/100</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress(
        score / 100,
        text=explanation,
    )


def importance_badge(value: str) -> str:
    """Return HTML for a severity/priority badge."""

    value_lower = value.lower()

    css_class = {
        "high": "badge-high",
        "medium": "badge-medium",
        "low": "badge-low",
    }.get(value_lower, "badge-medium")

    return (
        f'<span class="badge {css_class}">'
        f"{value}"
        f"</span>"
    )


def display_keyword_list(
    keywords: list[str],
) -> None:
    """Display keywords as small pills."""

    if not keywords:
        st.caption("None identified.")
        return

    html = ""

    for keyword in keywords:
        html += (
            f'<span class="keyword">'
            f"{keyword}"
            f"</span>"
        )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


# ============================================================
# HEADER / HERO
# ============================================================

st.markdown(
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
            and practical ways to improve your chances.
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# INPUT AREA
# ============================================================

st.markdown(
    '<div class="section-heading">1. Upload Your Resume</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-description">'
    "Upload your current resume in PDF or DOCX format."
    "</div>",
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Upload Your Resume",
    type=["pdf", "docx"],
    label_visibility="collapsed",
    help="Supported formats: PDF and DOCX.",
)


resume_text = ""


if uploaded_file is not None:

    st.markdown(
        f"""
        <div class="input-card">
            <div class="input-card-title">
                📄 {uploaded_file.name}
            </div>

            <div class="input-card-text">
                Your resume has been selected.
                Extracting readable text for analysis...
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        resume_text = extract_resume_text(
            uploaded_file.getvalue(),
            uploaded_file.name,
        )

        st.success(
            f"Resume successfully extracted — "
            f"{len(resume_text.split())} words found."
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

st.markdown(
    '<div class="section-heading">2. Job Description</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-description">'
    "Paste the complete job description for the position you want to apply for."
    "</div>",
    unsafe_allow_html=True,
)

job_description = st.text_area(
    "Paste Job Description",
    height=280,
    placeholder=(
        "Example:\n\n"
        "We are looking for a Python Developer with experience in "
        "FastAPI, PostgreSQL, REST APIs, Git, and Docker..."
    ),
    label_visibility="collapsed",
)


# ============================================================
# ANALYZE BUTTON
# ============================================================

st.markdown(
    '<div class="section-heading">3. Analyze</div>',
    unsafe_allow_html=True,
)

analyze_clicked = st.button(
    "🚀 Analyze Resume",
    type="primary",
    use_container_width=True,
)


# ============================================================
# ANALYSIS
# ============================================================

if analyze_clicked:

    if uploaded_file is None:
        st.warning(
            "Please upload your resume first."
        )

    elif not resume_text.strip():
        st.warning(
            "The uploaded resume does not contain readable text."
        )

    elif not job_description.strip():
        st.warning(
            "Please paste the job description first."
        )

    else:

        with st.spinner(
            "AI is comparing your resume with the job description..."
        ):

            try:

                result = analyze_resume(
                    resume_text,
                    job_description,
                )

                st.session_state[
                    "analysis_result"
                ] = result

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

    result = st.session_state["analysis_result"]

    st.divider()

    st.markdown(
        """
        <div class="section-heading">
            Resume Analysis Results
        </div>

        <div class="section-description">
            Here is how your resume compares with the selected job.
        </div>
        """,
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # SCORE CARDS
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


    st.markdown("<br>", unsafe_allow_html=True)


    # --------------------------------------------------------
    # TABS
    # --------------------------------------------------------

    (
        skills_tab,
        experience_tab,
        problems_tab,
        recommendations_tab,
        ats_tab,
        final_tab,
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
    # SKILLS TAB
    # ========================================================

    with skills_tab:

        matching_col, missing_col = st.columns(2)

        with matching_col:

            st.markdown(
                """
                <div class="result-card">
                    <div class="result-title">
                        Matching Skills
                    </div>

                    <div class="result-description">
                        Skills in your resume that are relevant
                        to this job.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
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


        with missing_col:

            st.markdown(
                """
                <div class="result-card">
                    <div class="result-title">
                        Missing Skills
                    </div>

                    <div class="result-description">
                        Important job requirements that are not
                        clearly demonstrated in your resume.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if result.missing_skills:

                for item in result.missing_skills:

                    with st.expander(
                        item.skill,
                        expanded=False,
                    ):

                        st.markdown(
                            importance_badge(
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
    # EXPERIENCE TAB
    # ========================================================

    with experience_tab:

        st.markdown(
            """
            <div class="result-card">
                <div class="result-title">
                    Matching Experience
                </div>

                <div class="result-description">
                    Relevant experience from your resume
                    mapped to job requirements.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if result.matching_experience:

            for item in result.matching_experience:

                with st.expander(
                    item.experience,
                    expanded=True,
                ):

                    st.markdown(
                        f"**Job requirement:** "
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
    # PROBLEMS TAB
    # ========================================================

    with problems_tab:

        if result.problems:

            for item in result.problems:

                with st.expander(
                    item.problem,
                    expanded=False,
                ):

                    st.markdown(
                        importance_badge(
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
                "for this job."
            )


    # ========================================================
    # RECOMMENDATIONS TAB
    # ========================================================

    with recommendations_tab:

        if result.recommendations:

            for item in result.recommendations:

                with st.expander(
                    item.recommendation,
                    expanded=False,
                ):

                    st.markdown(
                        importance_badge(
                            item.priority
                        ),
                        unsafe_allow_html=True,
                    )

                    st.write(
                        item.explanation
                    )

                    st.markdown(
                        f"""
                        **Suggested action**

                        {item.action}
                        """
                    )

        else:

            st.info(
                "No recommendations were generated."
            )


    # ========================================================
    # ATS TAB
    # ========================================================

    with ats_tab:

        keyword_columns = st.columns(2)


        with keyword_columns[0]:

            st.markdown(
                """
                <div class="keyword-box">
                    <div class="keyword-title">
                        ✅ Matched Keywords
                    </div>
                """,
                unsafe_allow_html=True,
            )

            display_keyword_list(
                result.matched_keywords
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )


        with keyword_columns[1]:

            st.markdown(
                """
                <div class="keyword-box">
                    <div class="keyword-title">
                        ❌ Missing Keywords
                    </div>
                """,
                unsafe_allow_html=True,
            )

            display_keyword_list(
                result.missing_keywords
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )


    # ========================================================
    # FINAL TAB
    # ========================================================

    with final_tab:

        st.markdown(
            f"""
            <div class="verdict-card">

                <div class="verdict-label">
                    Final Recruiter Verdict
                </div>

                <div class="verdict-title">
                    {result.final_verdict}
                </div>

                <div class="verdict-summary">
                    {result.final_summary}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "### Overall Assessment"
        )

        st.write(
            result.overall_explanation
        )

        st.markdown(
            "### Score Breakdown"
        )

        breakdown = {
            "Overall Score": result.overall_score,
            "Job Match": result.job_match.score,
            "ATS Compatibility": result.ats_compatibility.score,
            "Resume Quality": result.resume_quality.score,
        }

        for label, score in breakdown.items():

            st.write(
                f"**{label}: {score}/100**"
            )

            st.progress(
                score / 100
            )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        AI Resume Analyzer · Powered by Groq · Built with Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)
