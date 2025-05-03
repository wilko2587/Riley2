.PHONY: install lint test clean package

install:
	pip install -r requirements.txt

lint:
	ruff src/ tests/

test:
	pytest

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -name "*.pyc" -delete

package:
	python src/riley2/scripts/package_current_version.py