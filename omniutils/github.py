import logging
from datetime import datetime, timezone
from typing import Optional

from .request_handler import RequestHandler

logger = logging.getLogger(__name__)


class GitHubUtils:
    @staticmethod
    def get_last_modified_date(
        file_path: str,
        owner: str,
        repo: str,
        token: Optional[str] = None,
    ):
        """
        Obtém a data da última modificação de um arquivo em um repositório GitHub.

        Este método consulta a API do GitHub para recuperar o commit mais recente associado
        a um arquivo específico, utilizando o caminho completo do arquivo dentro do repositório.
        A data de modificação é extraída do commit (geralmente quando o commit foi empurrado para o repositório remoto),
        convertida de uma string no formato UTC para um objeto datetime em UTC, ajustada para o horário local
        e, por fim, o fuso horário é removido para facilitar comparações com datas "naive".

        Parâmetros:
            file_path (str): O caminho do arquivo dentro do repositório (por exemplo, "data/trusted/arquivo.txt").
            token (str): O token de autenticação do GitHub para acessar a API.
            owner (str): O nome do proprietário do repositório.
            repo (str): O nome do repositório.

        Retorna:
            - datetime: Um objeto datetime representando a data da última modificação do arquivo,
              convertido para o horário local (sem informação de fuso horário).
            - None: Caso a requisição não seja bem-sucedida ou nenhum commit seja encontrado.

        Exemplos de uso:
        ```python
        from github import get_last_modified_date

        token = "seu_token_github"
        last_mod_date = get_last_modified_date(
            file_path="data/trusted/arquivo.txt",
            token=token,
            owner="eHealthDataInnovations",
            repo="medication-data-framework"
        )
        if last_mod_date:
            print(f"Última modificação: {last_mod_date}")
        else:
            print("Não foi possível obter a data de modificação.")
        ```
        """

        # Endpoint da API para o commit mais recente
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        params = {
            "path": file_path,
            "per_page": 1,  # Limita a resposta a um commit, o mais recente
        }

        headers = {}
        if token:
            # Headers com o token de acesso
            headers = {"Authorization": f"Bearer {token}"}

        response = RequestHandler.request_with_retry(
            url, headers=headers, params=params
        )  # type: ignore[arg-type]

        if response.status_code == 200 and response.json():
            commit_data = response.json()[0]

            # Data em que o commit foi realmente aplicado ao repositório,
            # geralmente quando ele foi "empurrado" (push) para o repositório remoto.
            last_modified_date = commit_data["commit"]["committer"]["date"]

            # Converte a string de data UTC para um objeto datetime em UTC
            last_modified_datetime = datetime.strptime(
                last_modified_date, "%Y-%m-%dT%H:%M:%SZ"
            ).replace(tzinfo=timezone.utc)

            # Converte o objeto datetime para o horário local
            last_modified_local_datetime = last_modified_datetime.astimezone()

            # Remove o fuso horário para facilitar comparações com outras datas
            # "naive"
            last_modified_local_naive = last_modified_local_datetime.replace(
                tzinfo=None
            )

            logger.debug(f"Última modificação: {last_modified_local_naive}")
            return last_modified_local_naive
        else:
            logger.warning(
                f"Erro ao acessar a data de modificação, "
                f"status_code {response.status_code}, "
                f"content: {response.text}"
            )
            return None
