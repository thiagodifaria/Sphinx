from __future__ import annotations
import logging

from app.core.application.state import AppState
from app.core.domain.models.iac import (
    IaCFile,
    TerraformBackendConfig,
    TerraformConfiguration,
)
from app.infrastructure.config.settings import Settings

logger = logging.getLogger(__name__)


class BuildTerraformConfigUseCase:
    """
    Constrói um objeto de configuração Terraform completo, resolvendo qual backend
    utilizar com base no estado da aplicação e nas configurações globais.
    """

    def __init__(self, app_state: AppState, settings: Settings):
        self._app_state = app_state
        self._settings = settings

    def execute(self, main_file: IaCFile) -> TerraformConfiguration:
        """
        Executa a lógica de construção da configuração.

        Args:
            main_file: O arquivo IaC principal para a operação.

        Returns:
            Um objeto TerraformConfiguration completo e pronto para ser usado.
        """
        backend_config = None

        if self._app_state.active_workspace:
            backend_config = self._app_state.active_workspace.backend_config
            logger.info(
                f"A usar o backend do workspace ativo: '{self._app_state.active_workspace.name}'"
            )
        elif (
            self._settings.tf_backend_s3_bucket
            and self._settings.tf_backend_s3_key
            and self._settings.tf_backend_s3_region
        ):
            backend_config = TerraformBackendConfig(
                bucket=self._settings.tf_backend_s3_bucket,
                key=self._settings.tf_backend_s3_key,
                region=self._settings.tf_backend_s3_region,
            )
            logger.info("A usar o backend S3 das configurações globais (.env).")

        return TerraformConfiguration(
            main_file=main_file, backend_config=backend_config
        )