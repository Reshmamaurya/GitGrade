import os
import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv  # For loading .env file


load_dotenv()  

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
PPLX_API_KEY = os.getenv("PPLX_API_KEY")

if not GITHUB_TOKEN or not PPLX_API_KEY:
    raise RuntimeError("Set GITHUB_TOKEN and PPLX_API_KEY in your .env file")

# ================= CONFIG =================
GITHUB_API = "https://api.github.com"
PPLX_URL = "https://api.perplexity.ai/chat/completions"

app = FastAPI(title="GitGrade – Repository Mirror")
templates = Jinja2Templates(directory="templates")

# ================= MODELS =================
class RepoRequest(BaseModel):
    url: str

# ================= ROUTES =================
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """Render home page"""
    return templates.TemplateResponse("index.html", {"request": request})

# ================= GITHUB =================
def parse_repo(url: str):
    """Extract owner and repo name from URL"""
    parts = url.rstrip("/").split("/")
    return parts[-2], parts[-1]

def github_get(endpoint: str):
    """Perform GET request to GitHub API"""
    r = requests.get(
        f"{GITHUB_API}{endpoint}",
        headers={"Authorization": f"token {GITHUB_TOKEN}"},
    )
    if r.status_code != 200:
        raise Exception(f"GitHub API error: {r.text}")
    return r.json()

def fetch_all_files(owner, repo, path=""):
    """Recursively fetch all files in a repository"""
    files = []
    items = github_get(f"/repos/{owner}/{repo}/contents/{path}")

    for item in items:
        if item["type"] == "file":
            files.append(item)
        elif item["type"] == "dir":
            files.extend(fetch_all_files(owner, repo, item["path"]))

    return files

def fetch_repo_data(repo_url: str):
    """Fetch repo info, commits, languages, files, and README"""
    owner, repo = parse_repo(repo_url)

    repo_info = github_get(f"/repos/{owner}/{repo}")
    commits = github_get(f"/repos/{owner}/{repo}/commits?per_page=100")
    languages = github_get(f"/repos/{owner}/{repo}/languages")
    files = fetch_all_files(owner, repo)

    readme = ""
    try:
        readme_data = github_get(f"/repos/{owner}/{repo}/readme")
        readme = requests.get(readme_data["download_url"]).text
    except:
        pass

    return {
        "files": files,
        "commits": commits,
        "languages": languages,
        "readme": readme,
        "stars": repo_info["stargazers_count"],
    }

# ================= SCORING =================
def score_repository(data):
    """Calculate a simple score for the repo"""
    score = 0

    if len(data["files"]) >= 5:
        score += 15
    if len(data["commits"]) >= 10:
        score += 20
    elif len(data["commits"]) >= 3:
        score += 10
    if len(data["readme"]) > 200:
        score += 20
    if any("test" in f["name"].lower() for f in data["files"]):
        score += 20
    if len(data["languages"]) > 1:
        score += 10
    if data["stars"] > 0:
        score += 5

    return min(score, 100)

# ================= AI =================
def call_perplexity(prompt: str):
    """Call Perplexity AI API"""
    r = requests.post(
        PPLX_URL,
        headers={
            "Authorization": f"Bearer {PPLX_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "sonar-pro",
            "messages": [
                {"role": "system", "content": "You are a senior software mentor."},
                {"role": "user", "content": prompt},
            ],
        },
        timeout=30,
    )

    if r.status_code != 200:
        raise Exception(f"Perplexity API error: {r.text}")

    return r.json()["choices"][0]["message"]["content"]
@app.post("/analyze")
def analyze_repo(req: RepoRequest):
    """Analyze a GitHub repository and return score + summary + roadmap"""
    try:
        # Fetch repo data and calculate score
        data = fetch_repo_data(req.url)
        score = score_repository(data)

        # Prepare AI prompt
        prompt = f"""
Analyze this GitHub repository and respond clearly.

Score: {score}/100
Files: {len(data["files"])}
Commits: {len(data["commits"])}
Languages: {list(data["languages"].keys())}

Return:
- Short summary
- 3–5 improvement steps
"""

        ai = call_perplexity(prompt)

        # Clean AI response: remove **, ###, numbers, bullets, extra spaces
        cleaned_lines = []
        for line in ai.split("\n"):
            line = line.strip()
            if line:
                line = line.replace("**", "").replace("###", "")
                line = line.lstrip("0123456789.-• ").strip()
                if line:
                    cleaned_lines.append(line)

        # Split summary and improvement steps
        summary_lines = []
        personal_recommendations = []
        improvement_started = False

        for line in cleaned_lines:
            if "improvement" in line.lower() or "roadmap" in line.lower():
                improvement_started = True
                continue
            if improvement_started:
                personal_recommendations.append(line)
            else:
                summary_lines.append(line)

        # Fallback if no recommendations found
        if not personal_recommendations:
            personal_recommendations = [
                "Add tests",
                "Improve documentation",
                "Refactor code structure",
            ]

        summary = " ".join(summary_lines) if summary_lines else "No summary available."

        return {
            "score": f"{score}/100",
            "summary": summary,
            "roadmap": personal_recommendations
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
