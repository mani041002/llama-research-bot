import streamlit as st
import requests
import os

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.main-title {
    font-family: 'Space Mono', monospace;
    font-size: 2.4rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -1px;
    margin-bottom: 0.2rem;
}
.subtitle {
    font-size: 1rem;
    color: #64748b;
    margin-bottom: 2rem;
}
.result-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #6366f1;
    border-radius: 10px;
    padding: 1.5rem 1.8rem;
    margin-top: 1.5rem;
    font-size: 0.97rem;
    line-height: 1.75;
    color: #1e293b;
}
.stat-bar {
    background: #f1f5f9;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-size: 0.82rem;
    color: #475569;
    margin-top: 0.8rem;
}
.error-box {
    background: #fff1f2;
    border: 1px solid #fecdd3;
    border-left: 4px solid #f43f5e;
    border-radius: 10px;
    padding: 1rem 1.4rem;
    color: #9f1239;
    margin-top: 1rem;
}
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 2rem;
    font-weight: 600;
    font-size: 0.95rem;
    cursor: pointer;
    transition: opacity 0.2s;
    width: 100%;
}
.stButton > button:hover {
    opacity: 0.88;
}
.badge {
    background: #dcfce7;
    color: #166534;
    border-radius: 999px;
    padding: 2px 10px;
    font-size: 0.75rem;
    font-weight: 600;
    vertical-align: middle;
    margin-left: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🔍 AI Research Agent</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Live web search + Groq LLaMA · Real-time facts, not hallucinations '
    '<span class="badge">LIVE</span></p>',
    unsafe_allow_html=True
)

st.divider()

with st.form(key="search_form", clear_on_submit=False):
    topic = st.text_input(
        "Research Topic",
        placeholder="Enter topic",
    )
    search_btn = st.form_submit_button("🚀 Run Research", use_container_width=True)

if search_btn:
    if not topic.strip():
        st.warning("Please enter a topic before running research.")
    else:
        with st.spinner("🌐 Searching the web and analysing with AI…"):
            try:
                api_url = f"{BACKEND_URL.rstrip('/')}/research"
                response = requests.get(
                    api_url,
                    params={"topic": topic.strip()},
                    timeout=60,
                )

                if response.status_code == 200:
                    data = response.json()

                    st.markdown("### 📋 Research Result")
                    st.markdown(
                        f'<div class="result-box">{data.get("answer", "No answer returned.")}</div>',
                        unsafe_allow_html=True
                    )

                    ctx_len = data.get("context_length", 0)
                    num_sources = len(data.get("sources", []))
                    st.markdown(
                        f'<div class="stat-bar">📊 Context scraped: <strong>{ctx_len:,} chars</strong> '
                        f'&nbsp;|&nbsp; Sources crawled: <strong>{num_sources}</strong></div>',
                        unsafe_allow_html=True
                    )

                elif response.status_code == 400:
                    err = response.json().get("detail", "Bad request")
                    st.markdown(
                        f'<div class="error-box">⚠️ <strong>Input Error:</strong> {err}</div>',
                        unsafe_allow_html=True
                    )
                elif response.status_code == 500:
                    err = response.json().get("detail", "Server error")
                    st.markdown(
                        f'<div class="error-box">🔴 <strong>Server Error:</strong> {err}</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.error(f"Unexpected status {response.status_code}: {response.text}")

            except requests.exceptions.ConnectionError:
                st.markdown(
                    '<div class="error-box">🔌 <strong>Connection Error:</strong> '
                    'Cannot reach the backend. Make sure uvicorn is running.</div>',
                    unsafe_allow_html=True
                )
            except requests.exceptions.Timeout:
                st.markdown(
                    '<div class="error-box">⏱️ <strong>Timeout:</strong> '
                    'The request took too long. Try again.</div>',
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.markdown(
                    f'<div class="error-box">❌ <strong>Unexpected Error:</strong> {str(e)}</div>',
                    unsafe_allow_html=True
                )

st.divider()
st.markdown(
    "<center><small>Powered by <strong>Groq LLaMA 3.3-70B</strong> · "
    "Live scraping via <strong>Wikipedia + NewsAPI</strong> · "
    "Backend on <strong>Render</strong> · Frontend on <strong>Streamlit Cloud</strong>"
    "</small></center>",
    unsafe_allow_html=True
)