# ShortlistIQ - AI Resume Shortlisting System

## 1. Project Overview
- **Project Title:** ShortlistIQ: Automated Resume Screening & Candidate Shortlisting System
- **Team Members:** 
  - Divyanshu Soni (Roll Number: `<Your Roll Number>`)
  - *(Add additional team member names and roll numbers here)*
- **Technology Stack:** Python 3.10+, Groq Cloud API (High-Performance LLM Inference), PyMuPDF (PDF Extraction), Pydantic v2 (Data Validation), Rich (Terminal UI), python-dotenv, UV Package Manager
- **Project Guide/Mentor:** `<Mentor / Guide Name>`
- **Project Objective:** To automate and streamline candidate evaluation by semantically parsing resumes against specific job descriptions using Large Language Models (LLMs), producing objective scores, detailed reasoning, and ranked shortlists without recruiter bias or manual screening fatigue.

---

## 2. Problem Statement
Recruitment teams receive hundreds to thousands of resumes for every technical job opening. Manually screening each candidate is extremely time-consuming, inconsistent, and susceptible to cognitive fatigue and unconscious bias. 

On the other hand, conventional Applicant Tracking Systems (ATS) rely primarily on naive keyword matching—penalizing strong candidates who describe experiences with different terminology while favoring candidates who simply keyword-stuff their resumes.

**ShortlistIQ** solves this problem by conducting an intelligent, semantic evaluation. It evaluates candidate resumes holistically across five distinct evaluation dimensions (Technical Skills, Experience, Industry Relevance, Education, and Overall Fit), providing structured scores, detailed justifications, and actionable ranking recommendations.

---

## 3. Features
- **Automated Resume Parsing:** Ingests and extracts clean textual content from multi-page PDF resumes using PyMuPDF.
- **Multi-Dimensional AI Evaluation:** Analyzes candidates across 5 structured dimensions with dedicated scoring (1-10) and written reasoning:
  - Technical Skills & Depth
  - Relevant Professional Experience
  - Industry Relevance & Domain Alignment
  - Educational Background
  - Overall Role & Culture Fit
- **Strict Schema Enforcement:** Leverages Pydantic v2 models and LLM JSON-mode to guarantee valid, type-safe structured data without hallucinated structures.
- **Transparent Reasoning & Insights:** Identifies concrete key strengths, red flags/concerns, and provides a clear justification for every numerical score assigned.
- **Automated Candidate Ranking:** Dynamically sorts candidates by total score (out of 50) and categorizes them into actionable tiers (`Hire`, `Strong Consider`, `Interview`, `Pass`).
- **Interactive Rich Terminal UI:** Built with formatted header banners, live loading spinners, metric summary cards, and color-coded candidate comparison tables.
- **High-Speed & Cost-Effective:** Powered by Groq's high-throughput LPU inference engine, running state-of-the-art open-weight models at zero API cost.

---

