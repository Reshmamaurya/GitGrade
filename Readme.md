# GitGrade – GitHub Repository Analyzer

GitGrade is a FastAPI-based web service that analyzes GitHub repositories. It fetches repository metadata (commits, files, languages, README, stars) and uses AI (Perplexity API) to provide a summary and improvement roadmap.

---

## Features

- Analyze GitHub repositories by URL
- Fetch files, commits, languages, README, and stars
- Calculate a repository score
- Generate AI-powered summary and improvement roadmap
- Returns JSON for easy frontend integration

---

## Tech Stack

- Python 3.10+
- FastAPI
- Jinja2 (for templates)
- Pydantic
- Requests
- Mangum (for serverless deployment)
- python-dotenv (for local environment variables)
- GitHub API
- Perplexity AI API

---
```
## Project Structure

GITGRADE/
├─ analyze.py 
├─ templates/
│ └─ index.html # Home page template
├─ .gitignore # Excludes .env and temporary files
├─ README.md
└─ .env # Local only, never commit
---
```
## Installation (Local Development)

1. Clone the repository:

```bash
git clone https://github.com/<your-username>/GitGrade.git
cd GitGrade
Create a virtual environment:

bash
Copy code
python -m venv venv
# Activate the virtual environment:
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Create a .env file in the project root (local only):

env
Copy code
GITHUB_TOKEN=your_github_token
PPLX_API_KEY=your_perplexity_api_key
Running Locally
bash
Copy code
uvicorn api.analyze:app --reload
Open http://127.0.0.1:8000/ in your browser.

Use the /analyze POST endpoint to analyze GitHub repositories.

Example POST request:

json
Copy code
POST /analyze
{
  "url": "https://github.com/owner/repo"
}
Example Response:

json
Copy code
{
  "score": "85/100",
  "summary": "Repository is a front-end web app with good structure...",
  "roadmap": [
    "Add more unit tests",
    "Improve documentation",
    "Refactor code for modularity"
  ]
}

[![Watch the demo](https://img.youtube.com/vi/TTTyJF_Hilw/maxresdefault.jpg)](https://youtu.be/TTTyJF_Hilw)

**Reshma Maurya**  
Pre-final Year CSE  
IIT Jodhpur

