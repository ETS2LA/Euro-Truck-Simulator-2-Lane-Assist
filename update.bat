@echo off
git pull
pip install -r requirements.txt
cd frontend
npm install
echo "Update complete"
pause