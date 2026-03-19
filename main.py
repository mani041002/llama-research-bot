from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from agent import run_research_agent
import uvicorn

app = FastAPI(
    title="AI Research Agent",
    description="Real-time web research powered by Groq LLM",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
@app.head("/")
def root():
    return {"status": "AI Research Agent is running"}

@app.get("/research")
def research(topic: str = Query(..., description="The topic to research")):
    if not topic or len(topic.strip()) < 2:
        raise HTTPException(status_code=400, detail="Topic must be at least 2 characters long")

    result = run_research_agent(topic.strip())

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)