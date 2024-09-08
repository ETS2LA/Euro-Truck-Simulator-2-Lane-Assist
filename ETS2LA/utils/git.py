import ETS2LA.variables as variables
import requests
import time
import git
import os

CACHE_DIR = f"{variables.PATH}cache"
CACHE_FILE = os.path.join(CACHE_DIR, "avatar_urls.txt")

def CheckForUpdate():
    try:
        repo = git.Repo()
        current_hash = repo.head.object.hexsha
        o = repo.remotes.origin
        origin_hash = o.fetch()[0].commit.hexsha
        return current_hash != origin_hash
    except:
        return False
    
commits_save = []
def GetHistory():
    global commits_save
    try:
        # If the git history has already been retrieved, then return that instead of searching again
        if commits_save == []:
            # Vars
            api_requests = 0
            commits = []
            authors = {}

            # Get the git history as json
            repo = git.Repo(search_parent_directories=True)
            
            for commit in repo.iter_commits():
                # Add the commit to the list
                commits.append({
                    "author": commit.author.name,
                    "message": commit.message,
                    "time": commit.committed_date
                })
            
            count = len(commits)
            index = 0
            for commit in commits:
                if index <= 100: # Only get images for the first 100 commits
                    if commit["author"] not in authors:
                        if commit["author"] == "DylDev": # Hardcoded because of usernames
                            url = f"https://api.github.com/users/DylDevs"
                        else:
                            url = f"https://api.github.com/users/{commit['author']}"

                        # Check if the avatar URL is cached
                        cached_url = load_cached_avatar_url(commit["author"])
                        if cached_url:
                            authors[commit["author"]] = cached_url
                        else:
                            try:
                                response = requests.get(url, timeout=6)
                                success = True
                            except:
                                success = False
                                print(f"Github API request was unsuccessful for author: {commit['author']}. (Timed out)")
                                continue

                            if success:
                                api_requests += 1
                                if response.status_code == 200:
                                    data = response.json()
                                    avatar_url = data["avatar_url"]
                                    authors[commit["author"]] = avatar_url
                                    save_avatar_url_to_cache(commit["author"], avatar_url)
                                else:
                                    authors[commit["author"]] = "https://github.com/favicon.ico"
                            else:
                                authors[commit["author"]] = "https://github.com/favicon.ico"
                    commit["picture"] = authors[commit["author"]]
                
                index += 1

            commits_save = commits
            return commits
        else:
            return commits_save
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
                    if time.time() - cached_time < 24 * 3600:
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
                    cached_urls.append(f"{username}: {time.time()}: {url}")
                else:
                    cached_urls.append(line.strip())

    # If the user was not found in the cache, add a new entry
    if username not in [line.split(": ")[0] for line in cached_urls]:
        cached_urls.append(f"{username}: {time.time()}: {url}")

    with open(CACHE_FILE, "w") as f:
        f.write("\n".join(cached_urls))