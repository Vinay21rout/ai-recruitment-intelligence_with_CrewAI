from crewai import Task
from agent import build_resume_parser_agent, build_jd_agent, build_analysis_agent

def build_resume_task(resume_text, agent):
    return Task(
        description=f"""
You are an advanced Resume Parser Agent responsible for extracting structured, accurate, ATS-relevant information from resumes for AI-powered job automation systems.

Analyze the following resume carefully and extract all important information.

--------------------------------------------------
OBJECTIVE
--------------------------------------------------

Extract:
- Personal information
- Education
- Skills
- Experience
- Projects
- Certifications
- Achievements
- Resume links
- ATS keywords
- Role suitability
- Missing information
- Resume quality indicators

--------------------------------------------------
INSTRUCTIONS
--------------------------------------------------

1. Extract all relevant details from the resume text.

2. Categorize skills properly into:
- technical_skills
- ai_ml_skills
- soft_skills
- tools_platforms

3. Extract projects with:
- project_name
- description
- technologies_used
- github_link
- live_link
- duration
- complexity_level

4. Extract internships/experience with:
- company_name
- role
- duration
- responsibilities
- technologies_used

5. Extract all URLs separately.

6. Detect ATS keywords.

7. Predict suitable job roles.

8. Detect experience level:
- beginner
- intermediate
- advanced

--------------------------------------------------
OUTPUT FORMAT
--------------------------------------------------

Return ONLY valid JSON.

JSON Structure:

{{
  "personal_information": {{
    "full_name": "",
    "email": "",
    "phone": "",
    "location": "",
    "linkedin": "",
    "github": "",
    "portfolio": ""
  }},

  "professional_summary": "",

  "education": [
    {{
      "degree": "",
      "branch": "",
      "institution": "",
      "cgpa_or_percentage": "",
      "start_year": "",
      "end_year": ""
    }}
  ],

  "skills": {{
    "technical_skills": [],
    "ai_ml_skills": [],
    "soft_skills": [],
    "tools_platforms": []
  }},

  "projects": [
    {{
      "project_name": "",
      "description": "",
      "technologies_used": [],
      "github_link": "",
      "live_link": "",
      "duration": "",
      "complexity_level": ""
    }}
  ],

  "experience": [
    {{
      "company_name": "",
      "role": "",
      "duration": "",
      "responsibilities": [],
      "technologies_used": []
    }}
  ],

  "certifications": [
    {{
      "certificate_name": "",
      "issuer": "",
      "date": "",
      "credential_link": ""
    }}
  ],

  "achievements": [],

  "leadership_and_activities": [],

  "resume_links": {{
    "github_links": [],
    "linkedin_links": [],
    "portfolio_links": [],
    "other_links": []
  }},

  "ats_keywords": [],

  "predicted_roles": [],

  "experience_level": "",

  "resume_metrics": {{
    "resume_length": "",
    "project_count": 0,
    "skills_count": 0,
    "has_github": false,
    "has_portfolio": false,
    "has_linkedin": false
  }},

  "missing_sections": [],

  "overall_resume_strength": ""
}}

--------------------------------------------------
IMPORTANT RULES
--------------------------------------------------

- Return ONLY JSON
- Do not include markdown
- Do not hallucinate
- Use empty arrays if missing
- Ensure valid JSON formatting

--------------------------------------------------
RESUME
--------------------------------------------------

{resume_text}

""",
        expected_output="Structured JSON containing extracted resume information.",
        agent=agent,
        async_execution=True
    )


