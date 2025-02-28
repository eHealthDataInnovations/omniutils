import json
from datetime import datetime

import requests  # pylint: disable=import-error

from omniutils.github import GitHubUtils


class DummyResponse:
    """
    Classe auxiliar para simular uma resposta da API do GitHub.
    """

    def __init__(self, status_code, json_data, url):
        self.status_code = status_code
        self._json_data = json_data
        self.url = url
        self.reason = "OK"
        self.text = json.dumps(json_data)

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if not 200 <= self.status_code < 300:
            raise requests.HTTPError(f"{self.status_code} Error", response=self)


def dummy_get(
    url, headers=None, params=None, **kwargs
):  # pylint: disable=unused-argument
    """
    Função dummy para simular uma requisição GET à API do GitHub.

    Ignora os parâmetros extras e retorna uma resposta simulada contendo um
    commit com a data '2024-01-15T12:34:56Z'.

    Args:
        url (str): A URL da requisição.
        headers (dict, opcional): Cabeçalhos HTTP.
        params (dict, opcional): Parâmetros da query string.
        **kwargs: Outros argumentos.

    Returns:
        DummyResponse: Uma instância simulada com status 200 e dados do commit.
    """
    commit_data = {"commit": {"committer": {"date": "2024-01-15T12:34:56Z"}}}
    # A API do GitHub retorna uma lista de commits; aqui simulamos uma lista
    # com um único commit.
    return DummyResponse(200, [commit_data], url)


def test_get_last_modified_date(monkeypatch):
    """
    Testa o método GitHubUtils.get_last_modified_date utilizando um patch para
    simular a resposta da API do GitHub. Como o método utiliza
    RequestHandler.request_with_retry, aplicamos o patch diretamente nessa
    função para evitar chamadas reais à API.

    Espera que a data de modificação retornada seja um objeto datetime 'naive'
    correspondente a '2024-01-15 12:34:56'.
    """
    # Aplica o patch na função request_with_retry da classe RequestHandler,
    # fazendo-a chamar dummy_get.
    monkeypatch.setattr(
        "omniutils.request_handler.RequestHandler.request_with_retry",
        lambda url, headers, params, **kwargs: dummy_get(  # noqa: E501 # pylint: disable=unnecessary-lambda, disable=line-too-long
            url, headers, params, **kwargs
        ),
    )

    data_obj = GitHubUtils.get_last_modified_date(
        file_path="data/trusted/file.txt",
        token="dummy_token",
        owner="owner",
        repo="repo",
    )
    # Como o método remove o tzinfo, espera-se um objeto datetime 'naive'.
    expected = datetime(
        2024, 1, 15, 9, 34, 56
    )  # 12:34:56 UTC = 09:34:56 no fuso horário de Brasília
    assert data_obj == expected
