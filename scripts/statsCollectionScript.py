import os
import json
import requests
from bs4 import BeautifulSoup

def get_visitor_stats(path):
    """
    Ruft die Besucherstatistiken von visitorbadge.io ab.
    :param path: Der URL-Pfad, der getrackt wird (z. B. ein GitHub-Profil oder Repository).
    :return: Ein Dictionary mit 'total_visitors' und 'unique_visitors'.
    """
    url = f"https://visitorbadge.io/status?path={path}"
    headers = { "User-Agent": "Mozilla/5.0 (compatible; GitHubActions/1.0)" }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch visitor stats: {response.status_code}")
    
    # HTML parsen
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extrahiert die Statistiken aus den entsprechenden HTML-Elementen
    stats = soup.find_all("h2")
    if len(stats) >= 2:
        total_visitors = stats[0].text.strip()
        unique_visitors = stats[1].text.strip()
        return {"total_visitors": int(total_visitors), "unique_visitors": int(unique_visitors)}
    else:
        raise Exception("Could not extract visitor statistics.")

def collect_commit_stats(username): 
    """
    Ruft die Commit-Statistiken von GitHub ab und kombiniert sie mit den Besucherstatistiken.
    """
    # Token aus Umgebungsvariable auslesen
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is not set.")
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
    return total_commits
    
if __name__ == "__main__":
    username = "SirQuacksALot"
    
    commits_stats = collect_commit_stats(username)
    visitor_stats = get_visitor_stats(f"https://github.com/{username}")
    
    # Save the total commits to a JSON file
    with open("stats.json", "w") as f:
        json.dump({"total_commits": total_commits, "visitor_stats": visitor_stats}, f, indent=2)
    print(f"Total commits: {commits_stats}")
    print(f"Visitor stats: {visitor_stats}")

