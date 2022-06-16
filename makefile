sources = dremioarrow scripts tests
source = dremioarrow

.PHONY: test multi format lint unittest coverage pre-commit clean
test: format lint unittest coverage

multi:
	poetry run tox $(source)

format:
	poetry run isort $(sources)
	poetry run black $(sources)

lint:
	poetry run flake8 $(sources)
	poetry run mypy $(sources)

unittest:
	poetry run pytest

coverage:
	poetry run pytest --cov=$(source) --cov-branch --cov-report=term-missing tests

pre-commit:
	poetry run pre-commit run --all-files

clean:
	rm -rf .mypy_cache .pytest_cache
	rm -rf *.egg-info
	rm -rf .tox dist site
	rm -rf coverage.xml .coverage
