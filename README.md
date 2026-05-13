# 🤖 AI Recruitment Intelligence — Multi-Agent System with CrewAI

> An intelligent, production-ready AI recruitment pipeline powered by **CrewAI multi-agent framework**, **FastAPI**, and **Streamlit** — designed to automate resume parsing, job description analysis, and candidate-job matching with ATS scoring.

---

## 📌 Overview

This system uses **3 specialized AI agents** working in a **parallel + sequential pipeline** to:

1. **Parse resumes** — extract structured ATS-relevant data (skills, projects, experience, certifications)
2. **Analyze job descriptions** — extract hiring requirements, ATS keywords, responsibilities
3. **Match & score** — compare resume vs JD and generate ATS score, job match %, skill gap analysis, and hiring recommendation

The backend is served via **FastAPI** with dedicated endpoints for each agent, and the frontend is a **Streamlit** dashboard with live agent status updates, real-time logs, and rich result visualization.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI (app.py)                 │
│         Live Agent Cards | Workflow Diagram | Results    │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP Requests
┌──────────────────────▼──────────────────────────────────┐
│                  FastAPI Backend (api/main.py)           │
│                                                          │
│  POST /parse-resume   POST /analyze-jd   POST /analyze-match │
│  POST /run-pipeline   GET  /health                       │
└──────────┬───────────────────┬──────────────────────────┘
           │                   │
    ┌──────▼──────┐     ┌──────▼──────┐
    │  agent.py   │     │   task.py   │
    │  (factory   │     │  (factory   │
    │  functions) │     │  functions) │
    └──────┬──────┘     └──────┬──────┘
           └─────────┬─────────┘
                     │
        ┌────────────▼────────────┐
        │     CrewAI Agents       │
        │                         │
        │  ⚡ PHASE 1 (Parallel)  │
        │  📄 Resume Parser Agent │
        │  📋 JD Analysis Agent   │
        │                         │
        │  🔗 PHASE 2 (Sequential)│
        │  🔍 Matching Agent      │
        └─────────────────────────┘
