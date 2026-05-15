from crewai import Task
from agent import build_resume_parser_agent, build_jd_agent, build_analysis_agent, build_email_writer_agent


def build_resume_task(resume_text, agent):
    return Task(
        description=f"""SYSTEM: You are an enterprise resume parsing engine. Your only job is to extract information from the resume text below and return it as a valid JSON object.

CRITICAL RULES — READ BEFORE PARSING:
1. Extract ONLY information that is EXPLICITLY written in the resume text below.
2. Do NOT infer, assume, or generate any information not present in the text.
3. Do NOT add skills, tools, or technologies that are not mentioned.
4. Do NOT paraphrase or embellish any content.
5. If a field has no data in the resume, use empty string "" or empty array [].
6. The full_name, email, and phone MUST be copied character-by-character from the resume text.
7. Return ONLY the JSON object. No explanation. No markdown. No ```json blocks.
8. Start your response with {{ and end with }}.

RESUME TEXT:
{resume_text}

OUTPUT — Return this exact JSON structure filled with data from the resume above:
{{
  "personal_information": {{
    "full_name": "<exact name from resume>",
    "email": "<exact email from resume>",
    "phone": "<exact phone from resume>",
    "location": "<exact location from resume>",
    "linkedin": "<exact linkedin url from resume or empty>",
    "github": "<exact github url from resume or empty>",
    "portfolio": "<exact portfolio url from resume or empty>"
  }},
  "professional_summary": "<exact objective/summary text from resume or empty>",
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
      "date": ""
    }}
  ],
  "achievements": [],
  "ats_keywords": [],
  "predicted_roles": [],
  "experience_level": "",
  "overall_resume_strength": ""
}}""",
        expected_output=(
            "A single valid JSON object starting with { and ending with }. "
            "All fields populated strictly from the resume text. "
            "personal_information.full_name must match the candidate name exactly as written in the resume. "
            "No markdown. No explanation. No code blocks."
        ),
        agent=agent,
        async_execution=True
    )


def build_jd_task(jd_text, agent):
    return Task(
        description=f"""SYSTEM: You are an enterprise job description parsing engine. Your only job is to extract hiring requirements from the JD text below and return a valid JSON object.

CRITICAL RULES — READ BEFORE PARSING:
1. Extract ONLY information that is EXPLICITLY written in the JD text below.
2. Do NOT infer industry norms or assume hidden requirements.
3. Clearly separate mandatory skills from preferred/optional skills.
4. Do NOT add requirements that are not written in the JD.
5. If a field has no data in the JD, use empty string "" or empty array [].
6. Return ONLY the JSON object. No explanation. No markdown. No ```json blocks.
7. Start your response with {{ and end with }}.

JOB DESCRIPTION TEXT:
{jd_text}

OUTPUT — Return this exact JSON structure filled with data from the JD above:
{{
  "job_information": {{
    "job_title": "<exact job title from JD>",
    "company_name": "<exact company name from JD or empty>",
    "location": "<exact location from JD or empty>",
    "work_mode": "<remote/hybrid/onsite — only if explicitly stated>",
    "employment_type": "<internship/full-time/part-time — only if stated>",
    "experience_level": "<fresher/junior/mid/senior — only if stated>",
    "salary_or_stipend": "<exact salary/stipend from JD or empty>"
  }},
  "role_category": "",
  "mandatory_skills": {{
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
  "overall_job_complexity": "",
  "candidate_suitability": {{
    "best_for": [],
    "not_ideal_for": []
  }}
}}""",
        expected_output=(
            "A single valid JSON object starting with { and ending with }. "
            "All fields populated strictly from the JD text. "
            "mandatory_skills and preferred_skills must be clearly separated. "
            "No markdown. No explanation. No code blocks."
        ),
        async_execution=True,
        agent=agent
    )


