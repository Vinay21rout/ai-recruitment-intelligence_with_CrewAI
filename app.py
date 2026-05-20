import streamlit as st
import requests
import json
import time
import threading

API_BASE = "http://localhost:8000"

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RecruitIQ · AI Recruitment Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background: #080c14 !important;
    color: #e2e8f4 !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 3rem !important; max-width: 1400px; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: #0b1020 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
    width: 340px !important;
}
section[data-testid="stSidebar"] > div { padding: 1.5rem 1.25rem; }

/* ── HEADER BAND ── */
.header-band {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.1rem 1.6rem;
    background: #0b1020;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    margin-bottom: 1.5rem;
}
.header-logo {
    display: flex;
    align-items: center;
    gap: 12px;
}
.logo-icon {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, #4f7eff, #8b5cf6);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
}
.header-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #e2e8f4;
    letter-spacing: -0.3px;
}
.header-subtitle {
    font-size: 0.72rem;
    color: #5a6a8a;
    margin-top: 1px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.header-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    padding: 5px 12px;
    border-radius: 20px;
    background: rgba(79,126,255,0.1);
    border: 1px solid rgba(79,126,255,0.25);
    color: #4f7eff;
    letter-spacing: 0.3px;
}

/* ── PIPELINE RAIL ── */
.pipeline-rail {
    display: flex;
    align-items: stretch;
    gap: 0;
    background: #0b1020;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    overflow: hidden;
    margin-bottom: 1.5rem;
}
.pipeline-step {
    flex: 1;
    padding: 1.1rem 1.2rem;
    position: relative;
    transition: background 0.3s;
    border-right: 1px solid rgba(255,255,255,0.05);
}
.pipeline-step:last-child { border-right: none; }
.pipeline-step.idle { background: transparent; }
.pipeline-step.active { background: rgba(79,126,255,0.07); }
.pipeline-step.done { background: rgba(34,197,139,0.06); }

.step-connector {
    position: absolute; right: -1px; top: 50%;
    transform: translateY(-50%);
    width: 0; height: 0;
    border-top: 8px solid transparent;
    border-bottom: 8px solid transparent;
    border-left: 8px solid #0b1020;
    z-index: 2;
}
.step-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: #3a4560;
    margin-bottom: 6px;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.step-icon { font-size: 1.3rem; margin-bottom: 6px; }
