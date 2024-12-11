cd server 
find . -name "*.py" ! -path "**/.venv/*" | entr -r uv run start.py