## 4. Technology Stack
- **Programming Language:** Python 3.10+
- **LLM Inference Engine:** [Groq Cloud API](https://console.groq.com/) (`qwen/qwen3.8-27b`)
- **PDF Processing:** [PyMuPDF](https://pymupdf.readthedocs.io/) (`pymupdf`)
- **Data Validation & Typing:** [Pydantic v2](https://docs.pydantic.dev/)
- **Terminal User Interface (TUI):** [Rich](https://rich.readthedocs.io/)
- **Configuration & Environment:** [python-dotenv](https://github.com/theskumar/python-dotenv)
- **Dependency Management:** [UV](https://docs.astral.sh/uv/) (Astral)

---

## 5. Project Structure
```text
resumeShortlister/
├── .env.example              # Environment variables template
├── .env.local                # Local API keys (excluded from git)
├── .gitignore                # Git ignore rules
├── guidance_prompt.md        # AI evaluation criteria, scoring rubric, and instructions
├── job_description.md        # Target role description, requirements, and qualifications
├── main.py                   # Application entry point & orchestration workflow
├── pyproject.toml            # Project dependencies and packaging configuration
├── README.md                 # Project documentation
├── resumes/                  # Input directory for candidate PDF resumes
│   └── Divyanshu's_RESUME.pdf
├── ui.py                     # Rich CLI components, scorecards, tables, and banners
├── utils.py                  # PDF parser, Groq API client, and Pydantic schemas
└── uv.lock                   # Locked dependency graph
```

---

## 6. Installation and Execution

### Prerequisites
- Python 3.10 or higher installed on your system
- A free [Groq Cloud API Key](https://console.groq.com/)

### Step 1: Clone the Repository
```bash
git clone https://github.com/pbanuru/resumeShortlister.git
cd resumeShortlister
```

### Step 2: Set Up Virtual Environment & Dependencies

**Option A: Using UV (Recommended - Fast)**
```bash
# Install uv if you haven't already
# Windows (PowerShell):
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS / Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies
uv sync
```

**Option B: Using standard Python `venv` and `pip`**
```bash
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

# Install required packages
pip install groq pymupdf pydantic python-dotenv rich
```

### Step 3: Configure Environment Variables
Copy `.env.example` to create your local `.env.local` file:
```bash
cp .env.example .env.local
```

Open `.env.local` and add your Groq API key:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
```

### Step 4: Add Resumes and Job Description
1. Place candidate resume files (`.pdf` format) inside the `resumes/` folder.
2. Update `job_description.md` with your target role requirements and qualifications.
3. *(Optional)* Modify `guidance_prompt.md` if you wish to adjust scoring weights or evaluation rubrics.

### Step 5: Run the Evaluation
```bash
# If using UV:
uv run main.py

# Or with activated virtual environment:
python main.py
```

---

## 7. Screenshots / Output

### Terminal Execution Output

```text
    ╭─────────────────────────────────────────────╮
    │         AI Resume Shortlister               │
    │     Powered by Groq ⚡ Qwen 3.8            │
    ╰─────────────────────────────────────────────╯

Setting up environment...
Environment setup complete!

Loading guidance prompt and job description...
Templates loaded successfully!

Scanning for resume PDFs...
Found 1 resume files:
        Divyanshu's_RESUME.pdf

Processing 1 resumes with AI... Complete!

┌─────── Total Candidates ────────┐ ┌─ Average Score ─┐ ┌─ 🏆 Top Candidate ─┐
│ 1                               │ │ 18.0/50         │ │ Divyanshu Soni     │
└─────────────────────────────────┘ └─────────────────┘ │ 18/50              │
                                                        └────────────────────┘
┌─ Strong Candidates (35+ score) ─┐                                           
│ 0                               │                                           
└─────────────────────────────────┘                                           

                         🏆 Resume Evaluation Results                          
┌────┬──────────────────┬────────┬────────┬────────┬───────┬────────┬─────────┐
│    │                  │ Techn… │        │ Indus… │       │ Overa… │  Total  │
│ R… │ Candidate        │ Skills │ Exper… │ Relev… │ Educ… │  Fit   │  Score  │
├────┼──────────────────┼────────┼────────┼────────┼───────┼────────┼─────────┤
│ 🥇 │ Divyanshu Soni   │  4/10  │  2/10  │  3/10  │ 6/10  │  3/10  │  18/50  │
└────┴──────────────────┴────────┴────────┴────────┴───────┴────────┴─────────┘

Total Candidates Evaluated: 1
Top Recommendation: None - Candidate does not meet minimum experience requirements.
Ready for Interview: None
```

---

## 8. DSA Concepts Used

*The following Data Structures and Algorithms concepts are practically implemented in this project:*

- **Strings & Text Processing:**
  - File reading and stream processing of raw extracted PDF text.
  - String normalization, sanitization of markdown code fences (```json), whitespace trimming, and string interpolation.
  - Multi-line system and prompt string templating.
- **Arrays / Lists & Matrices:**
  - Dynamic Lists (`List[Path]`, `List[CandidateEvaluation]`) for batch candidate collection, iteration, and transformation.
  - Two-dimensional tabular data representation (matrix of rows and columns) for console rendering via Rich Table.
- **Hashing & Hash Maps (Dictionaries):**
  - Key-value dictionary lookups ($O(1)$) used for parsing JSON outputs and environment variables.
  - Pydantic schema serialization and validation through Python hash maps (`model_dump()`, `model_validate()`).
- **Searching & Filtering:**
  - Directory scanning and pattern matching using `Path.glob("*.pdf")` ($O(N)$ linear search across files).
  - Threshold filtering to identify strong candidates (`candidate.total_score >= 35`).
- **Sorting (Timsort Algorithm):**
  - Ranking candidates in descending order of total score using Python's hybrid sorting algorithm (Timsort) with $O(N \log N)$ time complexity.
- **Time and Space Complexity:**
  - **Time Complexity:**
    - PDF Text Extraction: $O(N \times P)$ where $N$ is the number of resumes and $P$ is the average page count.
    - Candidate Ranking / Sorting: $O(N \log N)$ where $N$ is the number of candidates.
    - Total Time Complexity: $O(N \times P + N \log N) + \mathcal{O}_{LLM}(T)$ where $T$ is the total token count.
  - **Space Complexity:**
    - Auxiliary memory: $O(N \times K)$ where $K$ is the average character/token size of each resume loaded in memory before batch transmission.

---

## 9. Learning Outcomes
- Understanding the practical mechanics of **Large Language Model (LLM) APIs**, prompt engineering, and temperature tuning.
- Implementing **Structured Outputs (JSON Mode)** with strict schema validation using **Pydantic v2**.
- Parsing, handling, and extracting text from semi-structured binary documents (**PDFs**) programmatically using **PyMuPDF**.
- Building accessible, production-grade **Command Line Interfaces (CLI)** with Rich terminal formatting.
- Managing project environments, dependencies, and lockfiles effectively using modern Python tooling (**UV**).
- Applying fundamental **Data Structures and Algorithms** to data normalization, parsing, and candidate ranking.

---

## 10. Future Scope
- **Web-Based Dashboard:** Build a modern web interface using Next.js / Streamlit / FastAPI for drag-and-drop resume uploading.
- **Candidate Verification Agent:** Integrate search APIs (e.g., Perplexity or GitHub/LinkedIn APIs) to independently verify candidate projects and contributions.
- **Multi-Job Matching:** Enable batch evaluation of resumes across multiple job postings simultaneously to find the best-fit role for each applicant.
- **Export & Integration:** Support one-click export of shortlists to CSV, Excel, PDF reports, or direct integration with ATS webhooks (Greenhouse, Lever).
- **Custom Weighting UI:** Allow HR managers to customize rubric weights per dimension (e.g., weighing technical skills at 40% vs. education at 10%).

---

## 11. References
- [Groq Cloud Documentation & API Reference](https://console.groq.com/docs)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [Pydantic v2 Official Documentation](https://docs.pydantic.dev/latest/)
- [Rich Python Library Documentation](https://rich.readthedocs.io/en/stable/)
- [Astral UV Package Manager Guide](https://docs.astral.sh/uv/)

---

## 12. License
This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
