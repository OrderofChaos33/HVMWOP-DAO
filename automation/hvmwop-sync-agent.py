import os
import subprocess
from github import Github
import openai

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REPO_NAME = "OrderofChaos33/HVMWOP-DAO"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)
openai.api_key = OPENAI_API_KEY

def read_quadrants(file_path="quadrants.md"):
    with open(file_path, "r") as f:
        content = f.read()
    return content

def extract_todo(content):
    lines = content.splitlines()
    tasks = []
    capture = False
    for line in lines:
        if line.strip().lower().startswith("## to do now"):
            capture = True
            continue
        if line.strip().startswith("##") and capture:
            break
        if capture and line.strip().startswith("-"):
            tasks.append(line.strip("- ").strip())
    return tasks

def ai_prioritize(tasks):
    prompt = f"Prioritize and refine these tasks:
{tasks}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an executive workflow optimizer."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message["content"]

def create_github_issue(title, body=""):
    issue = repo.create_issue(title=title, body=body)
    print(f"Issue created: {issue.html_url}")

def sync_tasks_to_github(tasks):
    for t in tasks:
        create_github_issue(t)

def git_push(commit_message="HVMWOP Agent Auto Commit"):
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", commit_message], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("Changes pushed to GitHub.")

if __name__ == "__main__":
    quadrant_text = read_quadrants()
    todo_tasks = extract_todo(quadrant_text)
    print(f"Found {len(todo_tasks)} tasks.")
    enhanced = ai_prioritize(todo_tasks)
    print("Enhanced Task List:
", enhanced)
    for task in todo_tasks:
        create_github_issue(task)
    git_push()