.step-title {
    font-size: 0.8rem;
    font-weight: 600;
    color: #c8d4f0;
    margin-bottom: 3px;
}
.step-desc {
    font-size: 0.68rem;
    color: #4a5878;
    line-height: 1.4;
}
.step-status {
    margin-top: 10px;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    padding: 3px 9px;
    border-radius: 20px;
}
.status-idle   { background: rgba(255,255,255,0.04); color: #3a4560; border: 1px solid rgba(255,255,255,0.06); }
.status-active { background: rgba(79,126,255,0.15); color: #4f7eff; border: 1px solid rgba(79,126,255,0.3); animation: pulse-blue 1.2s infinite; }
.status-done   { background: rgba(34,197,139,0.12); color: #22c58b; border: 1px solid rgba(34,197,139,0.3); }

@keyframes pulse-blue {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.55; }
}

/* ── SCORE CARDS ── */
.score-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 1.25rem;
}
.score-card {
    background: #0b1020;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 1.2rem 1.1rem;
    position: relative;
    overflow: hidden;
}
.score-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.score-card.blue::before   { background: linear-gradient(90deg, #4f7eff, #8b5cf6); }
.score-card.green::before  { background: linear-gradient(90deg, #22d38a, #16a372); }
.score-card.purple::before { background: linear-gradient(90deg, #8b5cf6, #ec4899); }
.score-card.amber::before  { background: linear-gradient(90deg, #f59e0b, #ef4444); }

.score-label {
    font-size: 0.68rem;
    font-weight: 600;
    color: #4a5878;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 8px;
}
.score-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2rem;
    font-weight: 500;
    line-height: 1;
    margin-bottom: 6px;
}
.score-card.blue   .score-value { color: #4f7eff; }
.score-card.green  .score-value { color: #22d38a; }
.score-card.purple .score-value { color: #a78bfa; }
.score-card.amber  .score-value { color: #f59e0b; }

.score-bar-track {
    height: 3px;
    background: rgba(255,255,255,0.06);
    border-radius: 2px;
    margin-top: 8px;
}
.score-bar-fill {
    height: 100%;
    border-radius: 2px;
    transition: width 1s ease;
}
.score-card.blue   .score-bar-fill { background: linear-gradient(90deg, #4f7eff, #8b5cf6); }
.score-card.green  .score-bar-fill { background: linear-gradient(90deg, #22d38a, #16a372); }
.score-card.purple .score-bar-fill { background: linear-gradient(90deg, #8b5cf6, #ec4899); }
.score-card.amber  .score-bar-fill { background: linear-gradient(90deg, #f59e0b, #ef4444); }

/* ── VERDICT CARD ── */
.verdict-card {
    border-radius: 14px;
    padding: 1.1rem 1.4rem;
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 1.25rem;
}
.verdict-card.pass {
    background: rgba(34,197,139,0.08);
    border: 1px solid rgba(34,197,139,0.22);
}
.verdict-card.fail {
    background: rgba(255,77,106,0.08);
    border: 1px solid rgba(255,77,106,0.22);
}
.verdict-icon { font-size: 1.6rem; }
.verdict-text-main {
    font-size: 0.95rem;
    font-weight: 600;
}
.verdict-card.pass .verdict-text-main { color: #22d38a; }
.verdict-card.fail .verdict-text-main { color: #ff4d6a; }
.verdict-text-sub {
    font-size: 0.75rem;
    color: #4a5878;
    margin-top: 2px;
}

/* ── SECTION HEADERS ── */
.section-hd {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #3a4560;
    margin: 1.5rem 0 0.75rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-hd::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.05);
}

/* ── SKILL TAGS ── */
.tag-row { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 0.5rem; }
.tag {
    font-size: 0.7rem;
    font-weight: 500;
    padding: 4px 11px;
    border-radius: 20px;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.2px;
}
.tag-match   { background: rgba(34,197,139,0.1); border: 1px solid rgba(34,197,139,0.28); color: #22d38a; }
.tag-missing { background: rgba(255,77,106,0.1); border: 1px solid rgba(255,77,106,0.28); color: #ff4d6a; }
.tag-partial { background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.28); color: #f59e0b; }

/* ── INSIGHT ROWS ── */
.insight-row {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 10px 12px;
    background: #0b1020;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 10px;
    margin-bottom: 7px;
    font-size: 0.8rem;
    color: #9aaac0;
    line-height: 1.5;
}
.insight-row .dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    flex-shrink: 0;
    margin-top: 5px;
}
.dot-green  { background: #22d38a; }
.dot-red    { background: #ff4d6a; }
.dot-amber  { background: #f59e0b; }
.dot-blue   { background: #4f7eff; }

/* ── LOG BOX ── */
.log-wrapper {
    background: #070b12;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 12px 14px;
    max-height: 220px;
    overflow-y: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    line-height: 1.7;
    color: #4a5878;
}
.log-wrapper .log-ts { color: #2a3450; margin-right: 8px; }
.log-wrapper .log-ok  { color: #22d38a; }
.log-wrapper .log-run { color: #4f7eff; }
.log-wrapper .log-info{ color: #9aaac0; }

/* ── EMAIL PANEL ── */
.email-panel {
    background: #070b12;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    overflow: hidden;
}
.email-topbar {
    background: #0b1020;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    padding: 10px 16px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.72rem;
    color: #4a5878;
}
.dot-r { width: 10px; height: 10px; border-radius: 50%; background: #ff5f57; }
.dot-y { width: 10px; height: 10px; border-radius: 50%; background: #febc2e; }
.dot-g { width: 10px; height: 10px; border-radius: 50%; background: #28c840; }
.email-body {
    padding: 20px 22px;
    font-size: 0.82rem;
    line-height: 1.9;
    color: #9aaac0;
    white-space: pre-wrap;
    font-family: 'Inter', sans-serif;
}

/* ── SIDEBAR ELEMENTS ── */
.sidebar-label {
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #3a4560;
    margin-bottom: 6px;
}
.sidebar-status {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 0.76rem;
    margin-bottom: 1rem;
}
.sidebar-status.online  { background: rgba(34,197,139,0.08); border: 1px solid rgba(34,197,139,0.2); color: #22d38a; }
.sidebar-status.offline { background: rgba(255,77,106,0.08); border: 1px solid rgba(255,77,106,0.2); color: #ff4d6a; }
.status-dot-sm { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.online  .status-dot-sm { background: #22d38a; box-shadow: 0 0 6px #22d38a80; }
.offline .status-dot-sm { background: #ff4d6a; }

/* Streamlit element overrides */
.stTextArea textarea {
    background: #0b1020 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    color: #c8d4f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
    resize: vertical !important;
}
.stTextArea textarea:focus {
    border-color: rgba(79,126,255,0.4) !important;
    box-shadow: 0 0 0 3px rgba(79,126,255,0.1) !important;
}
.stTextArea label, .stCheckbox label {
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.7px !important;
    color: #3a4560 !important;
}
.stButton > button {
    background: linear-gradient(135deg, #4f7eff, #7c5cf6) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.3px !important;
    padding: 0.6rem 1rem !important;
    transition: opacity 0.2s, transform 0.1s !important;
}
.stButton > button:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }
.stButton > button:active { transform: translateY(0) !important; }
.stDownloadButton > button {
    background: #0b1020 !important;
    color: #4f7eff !important;
    border: 1px solid rgba(79,126,255,0.3) !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-size: 0.78rem !important;
}
.stProgress > div > div { background: linear-gradient(90deg,#4f7eff,#7c5cf6) !important; border-radius: 4px !important; }
.stProgress > div { background: #0b1020 !important; border-radius: 4px !important; }
div[data-testid="stTabs"] button {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    color: #4a5878 !important;
    letter-spacing: 0.3px !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #e2e8f4 !important;
    border-bottom-color: #4f7eff !important;
}
.stAlert { border-radius: 10px !important; }
.stCheckbox > label { color: #9aaac0 !important; font-size: 0.8rem !important; text-transform: none !important; letter-spacing: 0 !important; }

/* Dividers */
hr { border-color: rgba(255,255,255,0.06) !important; margin: 1rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def pipeline_html(statuses):
    steps = [
        ("01", "📄", "Resume Parser", "Skills · ATS keywords · Projects · Experience", statuses[0]),
        ("02", "📋", "JD Analyzer",   "Role requirements · Responsibilities · Stack",  statuses[1]),
        ("03", "🔍", "Match Analyzer","Profile vs requirements · Gap analysis",         statuses[2]),
        ("04", "✉️",  "Email Writer",  "Auto-generates professional HR response",        statuses[3]),
    ]
    html = '<div class="pipeline-rail">'
    for num, icon, title, desc, status in steps:
        dot = {"idle": "·", "active": "▶", "done": "✓"}[status]
        html += f"""
        <div class="pipeline-step {status}">
            <div class="step-num">AGENT {num}</div>
            <div class="step-icon">{icon}</div>
            <div class="step-title">{title}</div>
            <div class="step-desc">{desc}</div>
            <div class="step-status status-{status}">{dot} {status.upper()}</div>
        </div>"""
    html += '</div>'
    return html

def score_cards_html(ats, match, tech, proj):
    def pct_of_10(v): return int(v * 10)
    def pct(v): return int(v)

    cards = [
        ("blue",   "ATS Score",         f"{ats}/10",   pct_of_10(ats)),
        ("green",  "Job Match",          f"{match}%",   pct(match)),
        ("purple", "Technical Fit",      f"{tech}/10",  pct_of_10(tech)),
        ("amber",  "Project Relevance",  f"{proj}/10",  pct_of_10(proj)),
    ]
    html = '<div class="score-grid">'
    for color, label, value, bar_pct in cards:
        html += f"""
        <div class="score-card {color}">
            <div class="score-label">{label}</div>
            <div class="score-value">{value}</div>
            <div class="score-bar-track">
                <div class="score-bar-fill" style="width:{bar_pct}%"></div>
            </div>
        </div>"""
    html += '</div>'
    return html

def verdict_html(is_fit):
    if is_fit:
        return '<div class="verdict-card pass"><div class="verdict-icon">🎯</div><div><div class="verdict-text-main">Recommended for Interview</div><div class="verdict-text-sub">Candidate meets the job requirements threshold.</div></div></div>'
    return '<div class="verdict-card fail"><div class="verdict-icon">⛔</div><div><div class="verdict-text-main">Not Recommended at This Time</div><div class="verdict-text-sub">Significant skill gaps identified against requirements.</div></div></div>'

def tag_html(items, tag_class):
    if not items:
        return '<span style="font-size:0.72rem;color:#3a4560;font-style:italic;">None detected</span>'
    return '<div class="tag-row">' + ''.join(f'<span class="tag {tag_class}">{s}</span>' for s in items) + '</div>'

def insight_rows(items, dot_class, empty_msg="None listed."):
    if not items:
        return f'<div style="font-size:0.78rem;color:#3a4560;font-style:italic;padding:8px 0;">{empty_msg}</div>'
    return ''.join(f'<div class="insight-row"><div class="dot {dot_class}"></div><div>{item}</div></div>' for item in items)

def log_html(log_lines):
    inner = ""
    for line in log_lines[-20:]:
        ts, msg = line[:10], line[10:]
        if "✅" in msg:
            inner += f'<div><span class="log-ts">{ts}</span><span class="log-ok">{msg}</span></div>'
        elif "⚡" in msg or "🔍" in msg or "✉️" in msg:
            inner += f'<div><span class="log-ts">{ts}</span><span class="log-run">{msg}</span></div>'
        else:
            inner += f'<div><span class="log-ts">{ts}</span><span class="log-info">{msg}</span></div>'
    return f'<div class="log-wrapper">{inner}</div>'

def email_html(text):
    return f"""
    <div class="email-panel">
        <div class="email-topbar">
            <div class="dot-r"></div><div class="dot-y"></div><div class="dot-g"></div>
            <span style="margin-left:8px;">AI-Generated HR Response</span>
        </div>
        <div class="email-body">{text}</div>
    </div>"""

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-band">
    <div class="header-logo">
        <div class="logo-icon">⚡</div>
        <div>
            <div class="header-title">RecruitIQ</div>
            <div class="header-subtitle">AI Recruitment Intelligence Platform</div>
        </div>
    </div>
    <div style="display:flex;gap:10px;align-items:center;">
        <div class="header-badge">Multi-Agent Pipeline</div>
        <div class="header-badge">v2.0</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-label">Backend Status</div>', unsafe_allow_html=True)
    try:
        r = requests.get(f"{API_BASE}/health", timeout=2)
        if r.status_code == 200:
            st.markdown('<div class="sidebar-status online"><div class="status-dot-sm"></div>FastAPI Server · Online</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="sidebar-status offline"><div class="status-dot-sm"></div>Server Error</div>', unsafe_allow_html=True)
    except:
        st.markdown('<div class="sidebar-status offline"><div class="status-dot-sm"></div>Backend Offline</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label" style="margin-top:1rem;">Resume Text</div>', unsafe_allow_html=True)
    resume_input = st.text_area("Resume", height=240, placeholder="Paste candidate resume here…", label_visibility="collapsed")

    st.markdown('<div class="sidebar-label" style="margin-top:0.75rem;">Job Description</div>', unsafe_allow_html=True)
    jd_input = st.text_area("JD", height=240, placeholder="Paste job description here…", label_visibility="collapsed")

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        show_raw = st.checkbox("Raw JSON", value=False)
    with col_b:
        verbose_logs = st.checkbox("Verbose Logs", value=False)

    st.divider()
    run_btn = st.button("⚡  Run AI Pipeline", use_container_width=True, type="primary")

    # Tip box
    st.markdown("""
    <div style="margin-top:1rem;padding:12px;background:#0b1020;border:1px solid rgba(255,255,255,0.06);border-radius:10px;">
        <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:#3a4560;margin-bottom:6px;">Pipeline Steps</div>
        <div style="font-size:0.72rem;color:#4a5878;line-height:1.8;">
            1 · Resume Parser<br>
            2 · JD Analyzer <span style="color:#2a3450;">(parallel)</span><br>
            3 · Match Analyzer<br>
            4 · HR Email Writer
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# PIPELINE STATUS (initial idle state)
# ─────────────────────────────────────────────────────────────
pipeline_ph = st.empty()
pipeline_ph.markdown(pipeline_html(["idle","idle","idle","idle"]), unsafe_allow_html=True)

st.divider()

# ─────────────────────────────────────────────────────────────
# LIVE LOGS
# ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-hd">Live Agent Logs</div>', unsafe_allow_html=True)
log_ph = st.empty()
log_ph.markdown(log_html(["[00:00:00] — Waiting for input…"]), unsafe_allow_html=True)
logs = []

def add_log(msg):
    ts = time.strftime("%H:%M:%S")
    logs.append(f"[{ts}] {msg}")
    log_ph.markdown(log_html(logs), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# EXECUTION
# ─────────────────────────────────────────────────────────────
if run_btn:
    if not resume_input.strip() or not jd_input.strip():
        st.error("⚠️  Please provide both a Resume and a Job Description before running.")
        st.stop()

    prog = st.progress(0)
    status_ph = st.empty()
    api_results = {}
    api_errors  = {}

    # ── PHASE 1: Resume + JD in parallel ──
    pipeline_ph.markdown(pipeline_html(["active","active","idle","idle"]), unsafe_allow_html=True)
    prog.progress(10)
    status_ph.info("⚡ Agents 01 & 02 running in parallel…")
    add_log("🚀 Pipeline started — launching parallel agents")

    def call_resume():
        try:
            r = requests.post(f"{API_BASE}/parse-resume", json={"resume_text": resume_input}, timeout=180)
            r.raise_for_status()
            api_results["resume"] = r.json()["result"]
            if verbose_logs: add_log("📄 Resume parser returned data")
        except Exception as e:
            api_errors["resume"] = str(e)
            add_log(f"❌ Resume parser error: {e}")

    def call_jd():
        try:
            r = requests.post(f"{API_BASE}/analyze-jd", json={"jd_text": jd_input}, timeout=180)
            r.raise_for_status()
            api_results["jd"] = r.json()["result"]
            if verbose_logs: add_log("📋 JD analyzer returned data")
        except Exception as e:
            api_errors["jd"] = str(e)
            add_log(f"❌ JD analyzer error: {e}")

    t1 = threading.Thread(target=call_resume)
    t2 = threading.Thread(target=call_jd)
    t1.start(); t2.start()
    tick = 0
    while t1.is_alive() or t2.is_alive():
        tick += 1
        add_log(f"⚡ Processing resume & JD… (tick {tick})")
        prog.progress(10 + min(tick * 3, 30))
        time.sleep(1.5)

    pipeline_ph.markdown(pipeline_html(["done","done","idle","idle"]), unsafe_allow_html=True)
    prog.progress(45)
    add_log("✅ Resume Parser + JD Analyzer complete")

    if api_errors:
        st.error(f"Agent error(s): {api_errors}")
        st.stop()

    # ── PHASE 2: Match Analyzer ──
    pipeline_ph.markdown(pipeline_html(["done","done","active","idle"]), unsafe_allow_html=True)
    status_ph.info("🔍 Agent 03 — running match analysis…")
    add_log("🔍 Launching Match Analyzer agent")

    def call_match():
        try:
            r = requests.post(
                f"{API_BASE}/analyze-match",
                json={"resume_output": api_results["resume"], "jd_output": api_results["jd"]},
                timeout=180
            )
            r.raise_for_status()
            api_results["analysis"] = r.json()["result"]
        except Exception as e:
            api_errors["analysis"] = str(e)
            add_log(f"❌ Match analyzer error: {e}")

    t3 = threading.Thread(target=call_match)
    t3.start()
    tick = 0
    while t3.is_alive():
        tick += 1
        add_log(f"🔍 Matching candidate profile… (tick {tick})")
        prog.progress(45 + min(tick * 4, 30))
        time.sleep(1.5)

    pipeline_ph.markdown(pipeline_html(["done","done","done","idle"]), unsafe_allow_html=True)
    prog.progress(80)
    add_log("✅ Match Analyzer complete")

    # ── PHASE 3: Email Writer ──
    pipeline_ph.markdown(pipeline_html(["done","done","done","active"]), unsafe_allow_html=True)
    status_ph.info("✉️ Agent 04 — writing HR email…")
    add_log("✉️ Launching Email Writer agent")

    def call_email():
        try:
            r = requests.post(f"{API_BASE}/write-email", json={"analysis_output": api_results["analysis"]}, timeout=180)
            r.raise_for_status()
            api_results["email"] = r.json()["result"]
        except Exception as e:
            api_errors["email"] = str(e)
            add_log(f"❌ Email writer error: {e}")

    t4 = threading.Thread(target=call_email)
    t4.start()
    tick = 0
    while t4.is_alive():
        tick += 1
        add_log(f"✉️ Writing HR response email… (tick {tick})")
        prog.progress(80 + min(tick * 2, 18))
        time.sleep(1.5)

    pipeline_ph.markdown(pipeline_html(["done","done","done","done"]), unsafe_allow_html=True)
    prog.progress(100)
    status_ph.success("🎉 All agents completed successfully!")
    add_log("✅ Pipeline finished — all 4 agents done")

    # ── PARSE ANALYSIS JSON ──
    raw = api_results.get("analysis", "")
    try:
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"): clean = clean[4:]
        start = clean.find("{"); end = clean.rfind("}") + 1
        data = json.loads(clean[start:end])
    except:
        data = None

    if not data:
        st.error("Failed to parse agent response. Check backend logs.")
        if show_raw:
            st.code(raw, language="text")
        st.stop()

    # ────────────────────────────────────────────────────────
    # RESULTS TABS
    # ────────────────────────────────────────────────────────
    st.divider()
    tab1, tab2, tab3, tab4 = st.tabs(["📊  Scores & Verdict", "🛠  Skills Analysis", "✉️  HR Email", "🗂  Raw JSON"])

    # ── TAB 1: SCORES ──
    with tab1:
        scores = data.get("scores", {})
        ats   = scores.get("ats_score", 0)
        match = scores.get("job_match_percentage", 0)
        tech  = scores.get("technical_match_score", 0)
        proj  = scores.get("project_relevance_score", 0)
        final = data.get("final_decision", {})

        st.markdown('<div class="section-hd">Candidate Score Summary</div>', unsafe_allow_html=True)
        st.markdown(score_cards_html(ats, match, tech, proj), unsafe_allow_html=True)

        st.markdown('<div class="section-hd">Hiring Verdict</div>', unsafe_allow_html=True)
        st.markdown(verdict_html(final.get("is_good_fit", False)), unsafe_allow_html=True)

        if final.get("reason"):
            st.markdown(f"""
            <div class="insight-row">
                <div class="dot dot-blue"></div>
                <div><strong style="color:#c8d4f0;">Decision Rationale:</strong>&nbsp; {final['reason']}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-hd">Improvement Recommendations</div>', unsafe_allow_html=True)
        recs = data.get("improvement_recommendations", [])
        st.markdown(insight_rows(recs, "dot-blue", "No recommendations listed."), unsafe_allow_html=True)

        # Experience & seniority summary
        if data.get("experience_summary") or data.get("seniority_level"):
            st.markdown('<div class="section-hd">Experience Profile</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                if data.get("seniority_level"):
                    st.markdown(f"""
                    <div class="score-card blue" style="margin:0;">
                        <div class="score-label">Seniority Level</div>
                        <div style="font-size:1.1rem;font-weight:600;color:#4f7eff;margin-top:4px;">{data['seniority_level']}</div>
                    </div>""", unsafe_allow_html=True)
            with col2:
                if data.get("experience_summary"):
                    st.markdown(f"""
                    <div class="score-card green" style="margin:0;">
                        <div class="score-label">Experience Summary</div>
                        <div style="font-size:0.8rem;color:#22d38a;margin-top:4px;line-height:1.5;">{data['experience_summary']}</div>
                    </div>""", unsafe_allow_html=True)

    # ── TAB 2: SKILLS ──
    with tab2:
        st.markdown('<div class="section-hd">Matched Skills</div>', unsafe_allow_html=True)
        st.markdown(tag_html(data.get("matched_skills", []), "tag-match"), unsafe_allow_html=True)

        st.markdown('<div class="section-hd">Missing Skills</div>', unsafe_allow_html=True)
        st.markdown(tag_html(data.get("missing_skills", []), "tag-missing"), unsafe_allow_html=True)

        st.markdown('<div class="section-hd">Partial Matches</div>', unsafe_allow_html=True)
        st.markdown(tag_html(data.get("partially_matched_skills", []), "tag-partial"), unsafe_allow_html=True)

        st.divider()
        col_s, col_w = st.columns(2)
        with col_s:
            st.markdown('<div class="section-hd">Candidate Strengths</div>', unsafe_allow_html=True)
            st.markdown(insight_rows(data.get("candidate_strengths", []), "dot-green", "No strengths identified."), unsafe_allow_html=True)
        with col_w:
            st.markdown('<div class="section-hd">Candidate Weaknesses</div>', unsafe_allow_html=True)
            st.markdown(insight_rows(data.get("candidate_weaknesses", []), "dot-red", "No weaknesses identified."), unsafe_allow_html=True)

        # Bonus: red flags
        if data.get("red_flags"):
            st.markdown('<div class="section-hd">Red Flags</div>', unsafe_allow_html=True)
            st.markdown(insight_rows(data.get("red_flags", []), "dot-amber"), unsafe_allow_html=True)

    # ── TAB 3: EMAIL ──
    with tab3:
        email_text = api_results.get("email", "No email generated.")
        st.markdown(email_html(email_text), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_dl1, col_dl2, _ = st.columns([1, 1, 3])
        with col_dl1:
            st.download_button(
                "⬇  Download .txt",
                email_text,
                file_name="hr_response.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col_dl2:
            st.download_button(
                "⬇  Download .md",
                f"# HR Response Email\n\n{email_text}",
                file_name="hr_response.md",
                mime="text/markdown",
                use_container_width=True
            )

    # ── TAB 4: RAW JSON ──
    with tab4:
        if show_raw:
            st.markdown('<div class="section-hd">Full Analysis JSON</div>', unsafe_allow_html=True)
            st.json(data)
            st.markdown('<div class="section-hd">Raw Email Output</div>', unsafe_allow_html=True)
            st.code(api_results.get("email", ""), language="text")
        else:
            st.markdown("""
            <div style="text-align:center;padding:3rem 0;color:#3a4560;">
                <div style="font-size:2rem;margin-bottom:12px;">🔒</div>
                <div style="font-size:0.85rem;">Enable <strong style="color:#9aaac0;">Raw JSON</strong> from the sidebar to view full API payloads.</div>
            </div>""", unsafe_allow_html=True)