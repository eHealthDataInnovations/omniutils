import json


class JsonOperator:
    @staticmethod
    def load_json(caminho_arquivo: str) -> dict:
        """
        Lê um arquivo JSON contendo retorna seu conteúdo como um dicionário.

        Parâmetros
        ----------
        caminho_arquivo : str
            O caminho para o arquivo JSON que será lido.

        Retorna
        -------
        dict
            O conteúdo do arquivo JSON .

        Exceções
        --------
        Levanta FileNotFoundError se o arquivo não for encontrado.
        Levanta json.JSONDecodeError se o conteúdo do arquivo não for um JSON
        válido.

        Exemplo
        -------
        ```
        conteudo = load_json("arquivo.json")
        print(conteudo)
        ```

        """
        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
                return json.load(arquivo)
        except FileNotFoundError as error:
            raise FileNotFoundError(
                f"Arquivo não encontrado: {caminho_arquivo}"
            ) from error
        except json.JSONDecodeError as error:
            raise ValueError(f"Erro ao decodificar JSON: {error}") from error

    @staticmethod
    def save_json(caminho_arquivo: str, conteudo: dict):
        """
        Escreve um dicionário em um arquivo JSON.

        Parâmetros
        ----------
        caminho_arquivo : str
            O caminho para o arquivo JSON que será escrito.
        conteudo : dict
            O dicionário que será escrito no arquivo.

        Exceções
        --------
        Levanta json.JSONDecodeError se o conteúdo do arquivo não for um JSON
        válido.

        Exemplo
        -------
        ```
        conteudo = {"nome": "João", "idade": 30}
        write_json("arquivo.json", conteudo)
        ```

        """
        try:
            with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
                json.dump(conteudo, arquivo, indent=4)
        except json.JSONDecodeError as err:
            raise ValueError(f"Erro ao decodificar JSON: {err}") from err