def build_analysis_task(agent, resume_task, jd_task):
    return Task(
        description="""SYSTEM: You are an enterprise recruitment intelligence analyst. You will receive two inputs via context:
1. RESUME DATA — parsed JSON output from the resume parser agent.
2. JD DATA — parsed JSON output from the JD parser agent.

Your job is to compare them and return a strict, evidence-based recruitment analysis as a valid JSON object.

CRITICAL RULES — READ BEFORE ANALYZING:
1. Compare ONLY what is present in the resume data against what is required in the JD data.
2. Do NOT assume the candidate has any skill not listed in resume data.
3. Do NOT inflate scores. Be strict and realistic.
4. candidate_info MUST be copied VERBATIM from resume data personal_information field:
   - full_name = resume_data.personal_information.full_name
   - email = resume_data.personal_information.email
   - phone = resume_data.personal_information.phone
   - applied_role = jd_data.job_information.job_title
5. Do NOT generate or guess candidate_info values.
6. Missing mandatory skills MUST reduce scores significantly.
7. Academic/personal projects are weighted lower than professional experience.
8. Return ONLY the JSON object. No explanation. No markdown. No ```json blocks.
9. Start your response with { and end with }.

SCORING METHODOLOGY:
- ats_score (0-10): keyword overlap between resume ats_keywords and JD ats_keywords
- job_match_percentage (0-100): weighted score — mandatory skills 50%, projects 25%, experience 15%, education 10%
- technical_match_score (0-10): technical_skills + ai_ml_skills + tools match against JD mandatory_skills
- project_relevance_score (0-10): how directly candidate projects relate to JD responsibilities

SCORE THRESHOLDS:
- 80-100: Strong shortlist — meets 80%+ mandatory requirements
- 60-79: Hold/review — meets 60-79% mandatory requirements
- 40-59: Weak match — significant gaps in mandatory requirements
- 0-39: Reject — does not meet core requirements

OUTPUT — Return this exact JSON structure:
{
  "candidate_info": {
    "full_name": "<VERBATIM from resume personal_information.full_name>",
    "email": "<VERBATIM from resume personal_information.email>",
    "phone": "<VERBATIM from resume personal_information.phone>",
    "applied_role": "<VERBATIM from jd job_information.job_title>"
  },
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
}""",
        expected_output=(
            "A single valid JSON object starting with { and ending with }. "
            "candidate_info.full_name must exactly match the name from resume parser output. "
            "Scores must be realistic and evidence-based. "
            "No markdown. No explanation. No code blocks."
        ),
        agent=agent,
        context=[resume_task, jd_task]
    )


def build_email_writer_task(agent, analysis_output):
    return Task(
        description=f"""SYSTEM: You are an enterprise HR communication specialist. You will receive a recruitment analysis report below. Your job is to write one professional HR email to the candidate.

RECRUITMENT ANALYSIS REPORT:
{analysis_output}

CRITICAL RULES — READ BEFORE WRITING:
1. Extract candidate name from candidate_info.full_name in the report above.
2. Extract applied role from candidate_info.applied_role in the report above.
3. Extract score from scores.job_match_percentage in the report above.
4. Extract 2-3 strengths from candidate_strengths in the report above.
5. Do NOT use any placeholder like [Name], [Role], [Company], [Date] — use actual values only.
6. Do NOT fabricate interview dates, HR contact details, or next steps not in the report.
7. Do NOT exaggerate strengths beyond what the report states.
8. Do NOT make false promises about future opportunities.
9. Write ONLY the email. No explanation. No JSON. No preamble.

EMAIL TYPE BASED ON SCORE:
- job_match_percentage >= 80:
  Subject: Congratulations! You have been shortlisted — [applied_role]
  Content: Warm congratulations, mention 2-3 specific strengths from report, invite for next round, mention company is excited to move forward.

- job_match_percentage 60-79:
  Subject: Application Update — [applied_role]
  Content: Thank candidate for applying, inform profile is under review, mention 1-2 genuine strengths, state decision will be communicated soon, avoid false promises.

- job_match_percentage < 60:
  Subject: Application Status — [applied_role]
  Content: Thank candidate sincerely, respectfully inform they are not moving forward, mention 1 genuine strength, provide 1-2 specific improvement suggestions from report, encourage to apply again in future.

TONE: Professional. Human. Concise. Respectful. No robotic language. No corporate jargon overload.""",
        expected_output=(
            "A complete, professional HR email with real candidate name and role from the report. "
            "No placeholders. No JSON. No markdown headers. Just the email text."
        ),
        agent=agent
    )
