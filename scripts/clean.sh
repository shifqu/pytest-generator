#!/bin/bash
set -euxo pipefail

poetry run isort pytest_generator/ tests/
poetry run black pytest_generator/ tests/
