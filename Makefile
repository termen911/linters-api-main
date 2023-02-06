PYTHON = venv/bin/python

fmt:
	make black isort

check:
	make EXIT_ZERO="no" -j 6 black isort flakeheaven mypy test

deploy:
	make check
	cf push

run-local:
	uvicorn app.main:app --port 8002

run-prod:
	uvicorn app.main:app --host 0.0.0.0 --port 80

# Installation & update
dev-install:
	python -m pip install -r requirements.txt
	python -m pip install -r requirements-dev.txt
	pre-commit install
	pre-commit install --hook-type commit-msg

deps-update:
	pcu -u requirements.txt
	pcu -u requirements-dev.txt
	pre-commit autoupdate

# Migrations
make-migrations:
    ifeq ($(m), )
		# Name cannot be empty
		# Usage: make make-migrations m=name
    else
		python -m alembic revision --autogenerate -m "$(m)"
    endif

migrate:
	python -m alembic upgrade head

# Python tests & linters:
test:
	python -m pytest

black:
    ifeq ($(EXIT_ZERO), no)
		python -m black . --check
    else
		python -m black .
    endif

isort:
    ifeq ($(EXIT_ZERO), no)
		python -m isort . --check
    else
		python -m isort .
    endif

flakeheaven:
    ifeq ($(EXIT_ZERO), no)
		python -m flakeheaven lint .
    else
		python -m flakeheaven lint . --exit-zero
    endif

mypy:
	python -m mypy .
