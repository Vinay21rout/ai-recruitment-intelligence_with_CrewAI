import streamlit as st
import requests
import json
import time
import threading

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="Job Automation Multi-Agent System", page_icon="🤖", layout="wide")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
.agent-card { background:linear-gradient(135deg,#1e1e2e,#2a2a3e); border-radius:14px; padding:20px; color:white; transition:all 0.4s ease; }
.agent-card.idle   { border:1px solid #444; opacity:0.6; }
.agent-card.active { border:2px solid #00d4ff; box-shadow:0 0 20px rgba(0,212,255,0.4); }
.agent-card.done   { border:2px solid #00ff88; box-shadow:0 0 15px rgba(0,255,136,0.3); }
.badge { display:inline-block; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:bold; }
.badge-idle   { background:#444; color:#aaa; }
.badge-active { background:#00d4ff; color:#000; animation:pulse 1.2s infinite; }
.badge-done   { background:#00ff88; color:#000; }
.workflow-box { background:#12122a; border:1px solid #333; border-radius:12px; padding:16px 20px; margin:10px 0; color:#ccc; font-size:0.88rem; }
.score-box { background:linear-gradient(135deg,#0f3460,#16213e); border:1px solid #00d4ff; border-radius:10px; padding:18px; text-align:center; color:white; }
.score-number { font-size:2.4rem; font-weight:bold; color:#00d4ff; }
.metric-label { font-size:0.82rem; color:#aaa; margin-top:4px; }
.skill-tag   { display:inline-block; background:#1a3a2a; border:1px solid #00ff88; color:#00ff88; padding:3px 10px; border-radius:20px; font-size:12px; margin:3px; }
.missing-tag { display:inline-block; background:#3a1a1a; border:1px solid #ff4444; color:#ff4444; padding:3px 10px; border-radius:20px; font-size:12px; margin:3px; }
.partial-tag { display:inline-block; background:#3a2a1a; border:1px solid #ffaa00; color:#ffaa00; padding:3px 10px; border-radius:20px; font-size:12px; margin:3px; }
.rec-box  { background:#0d2a1a; border-left:4px solid #00ff88; padding:12px 16px; border-radius:0 8px 8px 0; color:#ccc; margin:6px 0; }
.warn-box { background:#2a1a0d; border-left:4px solid #ffaa00; padding:12px 16px; border-radius:0 8px 8px 0; color:#ccc; margin:6px 0; }
.sec-hdr  { font-size:1.05rem; font-weight:bold; color:#00d4ff; border-bottom:1px solid #333; padding-bottom:6px; margin-bottom:12px; }
.log-line         { font-family:monospace; font-size:0.82rem; color:#aaa; padding:2px 0; }
.log-line.info    { color:#00d4ff; }
.log-line.success { color:#00ff88; }
.log-line.warn    { color:#ffaa00; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 🤖 Job Automation Multi-Agent System")
st.caption("AI-powered Resume × JD Analysis — Parallel + Sequential CrewAI Pipeline via FastAPI")
st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📄 Inputs")
    resume_input = st.text_area("Resume Text", height=260, placeholder="Paste resume here...")
    jd_input     = st.text_area("Job Description", height=260, placeholder="Paste JD here...")
    st.divider()
    st.markdown("### ⚙️ Settings")
    show_raw = st.checkbox("Show Raw JSON", value=False)
    st.divider()

    # API health check
    try:
        r = requests.get(f"{API_BASE}/health", timeout=2)
        if r.status_code == 200:
            st.success("🟢 FastAPI Server Online")
        else:
            st.error("🔴 FastAPI Server Error")
    except Exception:
        st.error("🔴 FastAPI Server Offline\nRun: `uvicorn fastapi.main:app --reload`")

    run_btn = st.button("🚀 Run Agents", use_container_width=True, type="primary")

# ── Workflow Diagram ──────────────────────────────────────────────────────────
st.markdown("### 🔄 Workflow Architecture")
st.markdown("""
<div class="workflow-box">
    <div style="text-align:center;font-size:0.75rem;color:#00d4ff;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px">⚡ Phase 1 — Parallel Execution</div>
    <div style="display:flex;gap:12px;justify-content:center;margin:8px 0;">
        <div style="flex:1;background:#1a1a2e;border:1px solid #00d4ff;border-radius:8px;padding:10px;text-align:center;">
            📄 <b>Resume Parser</b><br><span style="font-size:0.75rem;color:#aaa">POST /parse-resume</span>
        </div>
        <div style="display:flex;align-items:center;color:#555;font-size:1.2rem;">⚡</div>
        <div style="flex:1;background:#1a1a2e;border:1px solid #00d4ff;border-radius:8px;padding:10px;text-align:center;">
            📋 <b>JD Analyzer</b><br><span style="font-size:0.75rem;color:#aaa">POST /analyze-jd</span>
        </div>
    </div>
    <div style="text-align:center;font-size:1.4rem;color:#555;margin:4px 0;">↓</div>
    <div style="text-align:center;font-size:0.75rem;color:#ffaa00;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px">🔗 Phase 2 — Sequential</div>
    <div style="background:#1a1a2e;border:1px solid #ffaa00;border-radius:8px;padding:10px;text-align:center;margin-bottom:8px;">
        🔍 <b>Matching Analyzer</b><br><span style="font-size:0.75rem;color:#aaa">POST /analyze-match</span>
    </div>
    <div style="text-align:center;font-size:1.4rem;color:#555;margin:4px 0;">↓</div>
    <div style="text-align:center;font-size:0.75rem;color:#ff88cc;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px">📧 Phase 3 — Sequential</div>
    <div style="background:#1a1a2e;border:1px solid #ff88cc;border-radius:8px;padding:10px;text-align:center;">
        ✉️ <b>Email Writer</b><br><span style="font-size:0.75rem;color:#aaa">POST /write-email</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Agent Cards ───────────────────────────────────────────────────────────────
st.markdown("### 🧠 Agent Status")
pipeline_ph = st.empty()

def render_pipeline(s1, s2, s3, s4, t1="", t2="", t3="", t4=""):
    badge = lambda s: f'<span class="badge badge-{s}">{"⏳ Idle" if s=="idle" else "⚡ Running" if s=="active" else "✅ Done"}</span>'
    def card(icon, title, endpoint, desc, s, timing):
        t = f'<div style="font-size:0.75rem;color:#888;margin-top:6px;">⏱ {timing}</div>' if timing else ""
        return f"""<div class="agent-card {s}">
            <div style="font-size:1.8rem">{icon}</div>
            <div style="font-size:1rem;font-weight:bold;margin:6px 0 2px">{title}</div>
            <div style="color:#555;font-size:0.75rem;margin-bottom:6px;font-family:monospace">{endpoint}</div>
            <div style="color:#bbb;font-size:0.8rem;margin-bottom:10px">{desc}</div>
            {badge(s)}{t}</div>"""
    with pipeline_ph.container():
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(card("📄","Resume Parser Agent","POST /parse-resume",
                "Extracts skills, projects, experience & ATS keywords from resume.",s1,t1), unsafe_allow_html=True)
        with c2:
            st.markdown(card("📋","JD Analysis Agent","POST /analyze-jd",
                "Extracts required skills, responsibilities & ATS keywords from JD.",s2,t2), unsafe_allow_html=True)
        with c3:
            st.markdown(card("🔍","Matching Analysis Agent","POST /analyze-match",
                "Compares resume vs JD — ATS score, match %, skill gaps & hiring decision.",s3,t3), unsafe_allow_html=True)
        with c4:
            st.markdown(card("✉️","Email Writer Agent","POST /write-email",
                "Writes professional HR email based on match score — shortlist, hold, or rejection.",s4,t4), unsafe_allow_html=True)

render_pipeline("idle","idle","idle","idle")

# ── Live Log ──────────────────────────────────────────────────────────────────
st.divider()
st.markdown("### 📟 Live Agent Log")
log_ph = st.empty()
_logs  = []

def log(msg, kind="info"):
    ts = time.strftime("%H:%M:%S")
    _logs.append(f'<div class="log-line {kind}">[{ts}] {msg}</div>')
    log_ph.markdown("".join(_logs[-15:]), unsafe_allow_html=True)

# ── Run ───────────────────────────────────────────────────────────────────────
if run_btn:
    if not resume_input.strip() or not jd_input.strip():
        st.error("Please provide both Resume and Job Description.")
        st.stop()

    _logs.clear()
    api_results = {}
    api_errors  = {}

    # ── Phase 1: Parallel API calls ───────────────────────────────────────────
    log("🚀 Phase 1 — Calling /parse-resume & /analyze-jd in parallel", "info")
    render_pipeline("active","active","idle","idle")

    t1_start = t2_start = time.time()

    def call_resume():
        try:
            r = requests.post(f"{API_BASE}/parse-resume", json={"resume_text": resume_input}, timeout=180)
            r.raise_for_status()
            api_results["resume"] = r.json()["result"]
        except requests.HTTPError as e:
            detail = r.json().get("detail", {})
            api_errors["resume"] = f"[{detail.get('type','Error')}] {detail.get('error', str(e))}"
        except Exception as e:
            api_errors["resume"] = str(e)

    def call_jd():
        try:
            r = requests.post(f"{API_BASE}/analyze-jd", json={"jd_text": jd_input}, timeout=180)
            r.raise_for_status()
            api_results["jd"] = r.json()["result"]
        except requests.HTTPError as e:
            detail = r.json().get("detail", {})
            api_errors["jd"] = f"[{detail.get('type','Error')}] {detail.get('error', str(e))}"
        except Exception as e:
            api_errors["jd"] = str(e)

    t_r = threading.Thread(target=call_resume)
    t_j = threading.Thread(target=call_jd)
    t_r.start(); t_j.start()

    dots = 0
    while t_r.is_alive() or t_j.is_alive():
        dots = (dots + 1) % 4
        d = "." * dots
        s1 = "active" if t_r.is_alive() else "done"
        s2 = "active" if t_j.is_alive() else "done"
        render_pipeline(s1, s2, "idle","idle")
        if t_r.is_alive(): log(f"⚡ Resume Parser Agent working{d}", "info")
        if t_j.is_alive(): log(f"⚡ JD Analysis Agent working{d}", "info")
        time.sleep(2)

    t_r.join(); t_j.join()

    t1_elapsed = f"{time.time()-t1_start:.1f}s"
    t2_elapsed = f"{time.time()-t2_start:.1f}s"

    if "resume" in api_errors:
        log(f"❌ Resume Parser failed: {api_errors['resume']}", "warn"); st.stop()
    else:
        log("✅ Resume Parser Agent — DONE", "success")

    if "jd" in api_errors:
        log(f"❌ JD Analyzer failed: {api_errors['jd']}", "warn"); st.stop()
    else:
        log("✅ JD Analysis Agent — DONE", "success")

    render_pipeline("done","done","idle","idle", t1_elapsed, t2_elapsed)

    # ── Phase 2: Sequential — Matching ───────────────────────────────────────
    log("🔗 Phase 2 — Calling /analyze-match sequentially", "warn")
    render_pipeline("done","done","active","idle", t1_elapsed, t2_elapsed)

    t3_start = time.time()

    def call_match():
        try:
            r = requests.post(f"{API_BASE}/analyze-match", json={
                "resume_output": api_results["resume"],
                "jd_output":     api_results["jd"]
            }, timeout=180)
            r.raise_for_status()
            api_results["analysis"] = r.json()["result"]
        except requests.HTTPError as e:
            detail = r.json().get("detail", {})
            api_errors["analysis"] = f"[{detail.get('type','Error')}] {detail.get('error', str(e))}"
        except Exception as e:
            api_errors["analysis"] = str(e)

    t_m = threading.Thread(target=call_match)
    t_m.start()

    dots = 0
    while t_m.is_alive():
        dots = (dots + 1) % 4
        render_pipeline("done","done","active","idle", t1_elapsed, t2_elapsed)
        log(f"⚡ Matching Analysis Agent working{'.' * dots}", "info")
        time.sleep(2)

    t_m.join()
    t3_elapsed = f"{time.time()-t3_start:.1f}s"

    if "analysis" in api_errors:
        log(f"❌ Matching Agent failed: {api_errors['analysis']}", "warn"); st.stop()
    else:
        log("✅ Matching Analysis Agent — DONE", "success")

    render_pipeline("done","done","done","idle", t1_elapsed, t2_elapsed, t3_elapsed)

    # ── Phase 3: Sequential — Email Writer ───────────────────────────────────
    log("📧 Phase 3 — Calling /write-email sequentially", "warn")
    render_pipeline("done","done","done","active", t1_elapsed, t2_elapsed, t3_elapsed)

    t4_start = time.time()

    def call_email():
        try:
            r = requests.post(f"{API_BASE}/write-email", json={
                "analysis_output": api_results["analysis"]
            }, timeout=180)
            r.raise_for_status()
            api_results["email"] = r.json()["result"]
        except requests.HTTPError as e:
            detail = r.json().get("detail", {})
            api_errors["email"] = f"[{detail.get('type','Error')}] {detail.get('error', str(e))}"
        except Exception as e:
            api_errors["email"] = str(e)

    t_e = threading.Thread(target=call_email)
    t_e.start()

    dots = 0
    while t_e.is_alive():
        dots = (dots + 1) % 4
        render_pipeline("done","done","done","active", t1_elapsed, t2_elapsed, t3_elapsed)
        log(f"⚡ Email Writer Agent working{'.' * dots}", "info")
        time.sleep(2)

    t_e.join()
    t4_elapsed = f"{time.time()-t4_start:.1f}s"

    if "email" in api_errors:
        log(f"❌ Email Writer failed: {api_errors['email']}", "warn"); st.stop()
    else:
        log("✅ Email Writer Agent — DONE", "success")

    render_pipeline("done","done","done","done", t1_elapsed, t2_elapsed, t3_elapsed, t4_elapsed)
    log("🎉 All 4 agents completed! Rendering results...", "success")

    # ── Parse Result ──────────────────────────────────────────────────────────
    raw = api_results.get("analysis", "")
    try:
        # strip markdown code blocks if present
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        s = clean.find("{"); e = clean.rfind("}") + 1
        data = json.loads(clean[s:e])
    except Exception:
        data = None

    st.divider()
    st.markdown("## 📊 Analysis Results")

    if not data:
        st.warning("Could not parse JSON. Raw output:")
        st.text(raw)
        st.stop()

    scores = data.get("scores", {})
    ats    = scores.get("ats_score", 0)
    match  = scores.get("job_match_percentage", 0)
    tech   = scores.get("technical_match_score", 0)
    proj   = scores.get("project_relevance_score", 0)

    # Candidate info banner
    cinfo = data.get("candidate_info", {})
    if cinfo.get("full_name"):
        st.markdown(f"""
        <div style="background:#1a1a2e;border:1px solid #00d4ff;border-radius:10px;padding:12px 20px;margin-bottom:16px;color:#eee;">
        👤 <b>{cinfo.get('full_name','')}</b> &nbsp;|&nbsp;
        📧 {cinfo.get('email','')} &nbsp;|&nbsp;
        💼 {cinfo.get('applied_role','')}
        </div>""", unsafe_allow_html=True)

    # Score cards
    s1,s2,s3,s4 = st.columns(4)
    for col, val, label in [(s1,f"{ats}/10","ATS Score"),(s2,f"{match}%","Job Match"),
                             (s3,f"{tech}/10","Technical Match"),(s4,f"{proj}/10","Project Relevance")]:
        with col:
            st.markdown(f'<div class="score-box"><div class="score-number">{val}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    prob  = data.get("interview_probability","N/A")
    final = data.get("final_decision", {})
    fit   = final.get("is_good_fit", False)

    p1, p2 = st.columns(2)
    with p1:
        color = {"High":"#00ff88","Medium":"#ffaa00","Low":"#ff4444"}.get(prob,"#aaa")
        st.markdown(f'<div class="score-box"><div style="font-size:1.4rem;font-weight:bold;color:{color}">🎯 {prob}</div><div class="metric-label">Interview Probability</div></div>', unsafe_allow_html=True)
    with p2:
        fc = "#00ff88" if fit else "#ff4444"
        ft = "✅ Good Fit" if fit else "❌ Not a Fit"
        st.markdown(f'<div class="score-box"><div style="font-size:1.4rem;font-weight:bold;color:{fc}">{ft}</div><div class="metric-label">Final Decision</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Skills
    st.markdown('<div class="sec-hdr">🛠️ Skills Analysis</div>', unsafe_allow_html=True)
    sk1, sk2, sk3 = st.columns(3)
    with sk1:
        st.markdown("**✅ Matched Skills**")
        st.markdown(" ".join([f'<span class="skill-tag">{s}</span>' for s in data.get("matched_skills",[])]), unsafe_allow_html=True)
    with sk2:
        st.markdown("**❌ Missing Skills**")
        st.markdown(" ".join([f'<span class="missing-tag">{s}</span>' for s in data.get("missing_skills",[])]), unsafe_allow_html=True)
    with sk3:
        st.markdown("**⚠️ Partial Matches**")
        st.markdown(" ".join([f'<span class="partial-tag">{s}</span>' for s in data.get("partially_matched_skills",[])]), unsafe_allow_html=True)

    st.divider()

    sw1, sw2 = st.columns(2)
    with sw1:
        st.markdown("**💪 Strengths**")
        for s in data.get("candidate_strengths",[]):
            st.markdown(f'<div class="rec-box">✅ {s}</div>', unsafe_allow_html=True)
    with sw2:
        st.markdown("**⚠️ Weaknesses**")
        for w in data.get("candidate_weaknesses",[]):
            st.markdown(f'<div class="warn-box">⚠️ {w}</div>', unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="sec-hdr">🚀 Matching Projects</div>', unsafe_allow_html=True)
    for p in data.get("matching_projects",[]):
        st.markdown(f"- 🟢 **{p}**")

    st.divider()

    ats_a = data.get("ats_analysis", {})
    st.markdown('<div class="sec-hdr">🔎 ATS Analysis</div>', unsafe_allow_html=True)
    st.markdown(f"**Keyword Match Quality:** {ats_a.get('keyword_match_quality','N/A')}")
    missing_kw = ats_a.get("missing_keywords", [])
    if missing_kw:
        st.markdown("**Missing Keywords:** " + " ".join([f'<span class="missing-tag">{k}</span>' for k in missing_kw]), unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="sec-hdr">📈 Improvement Recommendations</div>', unsafe_allow_html=True)
    for r in data.get("improvement_recommendations",[]):
        st.markdown(f'<div class="rec-box">💡 {r}</div>', unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="sec-hdr">🧠 Final Reasoning</div>', unsafe_allow_html=True)
    st.info(final.get("reasoning","N/A"))
    st.markdown('<div class="sec-hdr">📌 Hiring Recommendation</div>', unsafe_allow_html=True)
    st.success(data.get("hiring_recommendation","N/A"))

    # ── Email Output ──────────────────────────────────────────────────────────────────
    st.divider()
    st.markdown('<div class="sec-hdr">✉️ Generated HR Email</div>', unsafe_allow_html=True)
    email_output = api_results.get("email", "")
    if email_output:
        st.markdown(f"""
        <div style="background:#12122a;border:1px solid #ff88cc;border-radius:12px;padding:20px;color:#eee;font-family:Georgia,serif;line-height:1.8;white-space:pre-wrap;">{email_output}</div>
        """, unsafe_allow_html=True)
        st.download_button("📥 Download Email", email_output, file_name="hr_email.txt", mime="text/plain")
    else:
        st.warning("Email output not available.")

    if show_raw:
        st.divider()
        st.markdown("**🗂️ Raw JSON**")
        st.json(data)
