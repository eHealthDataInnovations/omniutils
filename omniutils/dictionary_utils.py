from collections.abc import Mapping
from typing import Dict, List, Optional


class DictionaryUtils:
    """
    Uma classe utilitária para manipulação e transformação de dicionários.

    A classe oferece métodos para expandir listas aninhadas, facilitando a transformação
    de dicionários com estruturas complexas (como listas e subdicionários) em uma lista de
    dicionários "achatados", onde cada item de uma lista é combinado com os demais valores fixos.
    """

    @staticmethod
    def expand_lists_recursive(
        data: Dict, sep: Optional[str] = "__", parent_key: Optional[str] = ""
    ) -> List[Dict]:
        """
        Expande listas presentes em todos os subníveis de um dicionário, repetindo os demais itens
        para cada item da lista. Listas vazias são tratadas com o valor `None`.

        O método percorre recursivamente todos os níveis do dicionário, identificando listas e
        subdicionários. Quando uma lista é encontrada, cada item da lista é expandido em novas
        entradas, combinando os valores fixos do dicionário com cada elemento da lista. Se um valor
        for um subdicionário, ele também será expandido recursivamente, e suas chaves serão concatenadas
        com a chave pai utilizando o separador especificado.

        Parâmetros:
            data (dict): Dicionário de entrada contendo listas e/ou subdicionários para serem expandidos.
            sep (Optional[str]): Separador utilizado para concatenar as chaves dos subníveis.
                                 O valor padrão é "__".
            parent_key (Optional[str]): Prefixo utilizado para as chaves compostas, aplicável em chamadas recursivas.
                                        O valor padrão é uma string vazia.

        Retorna:
            List[dict]: Uma lista de dicionários com as listas expandidas. Cada dicionário na lista
                        representa uma combinação dos valores fixos do dicionário original com um dos itens
                        das listas encontradas.

        Exceções:
            ValueError: Se o argumento `data` não for um dicionário.

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
        #     {"id": 1, "tags": "python", "meta__author": "user", "meta__likes": 10},
        #     {"id": 1, "tags": "python", "meta__author": "user", "meta__likes": 20},
        #     {"id": 1, "tags": "utils",  "meta__author": "user", "meta__likes": 10},
        #     {"id": 1, "tags": "utils",  "meta__author": "user", "meta__likes": 20}
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

        def flatten_key(key, parent):
            return f"{parent}{sep}{key}" if parent else key

        # Separar as chaves cujos valores são listas dos demais valores fixos
        list_keys = {
            key: value for key, value in data.items() if isinstance(value, list)
        }
        fixed_keys = {
            key: value
            for key, value in data.items()
            if not isinstance(value, list)
        }

        # Expande recursivamente subníveis de dicionários dentro dos valores
        # fixos
        expanded_fixed = {}
        for key, value in fixed_keys.items():
            if isinstance(value, dict):
                sub_expanded = DictionaryUtils.expand_lists_recursive(
                    value, parent_key=flatten_key(key, parent_key)
                )
                for sub_entry in sub_expanded:
                    expanded_fixed.update(sub_entry)
            else:
                expanded_fixed[flatten_key(key, parent_key)] = value

        # Caso não haja listas, retorna os valores fixos
        if not list_keys:
            return [expanded_fixed]

        # Expandir listas em todos os níveis
        expanded_data = []
        for key, values in list_keys.items():
            if not values:  # Tratamento de lista vazia
                entry = expanded_fixed.copy()
                entry[flatten_key(key, parent_key)] = None
                expanded_data.append(entry)
            else:
                for value in values:
                    entry = expanded_fixed.copy()
                    if isinstance(value, dict):
                        # Se o item da lista for um dicionário,
                        # expanda-o recursivamente
                        sub_expanded = DictionaryUtils.expand_lists_recursive(
                            value, parent_key=flatten_key(key, parent_key)
                        )
                        for sub_entry in sub_expanded:
                            entry.update(sub_entry)
                            expanded_data.append(entry)
                    else:
                        # Caso seja um valor simples, apenas atribua-o
                        entry[flatten_key(key, parent_key)] = value
                        expanded_data.append(entry)

        return expanded_data
