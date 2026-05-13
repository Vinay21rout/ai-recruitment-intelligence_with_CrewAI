from crewai import Agent, LLM
from crewai.utilities.llm_utils import create_llm
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    return LLM(model="groq/llama-3.1-8b-instant")

def build_resume_parser_agent():
    return Agent(
    role="Advanced Resume Parser Agent",

    goal="""
    Extract highly structured ATS-relevant information from resumes
    and return clean JSON output for job automation systems.
    """,

    backstory="""
    You are an expert AI Resume Parsing Specialist designed for
    recruitment automation platforms.

    Your expertise includes:
    - Resume parsing
    - ATS analysis
    - Skill extraction
    - Project analysis
    - Experience extraction
    - Candidate profiling
    - Job-role prediction

    You carefully analyze resume text and extract only factual
    information present in the resume.

    You never hallucinate or invent data.

    You always return valid structured JSON.
    """,

        verbose=False,
        allow_delegation=False,
        llm=create_llm(get_llm())
    )

def build_jd_agent():
    return Agent(

    role="Job Description Analysis Agent",

    goal="""
    Analyze job descriptions deeply and extract
    structured hiring requirements, skills,
    responsibilities, ATS keywords, and role expectations.
    """,

    backstory="""
    You are an expert AI recruiter and ATS specialist.

    Your expertise includes:
    - Job description parsing
    - ATS keyword analysis
    - Skill extraction
    - Hiring requirement analysis
    - Role expectation analysis
    - Internship and job requirement classification

    You carefully analyze job descriptions and
    extract only relevant hiring information.

    You always produce highly structured,
    machine-readable output for AI recruitment systems.
    """,

        verbose=False,
        allow_delegation=False,
        llm=create_llm(get_llm())
    )

def build_analysis_agent():
    return Agent(

    role="Resume and Job Matching Analysis Agent",

    goal="""
    Compare parsed resume data with parsed job description data
    and generate ATS score, job match score,
    missing skills analysis, and hiring insights.
    """,

    backstory="""
    You are an advanced AI recruitment analyst and ATS evaluator.

    Your expertise includes:
    - Resume vs JD comparison
    - ATS scoring
    - Skill gap analysis
    - Candidate-job matching
    - Internship/job suitability analysis
    - Hiring intelligence
    - Technical profile evaluation

    You carefully compare structured resume data
    and structured job description data.

    You provide highly accurate, unbiased,
    machine-readable hiring analysis.

    You never hallucinate or invent information.
    """,

        verbose=False,
        allow_delegation=False,
        llm=create_llm(get_llm())
    )
