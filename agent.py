import os
import requests
from bs4 import BeautifulSoup
import time
import re
from dotenv import load_dotenv
from google import genai
from groq import Groq

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GROQ_API_KEY   = os.environ.get("GROQ_API_KEY", "")
NEWSAPI_KEY    = os.environ.get("NEWSAPI_KEY", "")
GROQ_MODEL     = "llama-3.3-70b-versatile"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


# ── Company Website Scraper ───────────────────────────────────────
def scrape_company_website(topic: str) -> tuple[str, list[str]]:
    results, sources = [], []
    topic_lower = topic.lower().strip()

    slug = re.sub(r"[^a-z0-9]", "", topic_lower)
    slug_dash = re.sub(r"\s+", "-", topic_lower)
    slug_dash = re.sub(r"[^a-z0-9-]", "", slug_dash)

    candidate_urls = [
        f"https://www.{slug}.com",
        f"https://{slug}.com",
        f"https://www.{slug_dash}.com",
        f"https://{slug_dash}.com",
        f"https://www.{slug}.io",
        f"https://{slug}.io",
        f"https://www.{slug}.ai",
        f"https://{slug}.ai",
    ]

    for url in candidate_urls:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=8)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                    tag.decompose()
                meta = soup.find("meta", attrs={"name": "description"})
                meta_text = meta["content"] if meta and meta.get("content") else ""
                texts = [
                    tag.get_text(separator=" ", strip=True)
                    for tag in soup.find_all(["p", "h1", "h2", "h3", "li", "article", "section"])
                    if len(tag.get_text(strip=True)) > 30
                ]
                content = re.sub(r"\s+", " ", " ".join(texts)).strip()[:4000]
                if content or meta_text:
                    full = f"Meta: {meta_text}\n{content}" if meta_text else content
                    results.append(f"[Company Website: {url}]\n{full}")
                    sources.append(url)
                    print(f"[Company Scrape] Got {len(full)} chars from {url}")
                    break
        except Exception as e:
            print(f"[Company Scrape] {url[:60]} → {e}")

    return "\n\n---\n\n".join(results), sources


# ── Wikipedia ─────────────────────────────────────────────────────
def search_wikipedia(query: str) -> str:
    try:
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + requests.utils.quote(query)
        resp = requests.get(url, headers=HEADERS, timeout=8)
        if resp.status_code == 200:
            extract = resp.json().get("extract", "")
            if extract:
                print(f"[Wikipedia] Got {len(extract)} chars")
                return f"[Wikipedia]\n{extract}"
    except Exception as e:
        print(f"[Wikipedia] Error: {e}")
    return ""


def search_wikipedia_query(query: str) -> list[dict]:
    try:
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": 3,
        }
        resp = requests.get("https://en.wikipedia.org/w/api.php", params=params, headers=HEADERS, timeout=8)
        results = []
        for item in resp.json().get("query", {}).get("search", []):
            results.append({
                "title": item.get("title", ""),
                "snippet": BeautifulSoup(item.get("snippet", ""), "html.parser").get_text(),
                "url": f"https://en.wikipedia.org/wiki/{requests.utils.quote(item.get('title', ''))}",
            })
        print(f"[Wiki Search] Found {len(results)} pages")
        return results
    except Exception as e:
        print(f"[Wiki Search] Error: {e}")
        return []


# ── NewsAPI ───────────────────────────────────────────────────────
def search_newsapi(query: str, num_results: int = 5):
    if not NEWSAPI_KEY:
        print("[NewsAPI] No key found, skipping.")
        return "", []
    try:
        params = {
            "q": query,
            "pageSize": num_results,
            "sortBy": "publishedAt",
            "language": "en",
            "apiKey": NEWSAPI_KEY,
        }
        resp = requests.get("https://newsapi.org/v2/everything", params=params, timeout=10)
        data = resp.json()
        if data.get("status") != "ok":
            return "", []
        parts, sources = [], []
        for a in data.get("articles", []):
            title       = a.get("title", "")
            description = a.get("description", "")
            source      = a.get("source", {}).get("name", "")
            url_link    = a.get("url", "")
            published   = a.get("publishedAt", "")
            if title and description:
                parts.append(
                    f"Title: {title}\nSource: {source} | Published: {published}\n"
                    f"Summary: {description}\nURL: {url_link}"
                )
                sources.append(url_link)
        print(f"[NewsAPI] Found {len(parts)} articles")
        return "\n\n".join(parts), sources
    except Exception as e:
        print(f"[NewsAPI] Error: {e}")
        return "", []