def build_jd_task(jd_text, agent):
    return Task(
        description=f"""
Analyze the following job description carefully.

--------------------------------------------------
OBJECTIVE
--------------------------------------------------

Extract:
- Role information
- Required skills
- Preferred skills
- Responsibilities
- Experience requirements
- Education requirements
- ATS keywords
- Tools & technologies
- Soft skills
- Role category
- Seniority level
- Work mode
- Location
- Salary/Stipend if available

--------------------------------------------------
INSTRUCTIONS
--------------------------------------------------

1. Identify the exact job role.

2. Extract technical skills separately.

3. Extract AI/ML skills separately if present.

4. Extract tools/platforms separately.

5. Extract soft skills separately.

6. Extract:
- mandatory requirements
- optional/preferred requirements

7. Detect ATS keywords from the JD.

8. Predict experience level:
- fresher
- junior
- mid-level
- senior

9. Detect work type:
- remote
- hybrid
- onsite

10. Detect role category:
- AI/ML
- Backend
- Frontend
- Full Stack
- Data Science
- DevOps
etc.

--------------------------------------------------
OUTPUT FORMAT
--------------------------------------------------

Return ONLY valid JSON.

JSON Structure:

{{
  "job_information": {{
    "job_title": "",
    "company_name": "",
    "location": "",
    "work_mode": "",
    "employment_type": "",
    "experience_level": "",
    "salary_or_stipend": ""
  }},

  "role_category": "",

  "required_skills": {{
    "technical_skills": [],
    "ai_ml_skills": [],
    "tools_platforms": [],
    "soft_skills": []
  }},

  "preferred_skills": [],

  "responsibilities": [],

  "education_requirements": [],

  "experience_requirements": [],

  "ats_keywords": [],

  "technologies_mentioned": [],

  "important_tools": [],

  "important_frameworks": [],

  "role_expectations": [],

  "application_deadline": "",

  "job_links": [],

  "overall_job_complexity": "",

  "candidate_suitability": {{
    "best_for": [],
    "not_ideal_for": []
  }}
}}

--------------------------------------------------
IMPORTANT RULES
--------------------------------------------------

- Return ONLY JSON
- Do not include markdown
- Do not hallucinate
- Use empty arrays if data missing
- Ensure valid JSON
- Extract only factual information from JD
- Normalize duplicate skills

--------------------------------------------------
JOB DESCRIPTION
--------------------------------------------------

{jd_text}

""",
        expected_output="Structured JSON containing complete job description analysis.",
        agent=agent,
        async_execution=True
    )


def build_analysis_task(agent, resume_task, jd_task):
    return Task(
        description="""
Analyze the parsed resume data and parsed job description data.

--------------------------------------------------
OBJECTIVE
--------------------------------------------------

Compare:
- skills
- projects
- experience
- technologies
- education
- ATS keywords

Then generate:
- ATS score
- Job match percentage
- Skill gap analysis
- Candidate strengths
- Candidate weaknesses
- Hiring recommendation
- Interview readiness
- Resume improvement suggestions

--------------------------------------------------
INSTRUCTIONS
--------------------------------------------------

1. Compare resume skills with required JD skills.

2. Detect:
- matched skills
- missing skills
- partially matched skills

3. Compare projects against JD requirements.

4. Evaluate candidate suitability for the role.

5. Generate ATS compatibility score out of 10.

6. Generate overall job match percentage.

7. Identify weak areas.

8. Identify strong areas.

9. Predict interview probability:
- low
- medium
- high

10. Recommend improvements for better matching.

11. Evaluate:
- project relevance
- technical depth
- experience quality

--------------------------------------------------
SCORING LOGIC
--------------------------------------------------

Consider:
- skill matching
- project relevance
- ATS keywords
- experience
- education
- technologies
- portfolio/GitHub presence

--------------------------------------------------
OUTPUT FORMAT
--------------------------------------------------

Return ONLY valid JSON.

JSON Structure:

{
  "scores": {
    "ats_score": 0,
    "job_match_percentage": 0,
    "technical_match_score": 0,
    "project_relevance_score": 0
  },

  "matched_skills": [],

  "missing_skills": [],

  "partially_matched_skills": [],

  "candidate_strengths": [],

  "candidate_weaknesses": [],

  "matching_projects": [],

  "irrelevant_projects": [],

  "experience_analysis": {
    "experience_relevance": "",
    "experience_level_fit": ""
  },

  "education_analysis": {
    "education_match": "",
    "degree_relevance": ""
  },

  "ats_analysis": {
    "keyword_match_quality": "",
    "missing_keywords": [],
    "resume_optimization_suggestions": []
  },

  "interview_probability": "",

  "hiring_recommendation": "",

  "improvement_recommendations": [],

  "final_decision": {
    "is_good_fit": false,
    "reasoning": ""
  }
}

--------------------------------------------------
IMPORTANT RULES
--------------------------------------------------

- Return ONLY valid JSON
- Do not include markdown
- Do not hallucinate
- Use only provided context
- Ensure proper JSON formatting
- Be unbiased and factual

""",
        expected_output="Structured JSON containing ATS analysis, job matching analysis, and candidate evaluation.",
        agent=agent,
        context=[resume_task, jd_task]
    )
