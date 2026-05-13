from crewai import Crew
from agent import build_resume_parser_agent, build_jd_agent, build_analysis_agent
from task import build_resume_task, build_jd_task, build_analysis_task
from text_content import resume_text, jd_text

resume_agent   = build_resume_parser_agent()
jd_agent       = build_jd_agent()
analysis_agent = build_analysis_agent()

resume_task   = build_resume_task(resume_text, resume_agent)
jd_task       = build_jd_task(jd_text, jd_agent)
analysis_task = build_analysis_task(analysis_agent, resume_task, jd_task)

crew = Crew(
    agents=[resume_agent, jd_agent, analysis_agent],
    tasks=[resume_task, jd_task, analysis_task],
    verbose=True
)

result = crew.kickoff()
print(result)
