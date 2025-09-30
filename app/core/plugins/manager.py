# src/sphinx/core/plugins/manager.py

from __future__ import annotations
import importlib.util
import inspect
import logging
from pathlib import Path

from app.core.plugins.interfaces import AnalysisRulePlugin, SphinxPlugin

logger = logging.getLogger(__name__)


class PluginManager:
    """
    Gerencia a descoberta, carregamento e registro de plugins externos.
    """
    def __init__(self, plugins_dir: str):
        self._plugins_dir = Path(plugins_dir)
        self._analysis_rule_plugins: list[AnalysisRulePlugin] = []

    def discover_and_load(self):
        """
        Varre o diretório de plugins, importa os módulos Python e registra as
        classes de plugin válidas encontradas.
        """
        logger.info(f"Procurando por plugins em '{self._plugins_dir}'...")
        if not self._plugins_dir.is_dir():
            logger.warning(f"Diretório de plugins '{self._plugins_dir}' não encontrado.")
            return

        for file_path in self._plugins_dir.glob("*.py"):
            if file_path.name == "__init__.py":
                continue
            
            try:
                # Importação dinâmica do arquivo Python como um módulo.
                spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
                if not spec or not spec.loader:
                    continue
                
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Inspeciona o módulo em busca de classes que implementam nossas interfaces.
                for _, cls in inspect.getmembers(module, inspect.isclass):
                    if issubclass(cls, SphinxPlugin) and cls is not SphinxPlugin and not inspect.isabstract(cls):
                        self._register_plugin(cls())
            
            except Exception as e:
                logger.error(f"Falha ao carregar o plugin '{file_path.name}': {e}")
        
        logger.info(f"Carregamento de plugins concluído. {len(self.get_analysis_rule_plugins())} plugin(s) de análise registrados.")

    def _register_plugin(self, plugin_instance: SphinxPlugin):
        """Registra uma instância de plugin na categoria apropriada."""
        if isinstance(plugin_instance, AnalysisRulePlugin):
            self._analysis_rule_plugins.append(plugin_instance)
            logger.debug(f"Plugin de Análise '{plugin_instance.name}' registrado.")
        else:
            logger.warning(f"Plugin '{plugin_instance.name}' de tipo desconhecido não foi registrado.")

    def get_analysis_rule_plugins(self) -> list[AnalysisRulePlugin]:
        """Retorna todos os plugins de regra de análise registrados."""
        return self._analysis_rule_plugins