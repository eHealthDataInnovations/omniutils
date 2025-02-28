from collections.abc import Mapping  # pylint: disable=no-name-in-module
from itertools import product
from typing import Any, Dict, List, Optional


class DictionaryUtils:
    """
    Uma classe utilitária para manipulação e transformação de dicionários.

    A classe oferece métodos para expandir listas aninhadas, facilitando a
    transformação de dicionários com estruturas complexas (como listas e
    subdicionários) em uma lista de dicionários "achatados", onde cada item de
    uma lista é combinado com os demais valores fixos.
    """

    @staticmethod
    def expand_lists_recursive(
        data: Dict, sep: Optional[str] = "__", parent_key: str = ""
    ) -> List[Dict]:
        """
        Expande listas presentes em todos os subníveis de um dicionário, gerando
        uma combinação de valores para cada item em cada lista. Listas vazias
        são tratadas como contendo o valor `None`.

        Este método percorre recursivamente todos os níveis do dicionário e cria
        uma lista de dicionários, onde cada dicionário representa uma combinação
         dos valores fixos do dicionário original com um dos itens das listas
        encontradas. Se um valor for um subdicionário, ele também será expandido
         recursivamente, e suas chaves serão concatenadas com a chave pai
        utilizando o separador especificado.

        Parâmetros:
            data (dict): Dicionário de entrada contendo listas e/ou
                subdicionários para serem expandidos.
            sep (str, opcional): Separador utilizado para concatenar as chaves
                dos subníveis. O padrão é "__".
            parent_key (str, opcional): Prefixo utilizado para as chaves
                compostas, aplicável em chamadas recursivas. O padrão é uma
                string vazia.

        Retorna:
            - List[dict]: Uma lista de dicionários, onde cada dicionário
                representa uma combinação dos valores fixos do dicionário
                original com um dos itens das listas encontradas.

        Exemplos de uso:
        ```python
        # Exemplo 1: Expansão de listas simples
        data = {
            "id": 1,
            "tags": ["python", "utils"],
            "meta": {"author": "user", "likes": [10, 20]}
        }
        result = DictionaryUtils.expand_lists_recursive(data)
        # Resultado:
        # [
        #{"id": 1, "tags": "python", "meta__author": "user", "meta__likes": 10},
        #{"id": 1, "tags": "python", "meta__author": "user", "meta__likes": 20},
        #{"id": 1, "tags": "utils",  "meta__author": "user", "meta__likes": 10},
        #{"id": 1, "tags": "utils",  "meta__author": "user", "meta__likes": 20}
        # ]

        # Exemplo 2: Lista vazia
        data = {"id": 1, "tags": []}
        result = DictionaryUtils.expand_lists_recursive(data)
        # Resultado:
        # [{"id": 1, "tags": None}]

        # Exemplo 3: Expansão com subníveis de dicionários
        data = {"id": 1, "meta": {"tags": ["python", "ai"]}}
        result = DictionaryUtils.expand_lists_recursive(data)
        # Resultado:
        # [
        #     {"id": 1, "meta__tags": "python"},
        #     {"id": 1, "meta__tags": "ai"}
        # ]
        ```
        """
        if not isinstance(data, Mapping):
            raise ValueError("O dado de entrada deve ser um dicionário.")

        def flatten_key(key: str, parent: str) -> str:
            return f"{parent}{sep}{key}" if parent else key

        items = []
        for key, value in data.items():
            full_key = flatten_key(key, parent_key)
            if isinstance(value, list):
                if not value:
                    items.append([{full_key: None}])
                else:
                    subitems = []
                    for item in value:
                        if isinstance(item, dict):
                            subitems.extend(
                                DictionaryUtils.expand_lists_recursive(
                                    item, sep, full_key
                                )
                            )
                        else:
                            subitems.append({full_key: item})
                    items.append(subitems)
            elif isinstance(value, dict):
                items.append(
                    DictionaryUtils.expand_lists_recursive(value, sep, full_key)
                )
            else:
                items.append([{full_key: value}])

        result = []
        for combination in product(*items):
            merged: Dict[str, Any] = {}
            for d in combination:  # pylint: disable=invalid-name
                merged.update(d)
            result.append(merged)
        return result
