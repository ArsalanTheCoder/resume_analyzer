"""Groq API integration and structured resume-analysis models."""

from __future__ import annotations

import os
from typing import Literal

from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
)
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from prompts import ANALYSIS_SYSTEM_PROMPT, build_analysis_input


# Load variables from .env when running locally.
# On Streamlit Cloud, these values can come from Streamlit Secrets.
load_dotenv()


GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_MODEL = "openai/gpt-oss-120b"


class AnalysisError(Exception):
    """User-friendly exception for resume-analysis failures."""


class ScoreExplanation(BaseModel):
    """A score with its supporting explanation."""

    model_config = ConfigDict(extra="forbid")

    score: int = Field(ge=0, le=100)
    explanation: str


class MatchingSkill(BaseModel):
    """A skill present in the resume and relevant to the job."""

    model_config = ConfigDict(extra="forbid")

    skill: str
    explanation: str


class MissingSkill(BaseModel):
    """A job-relevant skill not clearly demonstrated by the resume."""

    model_config = ConfigDict(extra="forbid")

    skill: str
    importance: Literal["High", "Medium", "Low"]
    explanation: str


class MatchingExperience(BaseModel):
    """Resume experience that relates to a job requirement."""

    model_config = ConfigDict(extra="forbid")

    experience: str
    job_requirement: str
    explanation: str


class ResumeProblem(BaseModel):
    """A resume weakness relative to the supplied job."""

    model_config = ConfigDict(extra="forbid")

    problem: str
    severity: Literal["High", "Medium", "Low"]
    explanation: str


class Recommendation(BaseModel):
    """An actionable recommendation for improving job fit."""

    model_config = ConfigDict(extra="forbid")

    recommendation: str
    priority: Literal["High", "Medium", "Low"]
    explanation: str
    action: str


class ResumeAnalysis(BaseModel):
    """Complete structured output returned by the Groq model."""

    model_config = ConfigDict(extra="forbid")

    overall_score: int = Field(ge=0, le=100)
    overall_explanation: str

    job_match: ScoreExplanation
    ats_compatibility: ScoreExplanation
    resume_quality: ScoreExplanation

    matching_skills: list[MatchingSkill]
    missing_skills: list[MissingSkill]

    matching_experience: list[MatchingExperience]

    problems: list[ResumeProblem]

    recommendations: list[Recommendation]

    matched_keywords: list[str]
    missing_keywords: list[str]

    final_verdict: str
    final_summary: str


def _client() -> OpenAI:
    """Create an OpenAI-compatible client configured to use Groq."""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise AnalysisError(
            "GROQ_API_KEY is missing. "
            "Add it to your .env file or Streamlit Secrets."
        )

    return OpenAI(
        api_key=api_key,
        base_url=GROQ_BASE_URL,
        timeout=120.0,
        max_retries=2,
    )


def _get_model() -> str:
    """Read the Groq model from the environment."""

    model = os.getenv(
        "GROQ_MODEL",
        DEFAULT_MODEL,
    ).strip()

    return model or DEFAULT_MODEL


def analyze_resume(
    resume_text: str,
    job_description: str,
) -> ResumeAnalysis:
    """
    Send the resume and job description to Groq
    and return a validated structured analysis.
    """

    if not resume_text.strip():
        raise AnalysisError(
            "Resume text is empty."
        )

    if not job_description.strip():
        raise AnalysisError(
            "Job description is empty."
        )

    client = _client()
    model = _get_model()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": ANALYSIS_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": build_analysis_input(
                        resume_text,
                        job_description,
                    ),
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "resume_analysis",
                    "strict": True,
                    "schema": ResumeAnalysis.model_json_schema(),
                },
            },
        )

    except AuthenticationError as exc:
        raise AnalysisError(
            "Groq authentication failed. "
            "Please check your GROQ_API_KEY."
        ) from exc

    except APITimeoutError as exc:
        raise AnalysisError(
            "The Groq request timed out. "
            "Please try again."
        ) from exc

    except APIConnectionError as exc:
        raise AnalysisError(
            "Could not connect to the Groq API. "
            "Please check your internet connection and try again."
        ) from exc

    except APIStatusError as exc:
        status = getattr(
            exc,
            "status_code",
            None,
        )

        if status == 400:
            message = (
                "Groq rejected the request. "
                "Please check the model name and request format."
            )

        elif status == 401:
            message = (
                "Groq authentication failed. "
                "Please check your GROQ_API_KEY."
            )

        elif status == 403:
            message = (
                "Your Groq API key does not have permission "
                "to use this request."
            )

        elif status == 404:
            message = (
                f"The Groq model '{model}' was not found. "
                "Check GROQ_MODEL in your environment settings."
            )

        elif status == 429:
            message = (
                "The Groq rate limit was reached. "
                "Please wait a moment and try again."
            )

        elif status and status >= 500:
            message = (
                "The Groq service returned a server error. "
                "Please try again shortly."
            )

        else:
            message = (
                "The Groq API rejected the request. "
                "Please check your API key, model, and settings."
            )

        raise AnalysisError(message) from exc

    except Exception as exc:
        raise AnalysisError(
            "The AI analysis could not be completed. "
            "Please try again."
        ) from exc

    # Groq returns structured JSON as message.content.
    content = response.choices[0].message.content

    if not content:
        raise AnalysisError(
            "The AI returned an empty response. "
            "Please try again."
        )

    try:
        return ResumeAnalysis.model_validate_json(
            content
        )

    except ValidationError as exc:
        raise AnalysisError(
            "The AI returned an invalid analysis response. "
            "Please try again."
        ) from exc
