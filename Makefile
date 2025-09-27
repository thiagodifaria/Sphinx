# Makefile

.PHONY: install lint format test typecheck all

# Define o interpretador a ser usado.
SHELL := /bin/bash

install:
	# Instala todas as dependências do projeto, incluindo as de desenvolvimento.
	poetry install

lint:
	# Executa o linter para verificar a qualidade e o estilo do código.
	poetry run ruff check .

format:
	# Formata todo o código do projeto de acordo com as regras definidas.
	poetry run ruff format .

test:
	# Executa a suíte de testes unitários e de integração.
	poetry run pytest

typecheck:
	# Executa o MyPy para fazer a checagem estática de tipos.
	poetry run mypy .

all: lint typecheck test
	# Atalho para executar as principais verificações de qualidade.
	@echo "All checks passed!"