"""
OmniUtils/
├── omniutils/                   # Diretório do pacote principal
│   ├── __init__.py              # Inicializa o pacote e pode expor os módulos principais
│   ├── text_utils.py            # Funções de manipulação de texto
│   ├── webpage_handler.py       # Funções para lidar com requisições e parsing de páginas
│   ├── check_settings.py        # Validação e carregamento de configurações
│   ├── dataframe_utils.py       # Utilitários para manipulação de DataFrames
│   ├── date_utils.py            # Funções para manipulação de datas
│   ├── dictionary_utils.py      # Funções para trabalhar com dicionários
│   ├── excel_operator.py        # Operações com arquivos Excel
│   ├── exceptions.py            # Definição de exceções personalizadas
│   ├── file_operator.py         # Funções para manipulação de arquivos
│   └── github.py                # Funções para interagir com a API do GitHub
│
├── tests/                       # Diretório com testes unitários
│   ├── __init__.py
│   ├── test_text_utils.py
│   ├── test_webpage_handler.py
│   ├── test_check_settings.py
│   ├── test_dataframe_utils.py
│   ├── test_date_utils.py
│   ├── test_dictionary_utils.py
│   ├── test_excel_operator.py
│   ├── test_exceptions.py
│   ├── test_file_operator.py
│   └── test_github.py
│
├── setup.py                     # Script de instalação (usando setuptools, por exemplo)
├── pyproject.toml               # Configuração do build (opcional, mas recomendado)
├── README.md                    # Documentação inicial e instruções de uso
├── LICENSE                      # Arquivo de licença (ex.: MIT, Apache, etc.)
└── requirements.txt             # Dependências necessárias para usar a biblioteca

OmniUtils: Uma coleção de utilitários para diversos propósitos, incluindo:
  - Processamento de textos (TextUtils)
  - Manipulação de páginas web (WebpageHandler)
  - Verificação e carregamento de configurações (check_settings)
  - Operações com DataFrames (DataFrameUtils)
  - Utilidades de datas (DateUtils e MonthType)
  - Operações com dicionários (DictionaryUtils)
  - Operações com planilhas Excel (ExcelOperator)
  - Tratamento de exceções customizadas (DataProcessorError, InvalidFileFormatError)
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
]
