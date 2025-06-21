find . | grep  __pycache__ | xargs rm -fr
isort .
black .
flake8 .
pipenv requirements > requirements.txt
