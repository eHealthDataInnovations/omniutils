import logging
from typing import Optional

logger = logging.getLogger(__name__)


class OmniUtilsException(Exception):
    """Exceção base para erros no processamento de dados."""
    def __init__(self, message: Optional[str] = None):
        logger.error(message)
        super().__init__(message)


class InvalidFileFormatError(OmniUtilsException):
    """Exceção para formatos inválidos de arquivos de dados."""
    def __init__(self, message="Formato inválido para arquivo de dados."):
        super().__init__(message)


class DataFrameFormatError(OmniUtilsException):
    """Exceção levantada para erros no formato do conjunto de dados."""
    def __init__(self, message="Erro no formato do conjunto de dados."):
        super().__init__(message)