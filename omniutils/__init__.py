"""
OmniUtils: Uma coleção de utilitários para diversos propósitos, incluindo:
  - Processamento de textos (TextUtils)
  - Manipulação de páginas web (WebpageHandler)
  - Verificação e carregamento de configurações (check_settings)
  - Operações com DataFrames (DataFrameUtils)
  - Utilidades de datas (DateUtils e MonthType)
  - Operações com dicionários (DictionaryUtils)
  - Operações com planilhas Excel (ExcelOperator)
  - Tratamento de exceções customizadas (DataProcessorError,
    InvalidFileFormatError)
  - Operações com arquivos (FileOperator)
  - Funções para interagir com o GitHub (get_last_modified_date)
"""

from .check_settings import check_settings
from .dataframe_utils import DataFrameUtils
from .date_utils import DateUtils, MonthType
from .dictionary_utils import DictionaryUtils
from .excel_operator import ExcelOperator
from .exceptions import DataFrameFormatError, InvalidFileFormatError
from .file_operator import FileOperator
from .github import GitHubUtils
from .json_operator import JsonOperator
from .request_handler import RequestHandler
from .text_utils import TextUtils

__all__ = [
    "TextUtils",
    "RequestHandler",
    "check_settings",
    "DataFrameUtils",
    "DateUtils",
    "MonthType",
    "DictionaryUtils",
    "ExcelOperator",
    "DataFrameFormatError",
    "InvalidFileFormatError",
    "FileOperator",
    "GitHubUtils",
    "JsonOperator",
]
