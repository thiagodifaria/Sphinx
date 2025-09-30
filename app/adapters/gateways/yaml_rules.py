# src/sphinx/adapters/gateways/rule_yaml.py

from __future__ import annotations
import logging
from pathlib import Path

import yaml
from pydantic import ValidationError

from app.core.application.ports.gateways.rules import RuleRepositoryPort
from app.core.domain.models.rules import AnalysisRule

logger = logging.getLogger(__name__)


class YamlRuleRepository(RuleRepositoryPort):
    """
    Implementação da RuleRepositoryPort que carrega as regras de um arquivo YAML.

    Este adaptador encapsula a lógica de I/O de arquivo e o parsing de YAML.
    Ele utiliza o poder do Pydantic para validar a estrutura do arquivo de
    regras, garantindo que apenas regras válidas e bem-formadas sejam
    carregadas na aplicação.
    """
    def __init__(self, file_path: str):
        self._file_path = Path(file_path)
        self._rules: list[AnalysisRule] = []

    def get_all(self) -> list[AnalysisRule]:
        """Lê o arquivo YAML, valida e retorna uma lista de objetos AnalysisRule."""
        if self._rules:
            return self._rules
            
        if not self._file_path.exists():
            logger.warning(f"Arquivo de regras '{self._file_path}' não encontrado.")
            return []

        try:
            with open(self._file_path, "r") as f:
                data = yaml.safe_load(f)
            
            if not data or "rules" not in data:
                logger.warning(f"Arquivo de regras '{self._file_path}' está vazio ou malformado.")
                return []

            # A validação do Pydantic acontece aqui, convertendo o dicionário em objetos tipados.
            self._rules = [AnalysisRule(**rule_data) for rule_data in data["rules"]]
            logger.info(f"{len(self._rules)} regra(s) de análise carregada(s) de '{self._file_path}'.")
            return self._rules

        except (yaml.YAMLError, ValidationError) as e:
            logger.error(f"Erro ao carregar ou validar o arquivo de regras '{self._file_path}': {e}")
            return []
        except Exception as e:
            logger.error(f"Erro inesperado ao ler o arquivo de regras: {e}")
            return []