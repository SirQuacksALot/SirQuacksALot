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
    
    # ParseHTML 
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Read Statistics
    stats = {}
    for div in dl.find_all("div"):
        dt = div.find("dt")
        dd = div.find("dd")
        if dt and dd:
            key = dt.text.strip().lower().replace(" ", "_")  # Normalisiere den Namen
            value = int(dd.text.strip().replace(",", ""))  # Entferne Kommata und konvertiere in int
            stats[key] = value
    
    # Check values
    if "total_visitors" in stats and "unique_visitors" in stats:
        return {
            "total_visitors": stats["total_visitors"],
            "unique_visitors": stats["unique_visitors"]
        }
    else:
        raise Exception("Could not extract total_visitors and unique_visitors from the stats.")

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

