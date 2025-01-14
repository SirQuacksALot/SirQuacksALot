import os
import json
import requests

def collect_commit_stats():
    # Token aus Umgebungsvariable auslesen
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is not set.")
        
    # Load repositories from GitHub API
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("https://api.github.com/users/SirQuacksALot/repos?per_page=100", headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch repositories: {response.status_code}, {response.text}")
    repos = response.json()

    # Calculate total commits
    total_commits = 0
    for repo in repos:
        repo_name = repo["full_name"]
        commits_url = f"https://api.github.com/repos/{repo_name}/commits?author=SirQuacksALot"
        print(f"Fetching commits for {repo_name}...")
        commit_response = requests.get(commits_url, headers=headers)
        if commit_response.status_code == 200:
            total_commits += len(commit_response.json())
        else:
            print(f"Warning: Failed to fetch commits for {repo_name}: {commit_response.status_code}")

    # Save the total commits to a JSON file
    with open("stats.json", "w") as f:
        json.dump({"total_commits": total_commits}, f, indent=2)
    print(f"Total commits: {total_commits}")

if __name__ == "__main__":
    collect_commit_stats()