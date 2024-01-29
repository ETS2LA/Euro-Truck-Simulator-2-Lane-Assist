@echo off
echo You need to have pdoc3 installed to build the docs. ('pdoc' is a package and cannot be directly executed)
echo If you don't have it, you can install it with: pip install pdoc3
echo The docs will be built in ./docs
pause

python -m pdoc --template-dir pdoc --force -o docs --html .