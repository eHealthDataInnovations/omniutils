import logging
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union

from exceptions import InvalidFileFormatError

logger = logging.getLogger(__name__)


class FileOperator:
    """
    Esta classe fornece métodos para renomear arquivos (totalmente ou
    parcialmente), alterar extensões, extrair partes do caminho, copiar
    arquivos, verificar a existência de arquivos e diretórios, listar arquivos
    em um diretório com filtros e limpar diretórios.

    Todos os métodos são implementados como métodos de classe ou estáticos,
    permitindo seu uso sem a necessidade de instanciar a classe.
    """
    @classmethod
    def rename_file(
        cls,
        filename_path: str,
        new_name: Optional[str] = None,
        insert_text: Optional[str] = None,
    ) -> str:
        """
        Renomeia um arquivo dado seu caminho e o novo nome, ou adiciona um
        texto ao nome original.

        Parâmetros:
            filename_path (str): Caminho completo do arquivo a ser renomeado.
            new_name (Optional[str]): Novo nome completo para o arquivo. Se
                fornecido, o arquivo será renomeado completamente.
            insert_text (Optional[str]): Texto a ser inserido no nome do arquivo
                original, antes da extensão. Se fornecido, será inserido entre
                o nome original e a extensão.

        Retorna:
            str: O novo caminho completo do arquivo renomeado.

        Exemplos de uso:
        ```python
        filename_path = "/caminho/para/arquivo.txt"

        # Renomeia completamente o arquivo:
        novo_caminho = FileOperator.rename_file(filename_path,
                                                new_name="novo_nome.txt")
        print(novo_caminho)  # Exemplo: "/caminho/para/novo_nome.txt"

        # Adiciona um texto ao nome original:
        novo_caminho = FileOperator.rename_file(filename_path, insert_text="v2")
        print(novo_caminho)  # Exemplo: "/caminho/para/arquivo_v2.txt"
        ```
        """

        if new_name is None and insert_text is None:
            raise ValueError(
                "Argumentos new_name e word não não ser nulos. "
                "Informe ao menos um."
            )
        if new_name and not isinstance(new_name, str):
            raise InvalidFileFormatError(
                "O novo nome do arquivo deve ser uma string válida."
            )
        if insert_text and not isinstance(insert_text, str):
            raise InvalidFileFormatError(
                "O texto a ser inserido no novo nome do arquivo deve ser uma "
                "string válida."
            )

        if not os.path.isfile(filename_path):
            raise FileNotFoundError(
                f"O arquivo {filename_path} não foi encontrado."
            )

        directory = os.path.dirname(filename_path)

        new_path = None
        if new_name:
            new_path = os.path.join(directory, new_name)
        elif insert_text:
            filename = os.path.basename(filename_path)
            filename_without_extension, extension = os.path.splitext(filename)
            filename = f"{filename_without_extension}_{insert_text}{extension}"
            new_path = os.path.join(directory, filename)

        if new_path:
            os.rename(filename_path, new_path)

        logger.debug(f"Arquivo renomeado para: {new_path}")
        return new_path

    @classmethod
    def rename_file_extension(cls, file_path, new_extension):
        """
        Renomeia a extensão de um arquivo para uma nova extensão fornecida.

        Parâmetros:
            file_path (str): Caminho completo do arquivo original.
            new_extension (str): Nova extensão a ser aplicada (deve incluir o
                ponto, por exemplo, '.txt').

        Retorna:
            str: O novo caminho completo do arquivo com a nova extensão.

        Exemplos de uso:
        ```python
        novo_caminho = FileOperator.rename_file_extension(
            "/caminho/para/arquivo.txt", ".csv")
        print(novo_caminho)  # Exemplo: "/caminho/para/arquivo.csv"
        ```
        """
        if not new_extension.startswith("."):
            raise InvalidFileFormatError("A nova extensão deve começar com um "
                                         "ponto ('.').")

        path = Path(file_path)
        new_file_path = path.with_suffix(new_extension)

        path.rename(new_file_path)
        return new_file_path

    @classmethod
    def rename_file_extension_in_string(
        cls,
        file_path: Optional[str],
        new_extension: str,
        insert_text: Optional[str] = None,
    ) -> Optional[str]:
        """
        Renomeia a extensão de um caminho de arquivo (como string) e insere um
        texto entre o nome do arquivo e a nova extensão.

        Parâmetros:
            file_path (Optional[str]): Caminho completo do arquivo original
                como string.
            new_extension (str): Nova extensão a ser aplicada (deve incluir o
                ponto, por exemplo, '.txt').
            insert_text (Optional[str]): Texto a ser inserido entre o nome do
                arquivo e a extensão. Se vazio, nenhum texto será inserido.

        Retorna:
            Optional[str]: Novo caminho completo do arquivo com a nova extensão
                e o texto inserido, em forma de string. Retorna o próprio valor
                se file_path for None.

        Exemplos de uso:
        ```python
        novo_caminho = FileOperator.rename_file_extension_in_string(
            "/caminho/para/arquivo.txt", ".csv", insert_text="v2"
        )
        print(novo_caminho)  # Exemplo: "/caminho/para/arquivo_v2.csv"
        ```
        """
        if not file_path:
            return file_path

        if new_extension is None:
            raise InvalidFileFormatError("A nova extensão do arquivo não pode "
                                         "ser nula.")

        if not new_extension.startswith("."):
            raise InvalidFileFormatError("A nova extensão deve começar com um "
                                         "ponto ('.').")

        # Cria um objeto Path para manipular o caminho
        path = Path(file_path)

        # Insere o texto entre o nome do arquivo e a extensão
        if insert_text:
            new_file_name = f"{path.stem}_{insert_text}{new_extension}"
        else:
            new_file_name = f"{path.stem}{new_extension}"

        # Retorna o novo caminho com o nome modificado
        new_file_path = path.with_name(new_file_name)

        return str(new_file_path)

    @classmethod
    def get_latest_file(
        cls,
        directory: str,
        prefix: Optional[str] = None,
        extensions: Optional[Union[str, List[str]]] = None,
    ) -> Optional[str]:
        """
        Obtém o arquivo mais recente em um diretório, opcionalmente filtrando
        por prefixo e/ou extensões.

        Parâmetros:
            directory (str): Caminho para o diretório onde estão os arquivos.
            prefix (Optional[str]): Prefixo dos arquivos a serem considerados.
                Se None, considera todos os arquivos.
            extensions (Optional[Union[str, List[str]]]): Lista ou string (
                separada por vírgulas) de extensões dos arquivos a serem
                considerados. Se None, considera todas.

        Retorna:
            Optional[str]: O caminho para o arquivo mais recente que atenda aos
            filtros, ou None se nenhum arquivo for encontrado.

        Exemplos de uso:
        ```python
        arquivo_recente = FileOperator.get_latest_file(
            "/caminho/para/diretorio", prefix="log", extensions=".txt"
        )
        print(arquivo_recente)
        ```
        """
        latest_file = None
        latest_mod_time = None

        lextensions = []
        if isinstance(extensions, str):
            for extension in extensions.split(","):
                lextensions.append(extension)
        elif isinstance(extensions, list):
            lextensions = extensions
        elif extensions is not None:
            raise InvalidFileFormatError(f"{type(extensions)} não suportado.")

        for filename in os.listdir(directory):
            if (prefix is None or filename.startswith(prefix)) and (
                lextensions is None
                or any(filename.endswith(ext) for ext in lextensions)
            ):
                file_path = os.path.join(directory, filename)
                file_mod_time = os.path.getmtime(file_path)

                if latest_mod_time is None or file_mod_time > latest_mod_time:
                    latest_mod_time = file_mod_time
                    latest_file = file_path

        return latest_file

    @staticmethod
    def extract_directory_path(filename_path: str) -> str:
        """
        Retorna o caminho do diretório a partir do caminho completo de um
        arquivo.

        Parâmetros:
            filename_path (str): Caminho completo do arquivo.

        Retorna:
            str: Caminho do diretório que contém o arquivo.

        Exemplos de uso:
        ```python
        dir_path = FileOperator.extract_directory_path(
            "/caminho/para/arquivo.txt")
        print(dir_path)  # Exemplo: "/caminho/para"
        ```
        """
        return os.path.dirname(filename_path)

    @classmethod
    def extract_filename(cls, file_path: Optional[str]) -> Optional[str]:
        """
        Extrai o nome do arquivo a partir do caminho completo fornecido.

        Parâmetros:
            file_path (Optional[str]): Caminho completo do arquivo.

        Retorna:
            Optional[str]: Nome do arquivo ou None se file_path for None.

        Exemplos de uso:
        ```python
        nome = FileOperator.extract_filename("/caminho/para/arquivo.txt")
        print(nome)  # Exemplo: "arquivo.txt"
        ```
        """
        if not file_path:
            return None
        return os.path.basename(file_path)

    @classmethod
    def extract_extension(cls, file_path: Optional[str]) -> Optional[str]:
        """
        Extrai a extensão de um arquivo a partir do caminho completo.

        Parâmetros:
            file_path (Optional[str]): Caminho completo do arquivo.

        Retorna:
            Optional[str]: Extensão do arquivo (incluindo o ponto), ou None se
            file_path for None.

        Exemplos de uso:
        ```python
        ext = FileOperator.extract_extension("/caminho/para/arquivo.txt")
        print(ext)  # Exemplo: ".txt"
        ```
        """
        extension = None
        if file_path:
            filename = os.path.basename(file_path)
            _, extension = os.path.splitext(filename)
        return extension

    @classmethod
    def get_file_timestamps(cls, filename_path: str) -> dict:
        """
        Retorna um dicionário com a data de criação e a data da última
        modificação de um arquivo.

        Parâmetros:
            filename_path (str): Caminho completo do arquivo.

        Retorna:
            dict: Dicionário com as chaves 'creation_time' e 'last_modified',
                contendo os respectivos valores como objetos datetime.

        Exemplos de uso:
        ```python
        timestamps = FileOperator.get_file_timestamps(
            "/caminho/para/arquivo.txt")
        print(timestamps["creation_time"], timestamps["last_modified"])
        ```
        """
        if not cls.file_exists(filename_path):
            raise FileNotFoundError(
                f"O arquivo {filename_path} não foi encontrado."
            )

        # Obter a data de criação do arquivo como float e convertê-la para
        # datetime
        creation_timestamp = os.path.getctime(filename_path)
        creation_time = datetime.fromtimestamp(creation_timestamp)

        # Obter a data da última modificação do arquivo como float e
        # convertê-la para datetime
        modification_timestamp = os.path.getmtime(filename_path)
        last_modified = datetime.fromtimestamp(modification_timestamp)

        file_info = {
            "creation_time": creation_time,
            "last_modified": last_modified,
        }
        logger.debug(f"File info: {file_info}")
        return file_info

    @classmethod
    def is_file_creation_date_today(cls, filename_path: str) -> bool:
        """
        Verifica se a data de criação do arquivo é igual à data de hoje.

        Parâmetros:
            filename_path (str): Caminho completo do arquivo.

        Retorna:
            bool: True se a data de criação for igual à data de hoje; caso
                contrário, False.

        Exemplos de uso:
        ```python
        resultado = FileOperator.is_file_creation_date_today(
            "/caminho/para/arquivo.txt")
        print(resultado)  # Exemplo: True ou False
        ```
        """
        # Obtém o tempo de criação do arquivo em segundos desde a época (epoch)
        file_info = cls.get_file_timestamps(filename_path)

        # Converte para datetime
        file_last_modified_date = file_info["last_modified"].date()

        # Obtém a data de hoje
        today_date = datetime.today().date()

        # Retorna True se as datas forem iguais, False caso contrário
        return file_last_modified_date == today_date

    @classmethod
    def create_directory_if_not_exists(cls, directory_path: str) -> str:
        """
        Cria uma árvore de diretórios se ela não existir.

        Parâmetros:
            directory_path (str): Caminho da árvore de diretórios a ser criada,
                                  no formato 'dir/subdir1/subdir2'.

        Retorna:
            str: O caminho do diretório criado ou existente.

        Exemplos de uso:
        ```python
        dir_created = FileOperator.create_directory_if_not_exists(
            "/caminho/para/diretorio/subdir")
        print(dir_created)  # Exemplo: "/caminho/para/diretorio/subdir"
        ```
        """
        path = Path(directory_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Diretório '{directory_path}' criado.")
        else:
            logger.debug(f"Diretório '{directory_path}' já existe.")
        return directory_path

    @classmethod
    def clean_directory(cls, directory: Optional[str] = None):
        """
        Remove todos os arquivos e subdiretórios dentro de um diretório
        especificado.

        Parâmetros:
            directory (Optional[str]): Caminho para o diretório a ser limpo.
                                       Se não especificado, a operação será
                                       ignorada.

        Exemplos de uso:
        ```python
        FileOperator.clean_directory("/caminho/para/diretorio")
        ```
        """
        if directory is None:
            logger.warning("Diretório não especificado. Operação ignorada.")
            return

        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Remove arquivos ou links simbólicos
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Remove subdiretórios
            except FileNotFoundError as e:
                logger.warning(
                    f"Arquivo não encontrado ao tentar deletar {file_path}. "
                    f"Ignorando: {e}"
                )
            except PermissionError as e:
                logger.error(
                    f"Permissão negada ao tentar deletar {file_path}. "
                    f"Razão: {e}"
                )
            except OSError as e:
                logger.error(
                    f"Erro ao acessar ou deletar {file_path}. Razão: {e}"
                )

    @classmethod
    def file_exists(cls, filename_path: str) -> bool:
        """
        Verifica se um caminho (arquivo ou diretório) existe.

        Parâmetros:
            filename_path (str): Caminho do arquivo ou diretório.

        Retorna:
            bool: True se o caminho existir; caso contrário, False.

        Exemplos de uso:
        ```python
        existe = FileOperator.file_exists("/caminho/para/arquivo.txt")
        print(existe)  # Exemplo: True
        ```
        """
        try:
            return os.path.exists(filename_path)
        except TypeError:
            return False

    @classmethod
    def directory_exists(cls, dir_path):
        """
        Verifica se o caminho fornecido é um diretório existente.

        Parâmetros:
            dir_path (str): Caminho do diretório.

        Retorna:
            bool: True se for um diretório existente; caso contrário, False.

        Exemplos de uso:
        ```python
        existe_dir = FileOperator.directory_exists("/caminho/para/diretorio")
        print(existe_dir)  # Exemplo: True
        ```
        """
        try:
            return os.path.isdir(dir_path)
        except TypeError:
            return False

    @classmethod
    def list_files(
        cls, directory_path: str, prefix=None, suffix=None, extensions=None
    ):
        """
        Lista todos os arquivos em um diretório, aplicando filtros opcionais
        por prefixo, sufixo e extensões.

        Parâmetros:
            directory_path (str): Caminho do diretório (obrigatório).
            prefix (Optional[str]): Prefixo dos arquivos a serem considerados
                (opcional).
            suffix (Optional[str]): Sufixo dos arquivos a serem considerados
                (opcional).
            extensions (Optional[Union[str, List[str]]]): Lista ou string
                (separada por vírgulas) de extensões dos arquivos a serem
                considerados (opcional).

        Retorna:
            List[str]: Lista de caminhos completos dos arquivos que correspondem
                aos filtros.

        Exemplos de uso:
        ```python
        arquivos = FileOperator.list_files("/caminho/para/diretorio",
                                           prefix="log", extensions=".txt")
        print(arquivos)
        ```
        """
        # Lista para armazenar os arquivos que correspondem aos filtros
        matched_files = []

        # Itera sobre os arquivos no diretório
        for root, _, files in os.walk(directory_path):
            for file in files:
                # Verifica o prefixo, se fornecido
                if prefix and not file.startswith(prefix):
                    continue
                # Verifica o sufixo, se fornecido
                if suffix and not file.endswith(suffix):
                    continue
                # Verifica a extensão, se fornecida
                if extensions and not any(
                    file.endswith(ext) for ext in extensions
                ):
                    continue
                # Adiciona o caminho completo do arquivo à lista
                matched_files.append(os.path.join(root, file))

        return matched_files

    @classmethod
    def delete_file(cls, filename_path: str):
        """
        Exclui o arquivo especificado pelo caminho.

        Parâmetros:
            filename_path (str): Caminho completo do arquivo a ser excluído.

        Exceções:
            FileNotFoundError: Se o arquivo não existir.

        Exemplos de uso:
        ```python
        FileOperator.delete_file("/caminho/para/arquivo.txt")
        ```
        """
        if cls.file_exists(filename_path):
            os.remove(filename_path)
            logger.debug(f"Arquivo {filename_path} foi excluído com sucesso.")
        else:
            logger.debug(f"Arquivo {filename_path} não encontrado.")

    @classmethod
    def check_path_like(cls, path: str) -> bool:
        """
        Verifica se uma string pode ser interpretada como um caminho válido.

        Parâmetros:
            path (str): A string que representa o caminho a ser verificado.

        Retorna:
            bool: True se a string for um caminho válido.

        Exceções:
            InvalidFileFormatError: Se o caminho não for do tipo str ou não
                puder ser interpretado como um Path.

        Exemplos de uso:
        ```python
        is_valid = FileOperator.check_path_like("/caminho/para/diretorio")
        print(is_valid)  # Exemplo: True
        ```
        """
        if not isinstance(path, str):
            logger.error(f"O caminho '{path}' não é válido.")
            raise InvalidFileFormatError("O caminho deve ser uma string.")

        try:
            # Tenta criar um objeto Path; falha se o formato for inválido
            Path(path)
            return True
        except (ValueError, TypeError) as err:
            logger.error(f"O caminho '{path}' não é válido. Errr: {err}")
            raise InvalidFileFormatError(f"O caminho '{path}' não é válido.") \
                from err

    @classmethod
    def sanitize_filename(cls, filename_path: str) -> str:
        """
        Substitui caracteres especiais no nome do arquivo por '_' (underline),
        ignorando o caminho do diretório.

        Parâmetros:
            filename_path (str): Caminho completo do arquivo.

        Retorna:
            str: Caminho completo do arquivo com o nome sanitizado.

        Exemplos de uso:
        ```python
        novo_caminho = FileOperator.sanitize_filename(
            "/caminho/para/arquivo@invalido!.txt")
        print(novo_caminho)  # Exemplo: "/caminho/para/arquivo_invalido_.txt"
        ```
        """
        # Separa o diretório e o nome do arquivo
        dir_path, filename = os.path.split(filename_path)

        # Sanitiza o nome do arquivo
        sanitized_filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)

        # Junta novamente o diretório e o nome do arquivo sanitizado
        return os.path.join(dir_path, sanitized_filename)

    @staticmethod
    def copy_file(src_filename_path: str, dest_filename_path: str) -> None:
        """
        Copia um arquivo de um caminho de origem para um caminho de destino.

        Parâmetros:
            src_filename_path (str): Caminho completo do arquivo de origem.
            dest_filename_path (str): Caminho completo do arquivo de destino.

        Exceções:
            FileNotFoundError: Se o arquivo de origem não existir.
            IOError: Se ocorrer falha durante a cópia.

        Exemplos de uso:
        ```python
        FileOperator.copy_file("/caminho/para/origem.txt",
                               "/caminho/para/destino.txt")
        ```
        """
        # Verifica se o arquivo de origem existe
        if not os.path.isfile(src_filename_path):
            raise FileNotFoundError(
                f"Arquivo de origem '{src_filename_path}' não encontrado."
            )

        # Verifica se o diretório de destino existe, caso contrário, cria o
        # diretório
        dest_directory = os.path.dirname(dest_filename_path)
        if not os.path.exists(dest_directory):
            os.makedirs(dest_directory, exist_ok=True)

        try:
            shutil.copy2(src_filename_path, dest_filename_path)
            print(
                f"Arquivo copiado de {src_filename_path} para "
                f"{dest_filename_path}"
            )
        except IOError as e:
            print(f"Erro ao copiar o arquivo: {e}")
            raise
