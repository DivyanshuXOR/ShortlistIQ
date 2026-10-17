import json
import os
from pathlib import Path
from typing import List, Dict, Any
import sys
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
import pymupdf  # PyMuPDF

# Load environment variables
load_dotenv(".env.local", override=True)


class ScoreWithReasoning(BaseModel):
    score: int
    reasoning: str


class CandidateEvaluation(BaseModel):
    name: str
    filename: str
    technical_skills: ScoreWithReasoning
    experience: ScoreWithReasoning
    industry_relevance: ScoreWithReasoning
    education: ScoreWithReasoning
    overall_fit: ScoreWithReasoning
    total_score: int
    key_strengths: List[str]
    concerns: List[str]


class RankedCandidate(BaseModel):
    name: str
    score: int
    ranking_reason: str
    recommendation: str  # Hire/Strong Consider/Interview/Pass


class ResumeEvaluationResults(BaseModel):
    candidates: List[CandidateEvaluation]
    final_ranking: List[RankedCandidate]
    total_candidates_evaluated: int
    top_recommendation: str
    ready_for_interview: List[str]
    notes: str = ""  # Optional notes for any issues


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from a PDF file using PyMuPDF."""
    doc = pymupdf.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()


def load_text_file(file_path: str) -> str:
    """Load text content from a file, with PyInstaller bundle fallback."""
    p = Path(file_path)
    if not p.exists() and hasattr(sys, "_MEIPASS"):
        bundled = Path(sys._MEIPASS) / file_path
        if bundled.exists():
            return bundled.read_text(encoding="utf-8")
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def get_resume_files(resumes_dir: str = "resumes") -> List[Path]:
    """Get all PDF files from the resumes directory."""
    resumes_path = Path(resumes_dir)
    if not resumes_path.exists():
        raise FileNotFoundError(f"Resumes directory '{resumes_dir}' not found")

    pdf_files = list(resumes_path.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in '{resumes_dir}' directory")

    return pdf_files


def prepare_resume_inputs(pdf_files: List[Path]) -> List[Dict[str, Any]]:
    """Extract text from resume PDFs for Groq API."""
    resume_inputs = []

    for pdf_file in pdf_files:
        text = extract_text_from_pdf(str(pdf_file))
        resume_input = {
            "filename": pdf_file.name,
            "text": text,
        }
        resume_inputs.append(resume_input)

    return resume_inputs


def call_groq_api(
    guidance_prompt: str, job_description: str, resume_inputs: List[Dict[str, Any]]
) -> tuple[ResumeEvaluationResults, object]:
    """Make API call to Groq with all resumes and get evaluation."""

    # Check for API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")

    client = Groq(api_key=api_key)

    # Build the resume text sections
    resumes_text = ""
    for i, resume in enumerate(resume_inputs, 1):
        resumes_text += f"\n\n{'='*60}\n"
        resumes_text += f"RESUME #{i} — Filename: {resume['filename']}\n"
        resumes_text += f"{'='*60}\n"
        resumes_text += resume["text"]

    # Prepare the system prompt with JSON schema
    system_prompt = f"""{guidance_prompt}

## JOB DESCRIPTION:
{job_description}

## OUTPUT FORMAT:
You MUST respond with ONLY valid JSON matching this exact schema (no markdown, no extra text):
{json.dumps(ResumeEvaluationResults.model_json_schema(), indent=2)}
"""

    user_message = f"""Please evaluate the following {len(resume_inputs)} resumes against the job description.

{resumes_text}

Respond with ONLY the JSON evaluation. No markdown code fences, no extra text."""

    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
            max_completion_tokens=8000,
            response_format={"type": "json_object"},
        )

        response_text = response.choices[0].message.content

        # Clean up the response
        cleaned = response_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        # Parse the structured output
        result_data = json.loads(cleaned)
        parsed_result = ResumeEvaluationResults.model_validate(result_data)

        return parsed_result, response

    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse Groq response as JSON: {e}\nResponse: {response_text[:500]}")
    except Exception as e:
        raise Exception(f"Groq API call failed: {str(e)}")


def setup_environment():
    """Setup and validate environment."""

    # Check if .env.local exists
    env_file = Path(".env.local")
    if not env_file.exists():
        raise FileNotFoundError(
            ".env.local file not found. Please copy .env.example to .env.local and add your Groq API key"
        )

    # Load and validate API key
    load_dotenv(".env.local", override=True)
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key or api_key == "your-groq-api-key":
        raise ValueError("Please set a valid GROQ_API_KEY in your .env.local file")

    return api_key
