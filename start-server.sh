cd server 
source ./env/bin/activate 
find . -name "*.py" ! -path "**/env/*" | entr -r python start.py