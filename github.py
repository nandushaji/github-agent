import os
import requests
from dotenv import load_dotenv
from langchain_core.documents import Document

load_dotenv()

github_token = os.getenv("GITHUB_TOKEN")


def fetch_github(owner,repo,endpoint):
    url = f"https://api.github.com/repos/{owner}/{repo}/{endpoint}"
    headers = {
        "Authorization":f"Bearer {github_token}"
    }
    response = requests.get(url,headers)
    if response.status_code == 200:
        data = response.json()
    else:
        print("Failed with status code:",response.status_code)
        return []
    # print(data)
    return data

def fetch_github_issues(owner,repo):
    issues = fetch_github(owner,repo,endpoint="issues")
    
    return load_issues(issues)

def load_issues(issues):
    docs = []
    for entry in issues:
        metadata = {
            "author": entry["user"]["login"],
            "comments":entry["comments"],
            "body":entry["body"],
            "labels":entry["labels"],
            "created_at":entry["created_at"]
        }
        data = entry["title"]
        if entry["body"]:
            data+=entry["body"]
        doc = Document(metadata=metadata,page_content=data)
        docs.append(doc)
    return docs
