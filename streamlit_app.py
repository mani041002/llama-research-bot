import streamlit as st
import requests
import os
import time

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="Llama Research Bot",
    page_icon="🦙",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 40%, #06b6d4 100%);
    min-height: 100vh;
}

.hero-section {
    text-align: center;
    padding: 3rem 1rem 2rem 1rem;
}

.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    color: white;
    border: 1px solid rgba(255,255,255,0.4);
    border-radius: 999px;
    padding: 4px 16px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 1px;
    margin-bottom: 1rem;
}

.hero-title {
    font-size: 2.8rem;
    font-weight: 800;
    color: white;
    margin-bottom: 0.5rem;
    line-height: 1.2;
}

.hero-subtitle {
    font-size: 1.05rem;
    color: rgba(255,255,255,0.85);
    margin-bottom: 0.5rem;
}

.hero-meta {
    font-size: 0.85rem;
    color: rgba(255,255,255,0.7);
    margin-bottom: 2rem;
}

.hero-meta span {
    margin: 0 8px;
}

.result-card {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    margin-top: 1.5rem;
    box-shadow: 0 20px 60px rgba(0,0,0,0.15);
    color: #1e293b;
    font-size: 0.96rem;
    line-height: 1.8;
}

.result-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #4f46e5;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e0e7ff;
}

.stat-row {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
}

.stat-chip {
    background: #f0fdf4;
    color: #166534;
    border-radius: 999px;
    padding: 4px 14px;
    font-size: 0.78rem;
    font-weight: 600;
    border: 1px solid #bbf7d0;
}

.error-card {
    background: #fff1f2;
    border: 1px solid #fecdd3;
    border-left: 4px solid #f43f5e;
    border-radius: 12px;
    padding: 1rem 1.4rem;
    color: #9f1239;
    margin-top: 1rem;
}

.info-banner {
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 10px;
    padding: 0.6rem 1.2rem;
    color: rgba(255,255,255,0.9);
    font-size: 0.82rem;
    text-align: center;
    margin-bottom: 1.5rem;
}

/* Input styling */
.stTextInput > div > div > input {
    border-radius: 999px !important;
    border: none !important;
    padding: 0.8rem 1.5rem !important;
    font-size: 1rem !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1) !important;
    font-family: 'Poppins', sans-serif !important;
}

.stTextInput > div > div > input:focus {
    box-shadow: 0 4px 20px rgba(0,0,0,0.2) !important;
    outline: none !important;
}

/* Button styling */
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #7c3aed, #06b6d4) !important;
    color: white !important;
    border: none !important;
    border-radius: 999px !important;
    padding: 0.7rem 2.5rem !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    font-family: 'Poppins', sans-serif !important;
    transition: all 0.3s !important;
    width: 100% !important;
    box-shadow: 0 4px 15px rgba(124,58,237,0.4) !important;
}

.stFormSubmitButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(124,58,237,0.5) !important;
}

.footer {
    text-align: center;
    color: rgba(255,255,255,0.6);
    font-size: 0.78rem;
    padding: 2rem 0 1rem 0;
}

.footer strong {
    color: rgba(255,255,255,0.9);
}

/* Hide streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def wake_up_backend():
    try:
        requests.get(f"{BACKEND_URL}/", timeout=30)
    except:
        pass


# ── HERO SECTION ──────────────────────────────────────────────────
st.markdown("""
<div class="hero-section">
    <div class="hero-badge">🦙 BETA</div>
    <div class="hero-title">Llama Research Bot</div>
    <div class="hero-subtitle">Real-time AI research powered by Groq LLaMA 3.3-70B</div>
    <div class="hero-meta">
        <span>✅ Live Web Search</span>
        <span>•</span>
        <span>⚡ Instant Results</span>
        <span>•</span>
        <span>🔍 No Hallucination</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-banner">
    ⚠️ First search may take <strong>30-60 seconds</strong> to wake up the backend. Please be patient!
</div>
""", unsafe_allow_html=True)

# ── SEARCH FORM ───────────────────────────────────────────────────
with st.form(key="search_form", clear_on_submit=False):
    topic = st.text_input(
        "",
        placeholder="Ask anything... e.g. Bitcoin price, India GDP, AI news",
        label_visibility="collapsed",
    )
    search_btn = st.form_submit_button("🔍 Research Now", use_container_width=True)

# ── RESEARCH CALL ─────────────────────────────────────────────────
if search_btn:
    if not topic.strip():
        st.warning("Please enter a topic before searching.")
    else:
        with st.spinner("⏳ Waking up backend..."):
            wake_up_backend()

        with st.spinner("🌐 Searching the web and analysing with AI…"):
            try:
                api_url = f"{BACKEND_URL.rstrip('/')}/research"
                response = requests.get(
                    api_url,
                    params={"topic": topic.strip()},
                    timeout=120,
                )

                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No answer returned.")
                    ctx_len = data.get("context_length", 0)
                    num_sources = len(data.get("sources", []))

                    st.markdown(f"""
                    <div class="result-card">
                        <div class="result-title">📋 Research Result — {topic}</div>
                        {answer}
                        <div class="stat-row">
                            <span class="stat-chip">📊 {ctx_len:,} chars scraped</span>
                            <span class="stat-chip">🔗 {num_sources} sources</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                elif response.status_code == 400:
                    err = response.json().get("detail", "Bad request")
                    st.markdown(f'<div class="error-card">⚠️ <strong>Input Error:</strong> {err}</div>', unsafe_allow_html=True)

                elif response.status_code == 500:
                    err = response.json().get("detail", "Server error")
                    st.markdown(f'<div class="error-card">🔴 <strong>Server Error:</strong> {err}</div>', unsafe_allow_html=True)

                else:
                    st.error(f"Unexpected status {response.status_code}: {response.text}")

            except requests.exceptions.ConnectionError:
                st.markdown(
                    '<div class="error-card">🔌 <strong>Connection Error:</strong> '
                    'Cannot reach the backend. Make sure it is running.</div>',
                    unsafe_allow_html=True
                )
            except requests.exceptions.Timeout:
                st.markdown(
                    '<div class="error-card">⏱️ <strong>Timeout:</strong> '
                    'Backend is still waking up. Please try again in 30 seconds.</div>',
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.markdown(
                    f'<div class="error-card">❌ <strong>Error:</strong> {str(e)}</div>',
                    unsafe_allow_html=True
                )

# ── FOOTER ────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Powered by <strong>Groq LLaMA 3.3-70B</strong> · 
    Sources: <strong>Wikipedia + NewsAPI + Live Scraping</strong> · 
    Built with <strong>FastAPI + Streamlit</strong>
</div>
""", unsafe_allow_html=True)