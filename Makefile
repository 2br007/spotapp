# start uvicorn server
run:
	uvicorn spotapp:app --reload --port 8000

seed:
	python scripts/seed_gijon.py

# check syntax
lintapi:
	flake8 api

lint:
	flake8 tests

# run tests
test:
	PYTHONPATH=. pytest --cov-report term \
	--cov=. \
	--cov-config=tests/.coveragerc \
	tests/

cov:
	PYTHONPATH=. pytest --cov-report html \
	--cov=. \
	--cov-config=tests/.coveragerc \
	tests/
