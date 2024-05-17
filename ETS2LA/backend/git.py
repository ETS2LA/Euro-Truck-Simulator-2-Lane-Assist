import git
import requests

def CheckForUpdate():
    repo = git.Repo()
    current_hash = repo.head.object.hexsha
    o = repo.remotes.origin
    origin_hash = o.fetch()[0].commit.hexsha
    if current_hash != origin_hash:
        return True
    else:
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
                    if not commit["author"] in authors:
                        if commit["author"] == "DylDev": # Hardcded because of usernames
                            url = f"https://api.github.com/users/DylDevs"
                        else:
                            url = f"https://api.github.com/users/{commit['author']}"
                        # Get the avatar url from the GitHub API
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
                            else:
                                authors[commit["author"]] = "https://github.com/favicon.ico"
                        else:
                            authors[commit["author"]] = "https://github.com/favicon.ico"
                    else:
                        pass
                    
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