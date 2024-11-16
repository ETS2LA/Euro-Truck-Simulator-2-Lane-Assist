@echo off
git stash
git pull
pip install -r requirements.txt --quiet
echo "Clearing cache, prepare to login again."
RMDIR /S /Q "cache"
echo "Cache cleared"
cd frontend
npm i
npm run build
cd ..
echo "Update complete"
pause