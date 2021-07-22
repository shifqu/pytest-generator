#!/bin/bash
set -euxo pipefail

poetry run cruft check
find . -not -path '*/\.*' -not -path '*/__*' -not -path '*/tests/*' -type f \( -iname "*md" -o -iname "*txt" \) | poetry run xargs proselint
find scripts/ -type f -not -name '*py' | poetry run xargs shellcheck
poetry run isort --check --diff pytest_generator/ tests/
poetry run black --check pytest_generator/ tests/
poetry run pydocstyle pytest_generator/ tests/
poetry run flake8 pytest_generator/ tests/
poetry run mypy --ignore-missing-imports pytest_generator/
poetry run bandit -r pytest_generator/
poetry run safety check
