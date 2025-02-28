import logging
import os
import time
from datetime import datetime, timedelta
from http.client import IncompleteRead
from typing import Dict, Optional

import htmldate  # type: ignore
import requests
import requests_cache  # type: ignore
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.exceptions import (
    ChunkedEncodingError,
)
from requests.exceptions import (
    ConnectionError as RequestsConnectionError,  # Renomeia a importação
)
from requests.exceptions import (
    RequestException,
    Timeout,
)
from requests_cache import CachedSession
from urllib3 import Retry

from .check_settings import check_settings
from .file_operator import FileOperator

logger = logging.getLogger(__name__)

settings = check_settings()

requests_cache_expire_after_days = (
    settings.get_requests_cache_expire_after_days()
)

# Configuração do cache
requests_cache.install_cache("request_http_cache", backend="sqlite")

TIMEOUT_CONNECT = 10
TIMEOUT_READ = 20
DEFAULT_RETRIES = 3
DEFAULT_BACKOFF_FACTOR = 0.5
DEFAULT_STATUS_FORCELIST = [
    429,  # Too Many Requests -  Indica que o cliente enviou muitas requisições
    # em um curto período de tempo.
    500,  # Internal Server Error -  Um erro genérico indicando que o servidor
    # encontrou uma condição inesperada que impediu o processamento da
    # requisição.
    502,  # Bad Gateway -  Indica que o servidor (ou gateway) recebeu uma
    # resposta inválida do servidor upstream (servidor de origem).
    503,  # Service Unavailable -  O servidor está temporariamente indisponível,
    # geralmente devido a manutenção ou sobrecarga.
    504,  # Gateway Timeout - Indica que o servidor (ou gateway) não recebeu uma
    # resposta do servidor upstream dentro do tempo limite.
    520,  # Web Server Is Returning an Unknown Erro - este é um código de status
    # não padrão gerado pelo Cloudflare. Indica um problema desconhecido na
    # comunicação entre o Cloudflare e o servidor de origem.
]


