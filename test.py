import git
repo = git.Repo()
current_hash = repo.head.object.hexsha
o = repo.remotes.origin
origin_hash = o.fetch()[0].commit.hexsha
if current_hash != origin_hash:
    print("Update available!")