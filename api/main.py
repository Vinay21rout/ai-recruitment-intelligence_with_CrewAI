import sys, io, threading, traceback, logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from crewai import Crew
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("job-agent-api")

# ── import from existing project files ───────────────────────────────────────
sys.path.append("..")
from agent import build_resume_parser_agent, build_jd_agent, build_analysis_agent, build_email_writer_agent
from task import build_resume_task, build_jd_task, build_analysis_task, build_email_writer_task

load_dotenv()

app = FastAPI(title="Job Automation Multi-Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request Models ────────────────────────────────────────────────────────────
class ResumeRequest(BaseModel):
    resume_text: str

class JDRequest(BaseModel):
    jd_text: str

class AnalysisRequest(BaseModel):
    resume_output: str
    jd_output: str

class EmailRequest(BaseModel):
    analysis_output: str

class FullPipelineRequest(BaseModel):
    resume_text: str
    jd_text: str

# ── Helper ────────────────────────────────────────────────────────────────────
def run_crew_silent(crew: Crew):
    old = sys.stdout
    sys.stdout = io.StringIO()
    try:
        result = crew.kickoff()
    finally:
        sys.stdout = old
    return str(result)


def error_response(endpoint: str, exc: Exception) -> HTTPException:
    tb = traceback.format_exc()
    short = str(exc)
    logger.error(f"[{endpoint}] {short}\n{tb}")
    return HTTPException(
        status_code=500,
        detail={
            "endpoint": endpoint,
            "error": short,
            "type": type(exc).__name__,
            "traceback": tb
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    logger.error(f"Unhandled error on {request.url.path}: {exc}\n{tb}")
    return JSONResponse(
        status_code=500,
        content={
            "endpoint": str(request.url.path),
            "error": str(exc),
            "type": type(exc).__name__,
            "traceback": tb
        }
    )

# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/parse-resume")
def parse_resume(req: ResumeRequest):
    logger.info("[/parse-resume] Starting Resume Parser Agent")
    try:
        agent = build_resume_parser_agent()
        task  = build_resume_task(req.resume_text, agent)
        crew  = Crew(agents=[agent], tasks=[task], verbose=False)
        result = run_crew_silent(crew)
        logger.info("[/parse-resume] Completed successfully")
        return {"result": result}
    except Exception as e:
        raise error_response("/parse-resume", e)


@app.post("/analyze-jd")
def analyze_jd(req: JDRequest):
    logger.info("[/analyze-jd] Starting JD Analysis Agent")
    try:
        agent = build_jd_agent()
        task  = build_jd_task(req.jd_text, agent)
        crew  = Crew(agents=[agent], tasks=[task], verbose=False)
        result = run_crew_silent(crew)
        logger.info("[/analyze-jd] Completed successfully")
        return {"result": result}
    except Exception as e:
        raise error_response("/analyze-jd", e)


@app.post("/analyze-match")
def analyze_match(req: AnalysisRequest):
    logger.info("[/analyze-match] Starting Matching Analysis Agent")
    try:
        r_agent = build_resume_parser_agent()
        j_agent = build_jd_agent()
        a_agent = build_analysis_agent()

        r_task = build_resume_task(req.resume_output, r_agent)
        j_task = build_jd_task(req.jd_output, j_agent)
        a_task = build_analysis_task(a_agent, r_task, j_task)

        crew = Crew(agents=[a_agent], tasks=[a_task], verbose=False)
        result = run_crew_silent(crew)
        logger.info("[/analyze-match] Completed successfully")
        return {"result": result}
    except Exception as e:
        raise error_response("/analyze-match", e)


@app.post("/write-email")
def write_email(req: EmailRequest):
    logger.info("[/write-email] Starting Email Writer Agent")
    try:
        e_agent = build_email_writer_agent()
        e_task  = build_email_writer_task(e_agent, req.analysis_output)
        crew    = Crew(agents=[e_agent], tasks=[e_task], verbose=False)
        result  = run_crew_silent(crew)
        logger.info("[/write-email] Completed successfully")
        return {"result": result}
    except Exception as e:
        raise error_response("/write-email", e)


@app.post("/run-pipeline")
def run_pipeline(req: FullPipelineRequest):
    """Runs all 3 agents: Resume + JD in parallel, then Matching sequentially."""
    results = {}
    errors  = {}

    def run_resume():
        try:
            results["resume"] = parse_resume(ResumeRequest(resume_text=req.resume_text))["result"]
        except Exception as e:
            errors["resume"] = {"error": str(e), "type": type(e).__name__, "traceback": traceback.format_exc()}

    def run_jd():
        try:
            results["jd"] = analyze_jd(JDRequest(jd_text=req.jd_text))["result"]
        except Exception as e:
            errors["jd"] = {"error": str(e), "type": type(e).__name__, "traceback": traceback.format_exc()}

    # Phase 1 — parallel
    t1 = threading.Thread(target=run_resume)
    t2 = threading.Thread(target=run_jd)
    t1.start(); t2.start()
    t1.join();  t2.join()

    if errors:
        return {"status": "error", "errors": errors}

    # Phase 2 — sequential (matching)
    try:
        results["analysis"] = analyze_match(AnalysisRequest(
            resume_output=results["resume"],
            jd_output=results["jd"]
        ))["result"]
    except Exception as e:
        return {"status": "error", "errors": {"analysis": str(e)}}

    # Phase 3 — sequential (email writer)
    try:
        results["email"] = write_email(EmailRequest(
            analysis_output=results["analysis"]
        ))["result"]
    except Exception as e:
        return {"status": "error", "errors": {"email": str(e)}}

    return {
        "status":          "success",
        "resume_output":   results["resume"],
        "jd_output":       results["jd"],
        "analysis_output": results["analysis"],
        "email_output":    results["email"]
    }
