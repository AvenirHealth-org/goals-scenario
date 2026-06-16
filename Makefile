.PHONY: install
install: ## Install the virtual environment and install the pre-commit hooks
	@echo "🚀 Creating virtual environment using uv"
	@uv sync
	@uv run pre-commit install

.PHONY: check
check: ## Run code quality tools.
	@echo "🚀 Checking lock file consistency with 'pyproject.toml'"
	@uv lock --locked
	@echo "🚀 Linting code: Running pre-commit"
	@uv run pre-commit run -a
	@echo "🚀 Static type checking: Running ty"
	@uv run ty check

.PHONY: audit
audit: ## Run pip-audit.
	@echo "🚀 Vulnerability check: Running pip-audit"
## CVE-2024-23342: safe to ignore for now, we should switch to python-jose[cryptography]
## to avoid vulnerable ecdsa package for serialization but that still depends on
## ecdsa so won't resolve this
## CVE-2026-44432 and CVE-2026-44431: vulnerabilities in urllib, pulled in by
## avenir-common via azure-storage-blob. We should be able to remove the
## dependency on avenir-storage-blob in the future or at least update it to
## a newer version once one has been released.
## GHSA-537c-gmf6-5ccf: vulnerabilities in cartography package pulled in
## by azure-storage-blob fixed in 48.0.1
	@uv run pip-audit --desc -s osv --ignore-vuln CVE-2024-23342 --ignore-vuln CVE-2026-44432 --ignore-vuln CVE-2026-44431 --ignore-vuln GHSA-537c-gmf6-5ccf

.PHONY: test
test: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@uv run python -m pytest --cov --cov-config=pyproject.toml --cov-report=xml

.PHONY: build
build: clean-build ## Build wheel file
	@echo "🚀 Creating wheel file"
	@uvx --from build pyproject-build --installer uv

.PHONY: clean-build
clean-build: ## Clean build artifacts
	@echo "🚀 Removing build artifacts"
	@uv run python -c "import shutil; import os; shutil.rmtree('dist') if os.path.exists('dist') else None"

.PHONY: docs-test
docs-test: ## Test if documentation can be built without warnings or errors
	@uv run mkdocs build -s

.PHONY: docs
docs: ## Build and serve the documentation
	@uv run mkdocs serve

.PHONY: pjnz-import-code
pjnz-import-code: ## Run the script to update vendored PJNZ import code
	@uv run ./scripts/update_pjnz_import_code.py

.PHONY: help
help:
	@uv run python -c "import re; \
	[[print(f'\033[36m{m[0]:<20}\033[0m {m[1]}') for m in re.findall(r'^([a-zA-Z_-]+):.*?## (.*)$$', open(makefile).read(), re.M)] for makefile in ('$(MAKEFILE_LIST)').strip().split()]"

.DEFAULT_GOAL := help
