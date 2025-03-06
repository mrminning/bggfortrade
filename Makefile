setup:
	python3 -m venv venv

install:
	pip install --upgrade pip &&\
        pip install -r requirements.txt

test:
	python -m pytest -vv

lint:
	pylint  --disable=R,C main.py

all: install lint test