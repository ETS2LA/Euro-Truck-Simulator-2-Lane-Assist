import ETS2LA.variables as variables
import requests
import time
import git
import os

CACHE_DIR = f"{variables.PATH}cache"
CACHE_FILE = os.path.join(CACHE_DIR, "avatar_urls.txt")

def GetCommitURL(repo, commit_hash):
    try:
        # Get the remote URL
        remote_url = repo.remotes.origin.url
        
        # Remove .git extension if present
        remote_url = remote_url.replace('.git', '')
        
        # Handle SSH format (git@github.com:user/repo.git)
        if remote_url.startswith('git@'):
            remote_url = remote_url.replace(':', '/')
            remote_url = remote_url.replace('git@', 'https://')
        
        # Determine platform and create URL
        if 'github.com' in remote_url:
            return f"{remote_url}/commit/{commit_hash}"
        elif 'gitlab.com' in remote_url:
            return f"{remote_url}/-/commit/{commit_hash}"
        else:
            return ""
    except:
        return ""

def CheckForUpdate():
    try:
        repo = git.Repo()
        current_hash = repo.head.object.hexsha
        
        o = repo.remotes.origin
        origin_hash = o.fetch()
        
        if len(origin_hash) > 0:
            origin_hash = origin_hash[0].commit.hexsha
        else:
            origin_hash = current_hash
            
        if current_hash != origin_hash:
            updates = []
            for commit in repo.iter_commits(f"{current_hash}..{origin_hash}"):
                if "Merge" not in commit.summary: # Ignore merge commits
                    updates.append({
                        "author": commit.author.name,
                        "message": commit.summary,
                        "description": commit.message.replace(commit.summary, "").strip(),
                        "time": commit.committed_date,
                        "url": GetCommitURL(repo, commit.hexsha)
                    })
            
            if updates == []: # local commit(s) waiting to be pushed, send those instead
                for commit in repo.iter_commits():
                    if "Merge" not in commit.summary:
                        updates.append({
                            "author": commit.author.name,
                            "message": commit.summary,
                            "description": commit.message.replace(commit.summary, "").strip(),
                            "time": commit.committed_date,
                            "url": GetCommitURL(repo, commit.hexsha)
                        })
                    if len(updates) >= 10:
                        break
                
                updates = updates[::-1]
                
                updates.append({
                    "author": "Backend",
                    "message": "DO NOT UPDATE!",
                    "description": "You have a local commit that is waiting to be pushed. Updating will clear the changes and stash them.",
                    "time": time.perf_counter(),
                    "url": ""
                })
                
            return updates
        else:
            return False
    except:
        import traceback
        traceback.print_exc()
        return False
    
commits_save = []
def GetHistory():
    global commits_save
    try:
        # Return cached results if available
        if commits_save != []:
            return commits_save

        # Vars
        api_requests = 0
        commits = []
        authors = {}

        # Get the git history as json
        repo = git.Repo(search_parent_directories=True)
        
        for commit in repo.iter_commits():
            if "Merge" not in commit.summary:  # Ignore merge commits like in CheckForUpdate
                commit_data = {
                    "author": commit.author.name,
                    "message": commit.summary,
                    "description": commit.message.replace(commit.summary, "").strip(),
                    "time": commit.committed_date,
                    "url": GetCommitURL(repo, commit.hexsha)  # Add URL like CheckForUpdate
                }

                # Handle avatar URLs for first 100 commits
                if len(commits) < 100:
                    if commit.author.name not in authors:
                        if commit.author.name == "DylDev":
                            url = "https://api.github.com/users/DylDevs"
                        elif commit.author.name == "Lun":
                            url = "https://api.github.com/users/Lun011666"
                        else:
                            url = f"https://api.github.com/users/{commit.author.name}"

                        cached_url = load_cached_avatar_url(commit.author.name)
                        if cached_url:
                            authors[commit.author.name] = cached_url
                        else:
                            try:
                                response = requests.get(url, timeout=6)
                                if response.status_code == 200:
                                    data = response.json()
                                    avatar_url = data["avatar_url"]
                                    authors[commit.author.name] = avatar_url
                                    save_avatar_url_to_cache(commit.author.name, avatar_url)
                                else:
                                    authors[commit.author.name] = "https://github.com/favicon.ico"
                            except:
                                print(f"Github API request was unsuccessful for author: {commit.author.name}. (Timed out)")
                                authors[commit.author.name] = "https://github.com/favicon.ico"
                    
                    commit_data["picture"] = authors[commit.author.name]

                commits.append(commit_data)

        commits_save = commits
        return commits
    except:
        import traceback
        traceback.print_exc()
        return []
    
def Update():
    raise Exception("Update") # Crash the app so that the handler can update.

def load_cached_avatar_url(username):
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(": ")
                if parts[0] == username:
                    # Check if the cached URL is older than 24 hours
                    cached_time = float(parts[1])
                    if time.perf_counter() - cached_time < 24 * 3600:
                        return parts[2]
    return None

def save_avatar_url_to_cache(username, url):
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    cached_urls = []
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(": ")
                if parts[0] == username:
                    # Update the existing entry for the user
                    cached_urls.append(f"{username}: {time.perf_counter()}: {url}")
                else:
                    cached_urls.append(line.strip())

    # If the user was not found in the cache, add a new entry
    if username not in [line.split(": ")[0] for line in cached_urls]:
        cached_urls.append(f"{username}: {time.perf_counter()}: {url}")

    with open(CACHE_FILE, "w") as f:
        f.write("\n".join(cached_urls))