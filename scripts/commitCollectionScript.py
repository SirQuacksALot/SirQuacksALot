import os
import json
import requests

def collect_commit_stats():
    # Token aus Umgebungsvariable auslesen
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is not set.")
    username = "SirQuacksALot"
    headers = {"Authorization": f"Bearer {token}"}
        
    # Load repositories from GitHub API
    repos = []
    page = 1
    while True:
        response = requests.get(
            f"https://api.github.com/user/repos?per_page=100&page={page}",
            headers=headers
        )
        if response.status_code != 200:
            raise Exception(f"Failed to fetch repositories: {response.status_code}, {response.text}")
        data = response.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    
    # Calculate total commits
    total_commits = 0
    for repo in repos:
        repo_name = repo["full_name"]
        page = 1
        while True:
            commits_url = f"https://api.github.com/repos/{repo_name}/commits?author={username}&per_page=100&page={page}"
            commit_response = requests.get(commits_url, headers=headers)
            if commit_response.status_code != 200:
                print(f"Warning: Failed to fetch commits for {repo_name}: {commit_response.status_code}")
                break
            commits = commit_response.json()
            if not commits:
                break
            total_commits += len(commits)
            page += 1
    
    # Save the total commits to a JSON file
    with open("stats.json", "w") as f:
        json.dump({"total_commits": total_commits}, f, indent=2)
    print(f"Total commits: {total_commits}")

if __name__ == "__main__":
    collect_commit_stats()