# ── Direct Scrape ─────────────────────────────────────────────────
def scrape_direct(topic: str) -> tuple[str, list[str]]:
    results, sources = [], []
    topic_lower = topic.lower()

    if any(w in topic_lower for w in ["stock", "price", "share", "market"]):
        company = re.sub(r"stock price|share price|current|price", "", topic_lower).strip()
        urls_to_try = [f"https://finance.yahoo.com/quote/{company.upper()}/"]
    elif any(w in topic_lower for w in ["bitcoin", "crypto", "ethereum", "btc"]):
        urls_to_try = ["https://coinmarketcap.com/currencies/bitcoin/"]
    else:
        urls_to_try = [f"https://en.wikipedia.org/wiki/{requests.utils.quote(topic)}"]

    for url in urls_to_try:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=8)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                    tag.decompose()
                texts = [
                    tag.get_text(separator=" ", strip=True)
                    for tag in soup.find_all(["p", "article", "main", "h1", "h2", "h3", "td", "li"])
                    if len(tag.get_text(strip=True)) > 30
                ]
                content = re.sub(r"\s+", " ", " ".join(texts)).strip()[:3000]
                if content:
                    results.append(f"[Source: {url}]\n{content}")
                    sources.append(url)
                    print(f"[Direct Scrape] Got {len(content)} chars from {url[:60]}")
        except Exception as e:
            print(f"[Direct Scrape] {url[:60]} → {e}")
        time.sleep(0.3)

    return "\n\n---\n\n".join(results), sources


# ── Gather All Context ────────────────────────────────────────────
def gather_context(topic: str) -> tuple[str, list[str]]:
    context_parts, all_sources = [], []

    company_text, company_sources = scrape_company_website(topic)
    if company_text:
        context_parts.append(company_text)
        all_sources.extend(company_sources)

    wiki_summary = search_wikipedia(topic)
    if wiki_summary:
        context_parts.append(wiki_summary)

    for item in search_wikipedia_query(topic):
        context_parts.append(
            f"[Wikipedia: {item['title']}]\nSnippet: {item['snippet']}\nURL: {item['url']}"
        )
        all_sources.append(item["url"])

    news_text, news_sources = search_newsapi(topic, num_results=5)
    if news_text:
        context_parts.append(f"[Latest News]\n{news_text}")
        all_sources.extend(news_sources)

    scraped_text, scraped_sources = scrape_direct(topic)
    if scraped_text:
        context_parts.append(scraped_text)
        all_sources.extend(scraped_sources)

    combined = "\n\n---\n\n".join(context_parts)
    print(f"[Agent] Total context: {len(combined)} chars from {len(all_sources)} sources")
    return combined[:12000], list(dict.fromkeys(all_sources))


# ── Gemini LLM ────────────────────────────────────────────────────
def synthesise_with_gemini(topic: str, context: str):
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = (
            f"You are an expert research assistant. "
            f"Answer ONLY using the web content provided below. "
            f"Do NOT hallucinate. Extract facts, numbers, prices, dates clearly. "
            f"Format your response with markdown.\n\n"
            f"Research Topic: {topic}\n\n"
            f"--- WEB CONTEXT ---\n{context}\n--- END ---\n\n"
            f"Give a comprehensive factual answer about: {topic}"
        )
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        if not response or not response.text:
            print("[Gemini] Empty response → falling back to Groq")
            return None
        print("[Gemini] Response received")
        return response.text
    except Exception as e:
        print(f"[Gemini] Failed: {e} → falling back to Groq")
        return None


# ── Groq LLM Fallback ─────────────────────────────────────────────
def synthesise_with_groq(topic: str, context: str) -> str:
    try:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert research assistant. "
                        "Answer ONLY using the web content provided. "
                        "Do NOT hallucinate. Extract facts, numbers, prices, dates clearly. "
                        "Format with markdown."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Topic: {topic}\n\n"
                        f"--- WEB CONTEXT ---\n{context}\n--- END ---\n\n"
                        f"Give a comprehensive factual answer about: {topic}"
                    ),
                },
            ],
            temperature=0.1,
            max_tokens=1500,
        )
        print("[Groq] Response received")
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: Both Gemini and Groq failed. Groq error: {str(e)}"


# ── Smart Synthesiser (Gemini → Groq fallback) ────────────────────
def synthesise(topic: str, context: str) -> str:
    if GEMINI_API_KEY:
        result = synthesise_with_gemini(topic, context)
        if result:
            return result

    if GROQ_API_KEY:
        print("[Agent] Using Groq fallback")
        return synthesise_with_groq(topic, context)

    return "Error: No AI API keys configured. Set GEMINI_API_KEY or GROQ_API_KEY."


# ── Main Entry Point ──────────────────────────────────────────────
def run_research_agent(topic: str) -> dict:
    if not GEMINI_API_KEY and not GROQ_API_KEY:
        return {"error": "No AI API key configured. Set GEMINI_API_KEY or GROQ_API_KEY."}

    context, sources = gather_context(topic)

    if not context:
        return {
            "topic": topic,
            "answer": "No web results found. Please try a different topic.",
            "sources": [],
            "context_length": 0,
        }

    answer = synthesise(topic, context)
    return {
        "topic": topic,
        "answer": answer,
        "sources": sources,
        "context_length": len(context),
    }