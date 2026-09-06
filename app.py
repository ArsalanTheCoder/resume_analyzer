"""Modern Streamlit UI for the AI Resume Analyzer."""

from __future__ import annotations

import html

import streamlit as st

from analyzer import AnalysisError, analyze_resume
from resume_parser import ResumeParseError, extract_resume_text


# ============================================================
# PAGE CONFIG
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

st.html(
    """
    <style>

    /* ========================================================
       GLOBAL
    ======================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 0% 0%,
                rgba(99, 102, 241, 0.07),
                transparent 25%
            ),
            radial-gradient(
                circle at 100% 0%,
                rgba(14, 165, 233, 0.05),
                transparent 25%
            ),
            #f8fafc;
    }

    .main .block-container {
        max-width: 1220px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* Hide default Streamlit footer */
    footer {
        visibility: hidden;
    }


    /* ========================================================
       HERO
    ======================================================== */

    .hero {
        text-align: center;
        padding: 2rem 0 3rem 0;
    }

    .hero-badge {
        display: inline-block;
        padding: 0.45rem 0.9rem;
        border-radius: 999px;
        background: #eef2ff;
        border: 1px solid #c7d2fe;
        color: #4f46e5;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        margin-bottom: 1rem;
    }

    .hero-title {
        margin: 0;
        color: #101828;
        font-size: 3.5rem;
        line-height: 1.05;
        font-weight: 850;
        letter-spacing: -0.055em;
    }

    .hero-title-accent {
        color: #4f46e5;
    }

    .hero-subtitle {
        max-width: 760px;
        margin: 1rem auto 0 auto;
        color: #667085;
        font-size: 1.05rem;
        line-height: 1.75;
    }


    /* ========================================================
       SECTION
    ======================================================== */

    .section-title {
        margin-top: 1.8rem;
        color: #101828;
        font-size: 1.25rem;
        font-weight: 800;
    }

    .section-description {
        margin-top: 0.35rem;
        margin-bottom: 1rem;
        color: #667085;
        font-size: 0.9rem;
        line-height: 1.6;
    }


    /* ========================================================
       UPLOAD CARD
    ======================================================== */

    .upload-card {
        background: #ffffff;
        border: 1px solid #e4e7ec;
        border-radius: 20px;
        padding: 1.4rem;
        margin-bottom: 1rem;
        box-shadow:
            0 10px 25px rgba(16, 24, 40, 0.04),
            0 2px 6px rgba(16, 24, 40, 0.02);
    }

    .upload-row {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .upload-icon {
        width: 46px;
        height: 46px;
        min-width: 46px;
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: 13px;
        background: #eef2ff;
        font-size: 1.25rem;
    }

    .upload-title {
        color: #1d2939;
        font-size: 1rem;
        font-weight: 800;
    }

    .upload-description {
        margin-top: 0.2rem;
        color: #667085;
        font-size: 0.85rem;
        line-height: 1.5;
    }


    /* ========================================================
       FILE STATUS
    ======================================================== */

    .file-status {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        background: #ecfdf3;
        border: 1px solid #abefc6;
        border-radius: 12px;
        padding: 0.8rem 1rem;
        margin-top: 0.8rem;
        color: #067647;
        font-size: 0.87rem;
    }


    /* ========================================================
       FILE UPLOADER
    ======================================================== */

    [data-testid="stFileUploader"] {
        margin-top: 0.9rem;
    }

    [data-testid="stFileUploaderDropzone"] {
        background: #ffffff !important;
        border: 1px dashed #a5b4fc !important;
        border-radius: 16px !important;
    }


    /* ========================================================
       TEXT AREA
    ======================================================== */

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
            0 0 0 3px rgba(99, 102, 241, 0.1) !important;
    }


    /* ========================================================
       ANALYZE BUTTON
    ======================================================== */

    .stButton > button {
        min-height: 3.2rem;
        border-radius: 14px;
        font-size: 1rem;
        font-weight: 800;
        transition:
            transform 0.15s ease,
            box-shadow 0.15s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow:
            0 10px 24px rgba(79, 70, 229, 0.18);
    }


    /* ========================================================
       SCORE CARDS
    ======================================================== */

    .score-card {
        background: #ffffff;
        border: 1px solid #e4e7ec;
        border-radius: 18px;
        padding: 1.2rem;
        min-height: 145px;
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

    .score-number {
        color: #101828;
        font-size: 2.3rem;
        line-height: 1;
        font-weight: 850;
        letter-spacing: -0.05em;
    }

    .score-max {
        color: #98a2b3;
        font-size: 0.95rem;
        font-weight: 650;
        letter-spacing: 0;
    }


    /* ========================================================
       RESULT CARD
    ======================================================== */

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
    }

    .result-card-description {
        color: #667085;
        font-size: 0.84rem;
        line-height: 1.55;
        margin-top: 0.3rem;
    }


    /* ========================================================
       BADGES
    ======================================================== */

    .badge {
        display: inline-block;
        padding: 0.28rem 0.65rem;
        border-radius: 999px;
        font-size: 0.74rem;
        font-weight: 750;
    }

    .badge-high {
        background: #fef3f2;
        border: 1px solid #fecdca;
        color: #b42318;
    }

    .badge-medium {
        background: #fffaeb;
        border: 1px solid #fedf89;
        color: #b54708;
    }

    .badge-low {
        background: #ecfdf3;
        border: 1px solid #abefc6;
        color: #027a48;
    }


    /* ========================================================
       KEYWORD BOX
    ======================================================== */

    .keyword-box {
        background: #ffffff;
        border: 1px solid #e4e7ec;
        border-radius: 18px;
        padding: 1.25rem;
        min-height: 155px;
        box-shadow:
            0 8px 24px rgba(16, 24, 40, 0.035);
    }

    .keyword-title {
        color: #344054;
        font-size: 0.88rem;
        font-weight: 800;
        margin-bottom: 0.7rem;
    }

    .keyword {
        display: inline-block;
        margin: 0.15rem;
        padding: 0.35rem 0.55rem;
        border-radius: 8px;
        background: #f8fafc;
        border: 1px solid #e4e7ec;
        color: #344054;
        font-size: 0.76rem;
    }


    /* ========================================================
       VERDICT
    ======================================================== */

    .verdict-card {
        background:
            linear-gradient(
                135deg,
                #eef2ff 0%,
                #ffffff 100%
            );
        border: 1px solid #c7d2fe;
        border-radius: 22px;
        padding: 1.7rem;
        box-shadow:
            0 12px 30px rgba(79, 70, 229, 0.08);
    }

    .verdict-label {
        color: #6366f1;
        font-size: 0.75rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    .verdict-title {
        color: #101828;
        font-size: 2rem;
        font-weight: 850;
        letter-spacing: -0.04em;
        margin-top: 0.4rem;
    }

    .verdict-summary {
        max-width: 850px;
        color: #475467;
        line-height: 1.7;
        font-size: 0.95rem;
        margin-top: 0.65rem;
    }


    /* ========================================================
       FOOTER
    ======================================================== */

    .custom-footer {
        margin-top: 3rem;
        padding-top: 1.25rem;
        border-top: 1px solid #e4e7ec;
        text-align: center;
        color: #98a2b3;
        font-size: 0.78rem;
    }

    </style>
    """
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def render_html(content: str) -> None:
    """Render custom HTML using Streamlit's native HTML component."""
    st.html(content)


def badge(value: str) -> str:
    """Return HTML for a High/Medium/Low badge."""

    safe_value = html.escape(value)

    badge_class = {
        "high": "badge-high",
        "medium": "badge-medium",
        "low": "badge-low",
    }.get(
        value.lower(),
        "badge-medium",
    )

    return (
        f'<span class="badge {badge_class}">'
        f"{safe_value}"
        f"</span>"
    )


def score_card(
    label: str,
    score: int,
) -> None:
    """Display a modern score card."""

    safe_label = html.escape(label)

    render_html(
        f"""
        <div class="score-card">

            <div class="score-label">
                {safe_label}
            </div>

            <div class="score-number">
                {score}
                <span class="score-max">/100</span>
            </div>

        </div>
        """
    )


def keyword_pills(
    keywords: list[str],
) -> None:
    """Render keywords as HTML pills."""

    if not keywords:
        st.caption("No keywords identified.")
        return

    content = ""

    for keyword in keywords:
        content += (
            '<span class="keyword">'
            f"{html.escape(keyword)}"
            "</span>"
        )

    render_html(content)


# ============================================================
# HERO
# ============================================================

render_html(
    """
    <div class="hero">

        <div class="hero-badge">
            ✦ AI-Powered Resume Analysis
        </div>

        <div class="hero-title">
            AI Resume
            <span class="hero-title-accent">
                Analyzer
            </span>
        </div>

        <div class="hero-subtitle">
            Compare your resume against a specific job description
            and discover your strengths, skill gaps, ATS keywords,
            resume problems, and practical recommendations.
        </div>

    </div>
    """
)


# ============================================================
# SECTION 1 — RESUME
# ============================================================

render_html(
    """
    <div class="section-title">
        1. Upload Your Resume
    </div>

    <div class="section-description">
        Upload your current resume in PDF or DOCX format.
    </div>

    <div class="upload-card">

        <div class="upload-row">

            <div class="upload-icon">
                📄
            </div>

            <div>
                <div class="upload-title">
                    Resume Document
                </div>

                <div class="upload-description">
                    Upload your resume and we will extract
                    the text before analyzing it against the job.
                </div>
            </div>

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

                ✅

                <span>
                    <strong>
                        {html.escape(uploaded_file.name)}
                    </strong>

                    &nbsp;·&nbsp;

                    {len(resume_text.split())}
                    words extracted successfully
                </span>

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
# SECTION 2 — JOB DESCRIPTION
# ============================================================

render_html(
    """
    <div class="section-title">
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
# SECTION 3 — ANALYZE
# ============================================================

render_html(
    """
    <div class="section-title">
        3. Analyze Your Resume
    </div>

    <div class="section-description">
        Groq will compare your resume with the supplied job
        description and create an evidence-based report.
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
            "Analyzing your resume with Groq..."
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
                    "Something unexpected happened while "
                    "analyzing your resume. Please try again."
                )


# ============================================================
# RESULTS
# ============================================================

if "analysis_result" in st.session_state:

    result = st.session_state[
        "analysis_result"
    ]

    st.divider()

    render_html(
        """
        <div class="section-title">
            Resume Analysis Results
        </div>

        <div class="section-description">
            Recruiter-style analysis based on your resume
            and the supplied job description.
        </div>
        """
    )


    # ========================================================
    # SCORE DASHBOARD
    # ========================================================

    columns = st.columns(4)

    with columns[0]:

        score_card(
            "Overall Score",
            result.overall_score,
        )

        st.caption(
            result.overall_explanation
        )

        st.progress(
            result.overall_score / 100
        )


    with columns[1]:

        score_card(
            "Job Match",
            result.job_match.score,
        )

        st.caption(
            result.job_match.explanation
        )

        st.progress(
            result.job_match.score / 100
        )


    with columns[2]:

        score_card(
            "ATS Compatibility",
            result.ats_compatibility.score,
        )

        st.caption(
            result.ats_compatibility.explanation
        )

        st.progress(
            result.ats_compatibility.score / 100
        )


    with columns[3]:

        score_card(
            "Resume Quality",
            result.resume_quality.score,
        )

        st.caption(
            result.resume_quality.explanation
        )

        st.progress(
            result.resume_quality.score / 100
        )


    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )


    # ========================================================
    # TABS
    # ========================================================

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

        left, right = st.columns(2)

        with left:

            render_html(
                """
                <div class="result-card">

                    <div class="result-card-title">
                        ✅ Matching Skills
                    </div>

                    <div class="result-card-description">
                        Skills found in your resume that
                        are relevant to the job.
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


        with right:

            render_html(
                """
                <div class="result-card">

                    <div class="result-card-title">
                        ❌ Missing Skills
                    </div>

                    <div class="result-card-description">
                        Important requirements that are not
                        clearly demonstrated in your resume.
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
                            badge(
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
                    Relevant experience mapped to actual
                    requirements in the job description.
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
                    Weaknesses that may reduce your chances
                    for this particular position.
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
                        badge(
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
                    Practical and honest improvements you
                    can make to strengthen your resume.
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
                        badge(
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

        left, right = st.columns(2)

        with left:

            render_html(
                """
                <div class="keyword-box">

                    <div class="keyword-title">
                        ✅ Matched Keywords
                    </div>

                </div>
                """
            )

            keyword_pills(
                result.matched_keywords
            )


        with right:

            render_html(
                """
                <div class="keyword-box">

                    <div class="keyword-title">
                        ❌ Missing Keywords
                    </div>

                </div>
                """
            )

            keyword_pills(
                result.missing_keywords
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

        st.markdown("### Overall Assessment")

        st.write(
            result.overall_explanation
        )

        st.markdown("### Score Breakdown")

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
