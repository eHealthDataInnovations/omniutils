import importlib.util
import os
import sys
from pathlib import Path


def check_settings():
    """
    Carrega dinamicamente o arquivo de configurações 'settings.py' do projeto.

    Este método realiza as seguintes operações:
      1. Determina o diretório base do projeto com base na localização deste
         arquivo.
      2. Constrói o caminho absoluto para o arquivo 'settings.py'.
      3. Verifica se o arquivo 'settings.py' existe. Se não existir, levanta uma
         exceção FileNotFoundError informando o caminho esperado.
      4. Cria uma especificação de módulo para 'settings.py' e tenta carregá-lo
         como um módulo Python.
      5. Se a especificação ou o carregador (loader) não estiverem disponíveis,
         levanta uma exceção ImportError.
      6. Após carregar o módulo, o insere no dicionário sys.modules sob o nome
         "settings".
      7. Retorna o módulo 'settings' carregado, permitindo o acesso às suas
         variáveis e configurações.

    Returns:
        module: O módulo Python resultante da importação do arquivo
            'settings.py'.

    Raises:
        FileNotFoundError: Se o arquivo 'settings.py' não for encontrado no
            caminho construído.
        ImportError: Se não for possível carregar o módulo a partir do caminho
            especificado.

    Exemplo de uso:
    ```python
        settings = check_settings()
        print(settings.DEBUG)
    ```
    """
    BASE_DIR = (  # pylint: disable=invalid-name
        Path(__file__).resolve().parent.parent
    )  # pylint: disable=invalid-name
    settings_path = os.path.join(BASE_DIR, "settings.py")

    # Verificar se o arquivo settings.py existe
    if not os.path.isfile(settings_path):
        raise FileNotFoundError(
            f"O arquivo settings.py não existe no caminho {settings_path}."
        )

    # Importar settings.py como um módulo
    spec = importlib.util.spec_from_file_location("settings", settings_path)
    if spec is None or spec.loader is None:
        raise ImportError(
            f"Não foi possível carregar o módulo a partir do caminho: {settings_path}"
        )

    settings = importlib.util.module_from_spec(spec)
    sys.modules["settings"] = settings
    spec.loader.exec_module(settings)

    return settings