```

---

## 🧠 Agents

| Agent | Role | Endpoint | Execution |
|-------|------|----------|-----------|
| 📄 Resume Parser Agent | Extracts structured ATS data from resume | `POST /parse-resume` | Parallel (Phase 1) |
| 📋 JD Analysis Agent | Extracts hiring requirements from JD | `POST /analyze-jd` | Parallel (Phase 1) |
| 🔍 Matching Analysis Agent | Compares resume vs JD, generates scores | `POST /analyze-match` | Sequential (Phase 2) |

---

## 📊 Output — What the System Generates

| Output | Description |
|--------|-------------|
| **ATS Score** | Compatibility score out of 10 |
| **Job Match %** | Overall candidate-job match percentage |
| **Technical Match Score** | Technical skills alignment score |
| **Project Relevance Score** | How relevant candidate projects are |
| **Matched Skills** | Skills present in both resume and JD |
| **Missing Skills** | Skills required by JD but absent in resume |
| **Partial Matches** | Skills partially matching JD requirements |
| **Candidate Strengths** | Key strengths identified |
| **Candidate Weaknesses** | Areas needing improvement |
| **Matching Projects** | Projects relevant to the JD |
| **ATS Keyword Analysis** | Keyword match quality + missing keywords |
| **Interview Probability** | Low / Medium / High |
| **Hiring Recommendation** | Detailed hiring decision |
| **Improvement Suggestions** | Actionable resume improvement tips |
| **Final Decision** | is_good_fit + detailed reasoning |

---

## 🗂️ Project Structure

```
JOB_AUTOMATION_MULTIAGENT/
│
├── api/
│   └── main.py              # FastAPI backend — all agent endpoints
│
├── agent.py                 # Agent factory functions (build_*_agent)
├── task.py                  # Task factory functions (build_*_task)
├── crew.py                  # Direct crew runner (for CLI testing)
├── app.py                   # Streamlit frontend UI
│
├── sample_input.py          # Sample resume + JD for testing
├── .env.example             # Environment variable template
├── .gitignore
└── README.md
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent Framework | [CrewAI](https://github.com/crewAIInc/crewAI) |
| Backend API | [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn |
| Frontend UI | [Streamlit](https://streamlit.io/) |
| LLM Support | Google Gemini / Groq / Ollama |
| Package Manager | [uv](https://github.com/astral-sh/uv) |
| Python | 3.11 |

---

## 🚀 Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/Vinay21rout/ai-recruitment-intelligence_with_CrewAI.git
cd ai-recruitment-intelligence_with_CrewAI/JOB_AUTOMATION_MULTIAGENT
```

### 2. Create virtual environment with Python 3.11

```bash
py -3.11 -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux
```

### 3. Install dependencies

```bash
pip install crewai fastapi uvicorn streamlit langchain-google-genai langchain-groq python-dotenv requests
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```env
# Choose one LLM provider:
GOOGLE_API_KEY=your_gemini_api_key    # https://aistudio.google.com/app/apikey
GROQ_API_KEY=your_groq_api_key        # https://console.groq.com/keys
OPENAI_API_KEY=NA
```

### 5. Configure LLM in `agent.py`

```python
# Google Gemini (best quality)
def get_llm():
    return LLM(model="google/gemini-2.5-flash")

# OR Groq (fast + free)
def get_llm():
    return LLM(model="groq/llama-3.3-70b-versatile")

# OR Ollama (local)
def get_llm():
    return LLM(model="ollama/phi3:mini", base_url="http://localhost:11434")
```

---

## ▶️ Running the System

### Terminal 1 — Start FastAPI backend

```bash
cd JOB_AUTOMATION_MULTIAGENT
uvicorn api.main:app --reload --port 8000
```

### Terminal 2 — Start Streamlit frontend

```bash
python -m streamlit run app.py
```

Open: **http://localhost:8501**

API Docs: **http://localhost:8000/docs**

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Server health check |
| `POST` | `/parse-resume` | Run Resume Parser Agent |
| `POST` | `/analyze-jd` | Run JD Analysis Agent |
| `POST` | `/analyze-match` | Run Matching Analysis Agent |
| `POST` | `/run-pipeline` | Run full pipeline (all 3 agents) |

### Example Request

```bash
curl -X POST http://localhost:8000/parse-resume \
  -H "Content-Type: application/json" \
  -d '{"resume_text": "Your resume text here..."}'
```

### Example Response

```json
{
  "result": "{\"personal_information\": {...}, \"skills\": {...}, \"projects\": [...], ...}"
}
```

---

## 🖥️ Streamlit UI Features

- **Live Agent Status Cards** — each agent card updates in real-time (Idle → Running → Done)
- **Workflow Architecture Diagram** — visual representation of parallel + sequential pipeline
- **Live Agent Log** — timestamped log stream showing agent progress
- **Execution Timing** — each agent card shows time taken
- **Score Dashboard** — ATS Score, Job Match %, Technical Match, Project Relevance
- **Skills Analysis** — matched / missing / partial skill tags
- **Strengths & Weaknesses** — side-by-side candidate evaluation
- **ATS Keyword Analysis** — keyword quality + missing keywords
- **Improvement Recommendations** — actionable suggestions
- **Final Hiring Decision** — reasoning + recommendation
- **Raw JSON Toggle** — view complete structured output
- **FastAPI Health Indicator** — live server status in sidebar

---

## 🧪 CLI Testing (without UI)

```bash
# Edit sample_input.py with your resume and JD
# Then run:
python crew.py
```

---

## 🔑 Supported LLM Providers

| Provider | Model | Free Tier |
|----------|-------|-----------|
| Google Gemini | `google/gemini-2.5-flash` | 15 RPM, 1500/day |
| Google Gemini | `gemini/gemini-1.5-flash` | Higher quota |
| Groq | `groq/llama-3.3-70b-versatile` | Generous free tier |
| Groq | `groq/deepseek-r1-distill-llama-70b` | Best JSON quality on Groq |
| Ollama | `ollama/phi3:mini` | Local, unlimited |
| Ollama | `ollama/llama3.1:8b` | Local, better quality |

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 👤 Author

**Vinay Kumar Rout**
- GitHub: [@Vinay21rout](https://github.com/Vinay21rout)
- LinkedIn: [linkedin.com/in/vinay-kumar-rout-4798372a9](https://linkedin.com/in/vinay-kumar-rout-4798372a9)
