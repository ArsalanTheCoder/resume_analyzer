# AI Resume Analyzer

A beginner-friendly Streamlit application that compares a PDF or DOCX resume against a specific job description using Grok through the xAI API.

## Features

- Upload PDF or DOCX resumes.
- Extract text locally with PyMuPDF and python-docx.
- Paste a complete job description.
- Analyze the resume against that exact job.
- Use Grok through the OpenAI Python SDK.
- Validate the AI response with Pydantic structured output.
- Display:
  - Overall Score
  - Job Match
  - ATS Compatibility
  - Resume Quality
  - Matching Skills
  - Missing Skills
  - Matching Experience
  - Resume Problems
  - Recommendations
  - Matched Keywords
  - Missing Keywords
  - Final Verdict
  - Final Summary
- Keep the xAI API key in `.env`.

## Architecture

```text
ai_resume_analyzer/
│
├── app.py              # Streamlit UI and result dashboard
├── analyzer.py         # xAI/Grok client and structured response models
├── resume_parser.py    # PDF/DOCX text extraction
├── prompts.py          # System prompt and analysis input
├── requirements.txt    # Python dependencies
├── .env                # Local secrets (create this yourself)
├── .env.example        # Example environment variables
├── .gitignore          # Prevent secrets and Python cache from being committed
└── README.md           # Project documentation
```

## Requirements

- Python 3.10+
- An xAI API key
- Internet access for the Grok API call

## Installation

### 1. Create a project folder

```bash
mkdir ai_resume_analyzer
cd ai_resume_analyzer
```

Copy the project files into this folder.

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the `.env` file

Copy `.env.example` to `.env`.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Then edit `.env`:

```env
XAI_API_KEY=your_real_xai_api_key
GROK_MODEL=grok-4.6
```

Never commit `.env` to Git.

## Getting an xAI API key

Create an API key in the xAI developer console and place it in `XAI_API_KEY`.

## Run the application

```bash
streamlit run app.py
```

Streamlit will show a local URL, normally something like:

```text
http://localhost:8501
```

Open that URL in your browser.

## How it works

1. The user uploads a PDF or DOCX resume.
2. The application extracts the text locally.
3. The user pastes the complete job description.
4. The Analyze Resume button sends both pieces of text to Grok.
5. Grok compares the resume against the job description.
6. The structured response is validated with Pydantic.
7. Streamlit renders the score cards and detailed recruiter-style results.

## Important behavior

This application is intentionally evidence-based.

It should not:
- invent skills or experience,
- assume missing experience,
- recommend lying on a resume,
- judge protected or personal characteristics,
- claim support for a specific ATS product without evidence.

For missing skills, recommendations are framed as future learning or practical experience rather than as existing qualifications.

## Troubleshooting

### `XAI_API_KEY is missing`

Make sure:
- the file is named `.env`,
- the variable is exactly `XAI_API_KEY`,
- Streamlit was restarted after changing `.env`.

### Authentication error

Verify that your xAI API key is valid and active.

### API/model error

Verify the model name in `.env`. The default in this project is:

```env
GROK_MODEL=grok-4.6
```

### PDF says there is no readable text

The file may be a scanned/image-only PDF. This project does not perform OCR; use a text-based PDF or add an OCR layer separately.

## Security

The API key is read from the environment and is never displayed in the Streamlit UI.

Keep `.env` private and do not commit it to source control.
