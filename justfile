# ABOUTME: Justfile for project automation and development tasks
# ABOUTME: Contains recipes for linting, formatting, type checking, and installation

# Default recipe - show available commands
default:
    @just --list

# Install all dependencies including dev dependencies
install-dev:
    uv add --dev ruff mypy pytest types-reportlab

# Install only production dependencies
install:
    uv sync

# Run ruff linting on the codebase with auto-fix
lint:
    uv run ruff check --fix .

# Run ruff formatting
format:
    uv run ruff format .

# Run ruff formatting check (CI mode)
format-check:
    uv run ruff format --check .

# Run mypy type checking
typecheck:
    cd demos/module_one_01_foundations_ai && uv run mypy app.py
    cd demos/module_one_02_adding_durability && uv run mypy --ignore-missing-imports activities.py worker.py workflow.py starter.py models.py
    cd demos/module_one_03_human_in_the_loop && uv run mypy --ignore-missing-imports activities.py worker.py workflow.py starter.py

# Run all quality checks (lint, format check, typecheck)
check: lint format-check typecheck
    @echo "All checks passed"

# Fix auto-fixable linting issues
fix:
    uv run ruff check --fix .
    uv run ruff format .

# Clean up Python cache files and directories
clean:
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    find . -type f -name "*.pyo" -delete
    find . -type f -name "*.pyd" -delete
    find . -type f -name ".coverage" -delete
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true

# Update all dependencies to their latest versions
update-deps:
    uv lock --upgrade

# Show current Python and package versions
versions:
    @echo "Python version:"
    @python --version
    @echo "\nInstalled packages:"
    @uv pip list


# Workshop Running Commands

# Run the Temporal Development Server
temporal:
    temporal server start-dev --ui-port 8080

# Run the demo for 01-AI-Agent
demo-1:
    uv run demos/module_one_01_foundations_ai/app.py

# Run the demo for 02-Add-Durability
demo-2:
    uv run demos/module_one_02_adding_durability/starter.py

# Run the worker for 02-Add-Durability
demo-2-worker:
    uv run demos/module_one_02_adding_durability/worker.py

# Run the demo for 03-Human-in-the-Loop
demo-3:
    uv run demos/module_one_03_human_in_the_loop/starter.py

# Run the worker for 03-Human-in-the-Loop
demo-3-worker:
    uv run demos/module_one_03_human_in_the_loop/worker.py