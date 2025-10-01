.PHONY: install lint format test typecheck all launch-ui

SHELL := /bin/bash

install:
	poetry install

lint:
	poetry run ruff check .

format:
	# Formata todo o código do projeto de acordo com as regras definidas.
	poetry run ruff format .

test:
	poetry run pytest

typecheck:
	poetry run mypy .

all: lint typecheck test
	@echo "All checks passed!"

launch-ui:
	start "Sphinx TUI" bash -c "poetry run sphinx; read -p 'Pressione Enter para sair...'"