from crewai import Agent, LLM
from crewai.utilities.llm_utils import create_llm
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    return LLM(model="google/gemini-2.5-flash")


def build_resume_parser_agent():
    return Agent(
        role="Resume Parser",

        goal="""
Extract ONLY explicitly written resume information
and return strict structured JSON.
No hallucinations.
No assumptions.
""",

        backstory="""
Enterprise ATS resume extraction engine.
Evidence-only parsing system.
""",

        verbose=False,
        allow_delegation=False,

        llm=create_llm(get_llm())
    )


def build_jd_agent():
    return Agent(
        role="JD Parser",

        goal="""
Extract ONLY explicitly stated hiring requirements
from the job description and return structured JSON.
No hallucinations.
""",

        backstory="""
Enterprise job description intelligence parser.
Strict requirement extraction system.
""",

        verbose=False,
        allow_delegation=False,

        llm=create_llm(get_llm())
    )

def build_analysis_agent():
    return Agent(
        role="ATS Match Analyst",

        goal="""
Compare parsed resume data with parsed JD data.
Generate realistic ATS scoring and skill gap analysis.
No score inflation.
No assumptions.
""",

        backstory="""
Enterprise recruitment intelligence engine.
Strict evidence-based evaluation system.
""",

        verbose=False,
        allow_delegation=False,

        llm=create_llm(get_llm())
    )


def build_email_writer_agent():
    return Agent(
        role="HR Email Writer",

        goal="""
Write concise professional HR emails
using ONLY analysis report data.
No placeholders.
No hallucinations.
""",

        backstory="""
Professional enterprise HR communication engine.
""",

        verbose=False,
        allow_delegation=False,

        llm=create_llm(get_llm())
    )