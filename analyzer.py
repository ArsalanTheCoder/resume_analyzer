"""Grok API integration and structured resume-analysis models."""

from __future__ import annotations

import os
import json
from typing import Literal

from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, APITimeoutError, AuthenticationError, OpenAI
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from prompts import ANALYSIS_SYSTEM_PROMPT, build_analysis_input

load_dotenv()

GROQ_BASE_URL = "https://api.groq.com/openai/v1"


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
    """Complete structured output expected from Grok."""

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
    """Create an OpenAI client configured for Groq."""
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise AnalysisError(
            "GROQ_API_KEY is missing. Add it to your .env file or Streamlit Secrets."
        )

    return OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
        timeout=120.0,
        max_retries=2,
    )


def analyze_resume(resume_text: str, job_description: str) -> ResumeAnalysis:
    """Send resume and job description to Grok and return validated structured output."""
    model = (
        os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-120b",
        ).strip()
        or "openai/gpt-oss-120b"
    )

    if not resume_text.strip():
        raise AnalysisError("Resume text is empty.")
    if not job_description.strip():
        raise AnalysisError("Job description is empty.")

    client = _client()

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
            "xAI authentication failed. Check that XAI_API_KEY is valid."
        ) from exc
    except APITimeoutError as exc:
        raise AnalysisError(
            "The xAI request timed out. Please try again."
        ) from exc
    except APIConnectionError as exc:
        raise AnalysisError(
            "Could not connect to the xAI API. Check your internet connection and try again."
        ) from exc
    except APIStatusError as exc:
        status = getattr(exc, "status_code", None)
        if status == 429:
            message = "The xAI API rate limit was reached. Please wait and try again."
        elif status and status >= 500:
            message = "The xAI service returned a server error. Please try again shortly."
        else:
            message = "The xAI API rejected the request. Check your model name, API key, and request settings."
        raise AnalysisError(message) from exc
    except Exception as exc:
        raise AnalysisError(
            "The AI analysis could not be completed. Please try again."
        ) from exc

    parsed = getattr(response, "output_parsed", None)
    if parsed is None:
        # Defensive fallback for SDK/API compatibility changes.
        try:
            output_text = getattr(response, "output_text", "")
            if not output_text:
                raise ValueError("No structured output was returned.")
            return ResumeAnalysis.model_validate_json(output_text)
        except (ValueError, ValidationError, TypeError) as exc:
            raise AnalysisError(
                "The AI returned an invalid analysis response. Please try again."
            ) from exc

    if not isinstance(parsed, ResumeAnalysis):
        try:
            return ResumeAnalysis.model_validate(parsed)
        except ValidationError as exc:
            raise AnalysisError(
                "The AI response did not match the expected analysis structure."
            ) from exc

    return parsed
