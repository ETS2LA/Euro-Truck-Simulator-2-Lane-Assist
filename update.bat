@echo off
git pull
pip install -r requirements.txt --quiet
cd frontend
npm install
echo "Update complete"
pause