class RequestHandler:
    """
    Gerencia requisições HTTP com cache, retry automático e processamento
    de respostas, além de oferecer métodos auxiliares como verificação de
    acesso à internet, download de arquivos e extração de conteúdo HTML.

    Métodos:
        - get_session() -> requests.Session:
            Retorna uma sessão HTTP configurada com cache.
        - request_with_retry(url: str,
                             method: str, **kwargs) -> requests.Response:
            Realiza uma requisição HTTP com retry automático.
        - get_last_modified(url: str) -> Optional[datetime]:
            Obtém a data de última modificação de uma página web.
        - download_file(url: str, filename_path: str,
                        headers: Optional[Dict]) -> str:
            Faz o download de um arquivo a partir de uma URL e o salva
            localmente.
        - get_soap_by_url(url: str) -> BeautifulSoup:
            Retorna um objeto BeautifulSoup com o conteúdo HTML obtido de uma
            URL.
        - get_soap_from_file(file_path: str) -> BeautifulSoup:
            Lê um arquivo HTML e retorna um objeto BeautifulSoup.
        - check_internet_access(url: str, timeout: int) -> bool:
            Verifica a disponibilidade de acesso à internet.
        - show_cache_info(show_urls: bool) -> None:
            Exibe informações sobre o cache de requisições HTTP.
    """

    _session = None

    @classmethod
    def get_session(cls):
        """
        Retorna uma sessão HTTP configurada com cache.

        Parâmetros:
            Nenhum.

        Retorna:
            - requests.Session: Sessão HTTP configurada com cache.

        Exemplos de uso:
        ```python
        session = RequestHandler.get_session()
        response = session.get("https://example.com")
        print(response.status_code)
        ```
        """
        if cls._session is None:
            session = CachedSession(
                "request_http_cache",
                # Habilita o uso do diretório de cache padrão do usuário
                # (dependente do sistema operacional
                use_cache_dir=True,
                # Respeita, prioritariamente os cabeçalhos Cache-Control das
                # respostas HTTP, se existir, para determinar a validade do
                # cache.
                cache_control=True,
                # Define o tempo de expiração do cache para um período de dias.
                # Se `cache_control=True`, o tempo de expiração será ignorado.
                expire_after=timedelta(days=requests_cache_expire_after_days),
                # Define os códigos HTTP que serão armazenados no cache. No
                # caso, respostas com código 200 (sucesso) e 400 (erro do
                # cliente) serão armazenadas.
                allowable_codes=[200, 400],
                # Define os métodos HTTP cujas respostas serão armazenadas no
                # cache
                allowable_methods=["GET", "POST"],
                # Exclui o parâmetro api_key ao comparar requisições para
                # verificar se uma resposta armazenada pode ser usada. Isso
                # impede que chaves de API diferentes invalidem o cache.
                ignored_parameters=["api_key"],
                # Inclui o cabeçalho Accept-Language como critério para
                # diferenciar as respostas no cache. Por exemplo, respostas para
                # diferentes idiomas serão armazenadas separadamente.
                match_headers=["Accept-Language"],
                # Quando ocorre um erro de requisição (como falha na conexão
                # ou timeout), o sistema usa dados do cache considerados
                # "obsoletos", se disponíveis. Isso evita interrupções no
                # serviço, mesmo que os dados estejam desatualizados.
                stale_if_error=True,
            )
            cls._session = session
        return cls._session

    @classmethod
    def request_with_retry(
        cls,
        url: str,
        method: str = "GET",
        **kwargs,
    ) -> requests.Response:
        """
        Realiza uma requisição HTTP com tentativas automáticas de retry em caso
        de falhas transitórias.

        Parâmetros:
            - url (str): A URL para a requisição.
            - method (str): Método HTTP a ser utilizado ("GET", "POST", "PUT"
                ou "DELETE").
            - **kwargs: Argumentos adicionais para a requisição, como:
                * data (dict): Dados para requisições POST/PUT.
                * json (dict): Dados JSON para requisições POST/PUT.
                * params (dict): Parâmetros de consulta.
                * headers (dict): Cabeçalhos HTTP.
                * verify (bool): Verificação do certificado SSL.
                * stream (bool): Se a resposta deve ser baixada em streaming.
                * timeout_connect (int): Tempo limite para conexão.
                * timeout_read (int): Tempo limite para leitura.
                * retries (int): Número de tentativas.
                * backoff_factor (float): Fator de espera entre tentativas.
                * status_forcelist (list): Lista de códigos HTTP para retry.

        Retorna:
            - requests.Response: Objeto de resposta HTTP resultante da
              requisição.

        Exceções:
            - HTTPError, ReadTimeout, RequestsConnectionError, Timeout,
              RetryError, RequestException.

        Exemplos de uso:
        ```python
        response = RequestHandler.request_with_retry("https://example.com",
                                                     method="GET")
        print(response.json())
        ```
        """

        # Define opções padrão
        verify = kwargs.get("verify", False)
        stream = kwargs.get("stream", False)
        headers = kwargs.get("headers", {})
        data = kwargs.get("data", None)
        json_data = kwargs.get("json", None)
        params = kwargs.get("params", None)
        timeout_connect = kwargs.get("timeout_connect", TIMEOUT_CONNECT)
        timeout_read = kwargs.get("timeout_read", TIMEOUT_READ)
        retries = kwargs.get("retries", DEFAULT_RETRIES)
        backoff_factor = kwargs.get("backoff_factor", DEFAULT_BACKOFF_FACTOR)
        status_forcelist = kwargs.get(
            "status_forcelist", DEFAULT_STATUS_FORCELIST
        )

        # Criação e configuração da sessão HTTP
        session = cls.get_session()

        # Configuração da estratégia de retry com backoff exponencial
        retry_strategy = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods=["GET", "POST", "PUT", "DELETE"],
            # Métodos suportados para retry
        )

        # Adaptador HTTP com a estratégia de retry
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        try:
            logger.debug(
                "Realizando %s em %s ... kwargs: %s ...",
                method,
                url,
                str(kwargs),
            )

            # Mapeamento de métodos HTTP suportados
            http_methods = {
                "GET": session.get,
                "POST": session.post,
                "PUT": session.put,
                "DELETE": session.delete,
            }

            # Verifica se o método HTTP fornecido é válido
            if method.upper() not in http_methods:
                raise ValueError(
                    f"Método HTTP inválido: {method}. Use 'GET', 'POST', 'PUT' "
                    f"ou 'DELETE'."
                )

            # Realiza a requisição HTTP de acordo com o método especificado
            response = http_methods[method.upper()](
                url,
                headers=headers,
                params=params,
                data=data,
                json=json_data,
                verify=verify,
                stream=stream,
                timeout=(timeout_connect, timeout_read),
            )

            # Tratamento especial para código 429 (Too Many Requests)
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                logger.warning(
                    "Retry-After definido. Tentando novamente em %s segundos...",
                    retry_after,
                )
                time.sleep(retry_after)

            # Levanta exceção se houver erro na resposta HTTP
            response.raise_for_status()

            logger.debug("Requisição %s para %s bem-sucedida!", method, url)

            return response

        except requests.exceptions.HTTPError as err:
            logger.error(
                "Erro HTTP ao acessar %s. Código: {err.response.status_code}, "
                "Erro: %s", url, err,
            )
            raise
        except requests.exceptions.ReadTimeout as err:
            logger.error(
                "O servidor está demorando muito para responder. Error: %s", err
            )
            raise
        except RequestsConnectionError as err:
            logger.warning(
                "Erro de conexão ao acessar o servidor. Erro: %s", err
            )
            raise
        except requests.exceptions.Timeout as err:
            logger.warning("Tempo limite excedido. Erro: %s ", err)
            raise
        except requests.exceptions.RetryError as err:
            logger.error(
                "Excedido o número máximo de tentativas devido a falhas "
                "recorrentes. Erro: %s",
                err,
            )
            raise
        except requests.exceptions.RequestException as err:
            logger.error("Erro geral de requisição ao acessar %s. %s", url, err)
            raise

    @classmethod
    def get_last_modified(cls, url: str) -> Optional[datetime]:
        """
        Obtém a data de última modificação de uma página web utilizando
        htmldate.

        Parâmetros:
            - url (str): A URL da página web.

        Retorna:
            - Optional[datetime]: Objeto datetime representando a data da última
                modificação, ou None se não for possível determinar.

        Exceções:
            - RequestException: Se ocorrer um erro na requisição.
            - Timeout: Se a requisição exceder o tempo limite.
            - ValueError: Se a data obtida for inválida.

        Exemplos de uso:
        ```python
        last_mod = RequestHandler.get_last_modified("https://example.com")
        print(last_mod)
        ```
        """
        try:
            RequestHandler.check_internet_access()
            date_str = htmldate.find_date(url, outputformat="%Y-%m-%d")
            last_modified = None  # Define como None inicialmente

            if date_str:
                last_modified = datetime.strptime(date_str, "%Y-%m-%d")

            logger.debug("Page last modified: %s ...", last_modified)
            return last_modified
        except (RequestsConnectionError, Timeout) as conn_err:
            logger.warning(
                "Erro de conexão ou timeout ao acessar %s: Erro %s",
                url,
                conn_err,
            )
            return None
        except RequestException as req_err:
            logger.error(
                "Erro de requisição ao tentar acessar %s: %s", url, req_err
            )
            return None
        except ValueError as val_err:
            logger.error("Erro ao processar a data obtida: %s", val_err)
            raise

    @classmethod
    def download_file(
        cls, url: str, filename_path: str, headers: Optional[Dict] = None
    ) -> str:
        """
        Faz o download de um arquivo a partir de uma URL e salva no caminho
        especificado.

        Parâmetros:
            - url (str): A URL do arquivo a ser baixado.
            - filename_path (str): Caminho completo onde o arquivo será salvo.
            - headers (Optional[Dict]): Cabeçalhos HTTP a serem enviados com a
              requisição. Caso não seja fornecido, utiliza um dicionário vazio.

        Retorna:
            - str: O caminho completo do arquivo baixado.

        Exceções:
            - RequestsConnectionError: Se o download falhar após várias
                tentativas devido a IncompleteRead.
            - Exception: Para outros erros ocorridos durante o download.

        Exemplos de uso:
        ```python
        local_file = RequestHandler.download_file(
            "https://example.com/file.pdf", "/path/to/file.pdf")
        print(local_file)
        ```
        """
        if headers is None:
            headers = {}  # Inicializa o dicionário se não for fornecido
        # Garante que os diretórios intermediários existem
        os.makedirs(os.path.dirname(filename_path), exist_ok=True)

        start_time = time.time()
        logger.debug(
            "Realizando o download do arquivo para %s ...", filename_path
        )
        response = None
        try:
            retry_count = 3  # Número de tentativas para IncompleteRead
            while retry_count > 0:
                try:
                    response = cls.request_with_retry(
                        url, stream=True, headers=headers
                    )
                    # Sanitiza o nome do arquivo para evitar problemas
                    # com caracteres inválidos
                    filename_path = FileOperator.sanitize_filename(
                        filename_path
                    )
                    with open(filename_path, "wb") as file_wb:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:  # Filtra chunks keep-alive vazios
                                file_wb.write(chunk)

                    return (
                        filename_path  # Download bem-sucedido, saindo do loop
                    )
                except (ChunkedEncodingError, IncompleteRead) as err:
                    logger.warning(
                        "IncompleteRead error: %s. Retentando... %d/3",
                        err,
                        (3 - retry_count + 1),
                    )
                    retry_count -= 1
                    time.sleep(2)  # Pequeno intervalo entre as tentativas
            # Se o retry_count chegar a 0, levanta uma exceção
            raise RequestsConnectionError(
                "Download falhou após várias tentativas devido a IncompleteRead."
            )
        except Exception as err:
            logger.error("Erro: %s", err)
            raise
        finally:
            end_time = time.time()
            processing_time = end_time - start_time
            logger.debug("Tempo decorrido: %.2f segundos", processing_time)
            if response:
                response.close()

        # Retorno no caso de falha, fora do try-finally
        return filename_path  # Ou, dependendo do caso, `return ""`

    @classmethod
    def get_soap_by_url(cls, url: str) -> BeautifulSoup:
        """
        Realiza uma requisição HTTP para a URL fornecida e retorna um objeto
        BeautifulSoup para análise do HTML.

        Parâmetros:
            - url (str): A URL da página web a ser acessada.

        Retorna:
            - BeautifulSoup: Objeto BeautifulSoup representando o conteúdo HTML
              da página.

        Exemplos de uso:
        ```python
        soup = RequestHandler.get_soap_by_url("https://example.com")
        print(soup.title.text)
        ```
        """
        # Realiza a requisição HTTP para a URL e obtém a resposta
        response = cls.request_with_retry(url)

        # Verifica se a resposta contém conteúdo HTML válido
        # Em caso de erro, `fetch_data_with_retry` já lidará com as exceções

        # Retorna o conteúdo da página web como um objeto BeautifulSoup
        return BeautifulSoup(response.content, "html.parser")

    @classmethod
    def get_soap_from_file(cls, file_path: str) -> BeautifulSoup:
        """
        Lê um arquivo HTML e retorna um objeto BeautifulSoup para análise.

        Parâmetros:
            - file_path (str): Caminho completo do arquivo HTML.

        Retorna:
            - BeautifulSoup: Objeto BeautifulSoup representando o conteúdo do
              arquivo HTML.

        Exceções:
            - FileNotFoundError: Se o arquivo não for encontrado.
            - ValueError: Se o conteúdo do arquivo estiver vazio ou inválido.

        Exemplos de uso:
        ```python
        soup = RequestHandler.get_soap_from_file("/path/to/file.html")
        print(soup.prettify())
        ```
        """
        try:
            # Abre o arquivo no modo de leitura
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            # Verifica se o conteúdo do arquivo não está vazio
            if not content.strip():
                raise ValueError(
                    f"O arquivo {file_path} está vazio ou inválido."
                )

            # Retorna o conteúdo como um objeto BeautifulSoup
            return BeautifulSoup(content, "html.parser")
        except FileNotFoundError as err:
            raise FileNotFoundError(
                f"Arquivo não encontrado: {file_path}. Erro: {err}"
            ) from err
        except Exception as err:
            logger.error("Erro ao processar o arquivo %s: %s", file_path, err)
            raise

    @classmethod
    def check_internet_access(
        cls, url="https://www.google.com", timeout=TIMEOUT_CONNECT
    ) -> bool:
        """
        Verifica a disponibilidade de acesso à internet tentando acessar uma
        URL padrão.

        Parâmetros:
            - url (str): A URL a ser acessada para verificar a conexão. Padrão:
                "https://www.google.com".
            - timeout (int): Tempo máximo de espera (em segundos) para a
                resposta. Padrão: TIMEOUT_CONNECT.

        Retorna:
            - bool: True se a conexão for bem-sucedida; caso contrário, lança
                uma exceção.

        Exceções:
            - RequestsConnectionError: Se ocorrer um erro de conexão ou se o
                tempo limite for excedido.
            - Timeout: Se a requisição exceder o tempo limite.

        Exemplos de uso:
        ```python
        if RequestHandler.check_internet_access():
            print("Internet disponível!")
        ```
        """
        try:
            logger.debug("Verificando conexão de internet ...")
            # Faz uma requisição GET ao URL especificado com um tempo limite
            response = requests.get(url, timeout=timeout)
            # Verifica se o código de status HTTP é 200 (OK)
            if response.status_code == 200:
                logger.debug("Conexão OK!")
                return True

            msm = (
                f"Erro ao acessar a página {url}! "
                f"Status Code: {response.status_code}, "
                f"response.text: {response.text}"
            )
            logger.warning(msm)
            raise RequestsConnectionError(msm)
        except RequestsConnectionError as err:
            # Se ocorrer um erro de conexão, a máquina provavelmente está
            # sem acesso à internet
            logger.warning("Internet indisponível! Erro: %s", err)
            raise RequestsConnectionError(err) from err
        except requests.Timeout as err:
            # Se a requisição exceder o tempo limite, também pode indicar
            # problemas de conexão
            logger.warning("Internet indisponível! Erro: %s", err)
            raise RequestsConnectionError(err) from err

        # Se o fluxo chegar aqui, algo inesperado ocorreu.
        raise RuntimeError("Código inatingível em check_internet_access")

    @classmethod
    def show_cache_info(cls, show_urls: bool = False):
        """
        Exibe informações sobre o cache de requisições HTTP.

        Parâmetros:
            - show_urls (bool): Se True, exibe as URLs armazenadas no cache.

        Retorna:
            - None

        Exemplos de uso:
        ```python
        RequestHandler.show_cache_info(show_urls=True)
        ```
        """

        session = cls.get_session()

        # Verifica se o cache está habilitado
        if not session.cache:
            logger.warning("O cache não está habilitado para esta sessão.")
            return

        # Obter o backend do cache
        cache_backend = session.cache
        cache_keys = list(cache_backend.responses.keys())
        cache_size = len(cache_keys)  # Conta as URLs no cache

        # Calcular o tamanho total do cache
        total_cache_size = sum(
            len(response.content)
            for response in cache_backend.responses.values()
        )

        logger.info(
            "REQUEST CACHE: Número de requisições armazenadas: %s; "
            "Tamanho total do cache: %s MB (aproximado)",
            cache_size,
            round(total_cache_size / (1024**2), 4),
        )

        if show_urls:
            logger.info("\nREQUEST CACHE: URLs armazenadas no cache:")
            for url_hash in cache_keys:
                response = cache_backend.responses[url_hash]
                url = response.request.url
                expiration = response.expires
                logger.info(
                    "REQUEST CACHE: - URL: %s; Data de Expiração: %s; "
                    "Tamanho da Resposta: %s MB",
                    url,
                    expiration,
                    round(len(response.content) / (1024**2), 4),
                )
