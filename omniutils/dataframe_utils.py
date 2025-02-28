import json
import logging
import re
import warnings
from typing import Any, Hashable, List, Literal, Optional, Tuple

import pandas as pd

from .exceptions import DataFrameFormatError
from .text_utils import TextUtils

logger = logging.getLogger(__name__)


class DataFrameUtils:
    """
    Conjunto de métodos utilitários estáticos para processamento e manipulação
    de DataFrames do pandas.

    Essa classe oferece funções para:
      - Filtrar linhas por palavras-chave ou com base em um dicionário de
        condições.
      - Encontrar a próxima linha composta apenas por valores NaN.
      - Converter colunas para string com preenchimento customizado.
      - Normalizar dados JSON para DataFrames planos.
      - Converter valores para tipos numéricos (inteiro ou float) de forma
        segura.
      - Identificar células contendo datas ou valores numéricos em um DataFrame.
      - Tratar colunas com tipos mistos ou que contenham dicionários.
      - Realizar outras operações comuns de transformação e limpeza de dados.

    Todos os métodos são implementados como estáticos, permitindo seu uso sem
    necessidade de instanciar a classe.
    """

    @staticmethod
    def filter_rows_by_keywords(
        df: pd.DataFrame, keywords: list[str], column_name: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Filtra as linhas de um DataFrame com base em uma lista de palavras-chave
        presentes em uma coluna específica ou em todas as colunas.

        Este método verifica se uma ou mais palavras-chave fornecidas estão
        contidas nos valores de uma coluna específica (se especificada) ou
        em todas as colunas do DataFrame, retornando um novo DataFrame com as
        linhas que atendem ao critério.

        Parâmetros:
            df (pd.DataFrame): O DataFrame a ser filtrado.
            keywords (list[str]): Lista de palavras-chave a serem buscadas.
            column_name (str, opcional): O nome da coluna onde a busca pelas
                                         palavras-chave será realizada. Se None,
                                          busca em todas as colunas.

        Retorna:
            pd.DataFrame: Um novo DataFrame contendo apenas as linhas onde ao
                          menos uma das palavras-chave foi encontrada. Caso
                          nenhuma linha corresponda ao critério, o DataFrame
                          retornado estará vazio.

        Exemplo:
        ```python
        import pandas as pd

        # Exemplo de DataFrame
        data = {
            "Nome": ["Alice", "Bob", "Carlos", "Diana"],
            "Descrição": ["Gerente de projetos", "Engenheiro de dados",
                          "Analista de sistemas", "Desenvolvedora full-stack"]
        }
        df = pd.DataFrame(data)

        # Filtrar linhas onde a coluna 'Descrição' contém as palavras 'dados'
        # ou 'projetos'
        resultado = filter_rows_by_keywords(df, ["dados", "projetos"],
                                            "Descrição")
        print(resultado)

        # Filtrar linhas onde qualquer coluna contém as palavras 'dados' ou
        # 'projetos'
        resultado = filter_rows_by_keywords(df, ["dados", "projetos"])
        print(resultado)
        ```

        Detalhes:
            - A busca pelas palavras-chave é case-insensitive (não diferencia
              maiúsculas de minúsculas).
            - Valores nulos são tratados como `False` na verificação.
            - Se `column_name` for especificado, a busca é restrita a essa
              coluna.
            - Caso contrário, a busca é realizada em todas as colunas do
              DataFrame.

        Notas:
            - Se nenhuma linha contiver as palavras-chave, o DataFrame retornado
               será vazio.
            - Este método utiliza `str.contains` para realizar a busca pelas
              palavras-chave, construindo uma expressão regular que combina
              todas as palavras da lista.

        Exceções:
            - ValueError: Levantada se o nome da coluna especificado não for
                          encontrado no DataFrame.
        """
        # Cria um padrão regex a partir da lista de palavras-chave
        keywords_pattern = "|".join(map(re.escape, keywords))

        if column_name:
            # Verifica se a coluna especificada existe no DataFrame
            if column_name not in df.columns:
                raise DataFrameFormatError(
                    f"Coluna '{column_name}' não encontrada no DataFrame."
                )
            # Filtra linhas com base na coluna especificada
            mask = (
                df[column_name]
                .astype(str)
                .str.contains(
                    rf"\b(?:{keywords_pattern})\b", case=False, na=False
                )
            )
        else:
            # Filtra linhas em todas as colunas
            mask = df.apply(
                lambda row: any(
                    re.search(
                        rf"\b(?:{keywords_pattern})\b",
                        str(value),
                        re.IGNORECASE,
                    )
                    for value in row
                ),
                axis=1,
            )

        return df[mask]

    @staticmethod
    def find_next_all_nan_row(df: pd.DataFrame, start_idx: int = 0) -> int:
        """
        Encontra a próxima linha composta apenas por valores NaN em um
        DataFrame, a partir de um índice inicial.

        Este método verifica todas as linhas do DataFrame para identificar a
        próxima linha onde todos os valores são NaN (não numéricos) após o
        índice inicial fornecido.

        Parâmetros:
        -----------
        df : pd.DataFrame
            O DataFrame a ser analisado.

        start_idx : int, opcional
            O índice inicial a partir do qual a busca será realizada. O padrão
            é 0.

        Retorna:
        --------
        int:
            O índice da próxima linha composta apenas por valores NaN. Se
            nenhuma linha for encontrada, retorna -1.

        Exemplo:
        --------
        ```python
        import pandas as pd
        import numpy as np

        # Exemplo de DataFrame
        data = {
            "Coluna1": [1, 2, np.nan, np.nan, 5],
            "Coluna2": [np.nan, 2, np.nan, np.nan, np.nan],
            "Coluna3": [3, np.nan, np.nan, np.nan, np.nan],
        }
        df = pd.DataFrame(data)

        # Encontrar a próxima linha com todos os valores NaN após o índice 1
        idx = DataFrameUtils.find_next_all_nan_row(df, start_idx=1)
        print(idx)

        # Saída:
        # 2 # Índice da próxima linha com todos os valores NaN
        ```

        Notas:
        ------
        - Este método utiliza `df.isna().all(axis=1)` para identificar
          linhas onde todos os valores são NaN.
        - A busca começa após o índice fornecido (`start_idx`) e retorna a
          primeira linha correspondente encontrada.
        - Caso nenhuma linha atenda ao critério, retorna `-1`.

        Exceções:
        ---------
        - O método não levanta exceções para índices fora do intervalo ou
          DataFrames sem linhas válidas. Retorna simplesmente `-1` nesses casos.
        """
        nan_rows = df.isna().all(axis=1)
        nan_indices = nan_rows.index[nan_rows].tolist()
        for idx in nan_indices:
            if idx > start_idx:
                return idx
        return -1

    @staticmethod
    def filter_by_dict(df: pd.DataFrame, data_filter: dict) -> pd.DataFrame:
        """
        Filtra um DataFrame com base em um dicionário de condições
        especificadas.

        Este método aplica filtros a um DataFrame do Pandas com base em pares
        chave-valor fornecidos no dicionário `data_filter`. As chaves do
        dicionário representam os nomes das colunas, e os valores representam os
         critérios de filtro. Se o valor for `None`, as linhas com valores nulos
         (NaN) serão descartadas.

        Parâmetros
        ----------
        df : pd.DataFrame
            O DataFrame a ser filtrado.
        data_filter : dict
            Um dicionário onde:
            - As chaves representam os nomes das colunas no DataFrame.
            - Os valores especificam os critérios de filtro:
              - Se o valor for `None`, a função filtra os valores não nulos
              (NaN) na coluna correspondente.
              - Para qualquer outro valor, filtra as linhas que têm o valor
              exato na coluna.

        Retorna
        -------
        pd.DataFrame
            Um novo DataFrame contendo apenas as linhas que atendem aos
            critérios especificados em `data_filter`.

        Exemplo de Uso
        --------------
        ```python
            import pandas as pd
            data = {
                'produtofarmaceutico__pk': ['1', '2', '2', '3'],
                'acessorio__pk': [None, '10', None, '20']
            }
            df = pd.DataFrame(data)
            data_filter = {'produtofarmaceutico__pk': '2',
            ssorio__pk': None}
            filtered_df = DataFrameUtils.filter_by_dict(df, data_filter)
            print(filtered_df)
              produtofarmaceutico__pk acessorio__pk
            2                           2          None
        ```
        Notas
        -----
        - Para condições mais complexas (e.g., maior/menor que, múltiplas
          condições), este método precisaria de adaptação.
        - Certifique-se de que as chaves em `data_filter` existam como colunas
          no DataFrame para evitar erros.

        """
        filtered_df = df.copy()
        for key, value in data_filter.items():
            if value is None:
                filtered_df = filtered_df[filtered_df[key].notna()]
            else:
                filtered_df = filtered_df[filtered_df[key] == value]
        return filtered_df

    @staticmethod
    def to_string_isna(df: pd.DataFrame, inplace: bool = False):
        """
        Converte as colunas de um DataFrame contendo apenas valores ausentes
        (NaN) para o tipo string.

        Este método verifica cada coluna do DataFrame e, caso todos os valores
        em uma coluna sejam NaN, converte a coluna para o tipo `str`.
        O método pode operar de forma in-place ou retornar uma cópia modificada
        do DataFrame.

        Parameters:
        ----------
        df : pd.DataFrame
            O DataFrame a ser processado.
        inplace : bool, opcional
            Se `True`, realiza as alterações diretamente no DataFrame fornecido
            (padrão é `False`).

        Returns:
        -------
        pd.DataFrame
            Se `inplace` for `False`, retorna uma nova cópia do DataFrame com
            as colunas de valores
            NaN convertidas para string. Se `inplace` for `True`, retorna o
            próprio DataFrame modificado.

        Examples:
        --------
        ```python
            import pandas as pd
            import numpy as np
            df = pd.DataFrame({"col1": [np.nan, np.nan], "col2": [1, 2]})
            DataFrameUtils.to_string_isna(df)
               col1 col2
            0   NaN    1
            1   NaN    2
        ```
        """
        # Define o DataFrame a ser utilizado
        df_copy = df
        if not inplace:
            df_copy = df.copy()

        # Converte colunas com apenas valores NaN para o tipo string
        for column in df_copy.columns:
            if df_copy[column].isna().all():
                df_copy[column] = df_copy[column].astype(str)

        return df_copy if not inplace else None

    @staticmethod
    def check_null(value):
        """
        Verifica e retorna um valor se ele não for nulo ou uma string que
        represente ausência de valor.

        Este método recebe um valor e verifica se ele é considerado não nulo
        (`pd.notna`) e se não
        é uma string "<NA>". Caso ambas as condições sejam verdadeiras, o
        método retorna o valor;
        caso contrário, retorna `None`.

        Parameters:
        ----------
        value : any
            O valor a ser verificado.

        Returns:
        -------
        any or None
            Retorna o valor original se não for nulo e diferente de "<NA>",
            ou `None` caso contrário.

        Examples:
        --------
        >>> DataFrameUtils._check_null("data")
        'data'

        >>> DataFrameUtils._check_null("<NA>")
        None

        >>> DataFrameUtils._check_null(None)
        None
        """
        if pd.notna(value) and value != "<NA>":
            return value
        return None

    @staticmethod
    def to_number_all(df: pd.DataFrame, inplace: bool = False) -> pd.DataFrame:
        """
        Converte os valores de todas as colunas de um DataFrame para tipos
        numéricos ou apropriados.

        Este método tenta converter os valores de cada coluna do DataFrame para
        o tipo numérico  (inteiros ou floats) onde possível, utilizando a
        função `TextUtils.to_number_str`. Valores que não podem ser convertidos
        permanecem como estão. Se `inplace=True`,  a modificação é feita
        diretamente no DataFrame original.

        Parâmetros:
        -----------
        df : pd.DataFrame
            O DataFrame que será processado para conversão dos valores.

        inplace : bool, opcional
            Indica se as alterações devem ser feitas diretamente no DataFrame
            original. Se `True`, o DataFrame original é modificado e o método
            não retorna nada. O padrão é `False`.

        Retorna:
        --------
        pd.DataFrame
            O DataFrame com os valores das colunas convertidos para tipos
            apropriados. Retorna apenas se `inplace=False`.

        Exemplo:
        --------
        ```python
        import pandas as pd
        from text_utils import TextUtils

        # Exemplo de DataFrame
        data = {
            "coluna1": ["123", "456", "789"],
            "coluna2": ["1.23", "4.56", "7.89"],
            "coluna3": ["texto", None, "12,34"]
        }
        df = pd.DataFrame(data)

        # Converter valores no DataFrame
        df_converted = TextUtils.to_number_all(df)

        print(df_converted)

        # Saída esperada:
        #    coluna1  coluna2 coluna3
        # 0    123.0    1.23  texto
        # 1    456.0    4.56   None
        # 2    789.0    7.89  12.34
        ```

        Notas:
        ------
        - Este método utiliza a função `TextUtils.to_number_str` para converter
          os valores.
        - Colunas que não contêm valores numéricos permanecem inalteradas.
        - Se `inplace=True`, o DataFrame original será modificado diretamente,
          e o método não  retornará nada.
        - Se ocorrer um erro ao processar uma coluna, será lançada uma exceção
          detalhada.

        Exceções:
        ---------
        - `ValueError`: Lançado se houver um erro ao processar alguma coluna.

        Dependências:
        -------------
        - `TextUtils.to_number_str`: Função que converte strings em números.
        - `pandas`: Biblioteca usada para manipulação de DataFrames.

        """
        df_copy = df
        if not inplace:
            df_copy = df.copy()

        for column in df_copy.columns:
            try:
                df_copy[column] = df_copy[column].apply(TextUtils.to_number_str)
            except Exception as err:
                raise DataFrameFormatError(
                    f"Erro ao processar a coluna '{column}': {err}"
                ) from err
        return df_copy

    @staticmethod
    def to_str(
        arr_dtype: pd.Series,
        max_length: Optional[int] = None,
        errors: Literal["raise", "coerce"] = "raise",
    ) -> pd.Series:
        """
        Converte uma coluna do Pandas para string, preenchendo com zeros
        à esquerda até atingir o comprimento especificado, preservando valores
        nulos (`pd.NA`).

        O método suporta colunas do tipo inteiro ou objeto, mas lançará exceções
        para tipos não suportados, como float e boolean, a menos que
        `errors="coerce"` seja especificado.

        Parâmetros
        ----------
        arr_dtype : pd.Series
            A coluna a ser convertida para string.

        max_length : int, opcional
            Comprimento máximo da string resultante. Valores numéricos serão
            preenchidos com zeros à esquerda até atingir esse comprimento.
            Valores nulos não serão alterados.

        errors : {"raise", "coerce"}, padrão "raise"
            - "raise": Levanta exceções para tipos não suportados
              (float, boolean).
            - "coerce": Ignora erros e tenta converter valores para string,
              definindo valores inválidos como nulos (`pd.NA`).

        Retorna
        -------
        pd.Series
            Uma série convertida para string, com preenchimento de zeros à
            esquerda se `max_length` for fornecido. Valores nulos permanecem
            inalterados.

        Exceções
        --------
        TypeError
            Levantada se a coluna contiver tipos não suportados (float, boolean
            ou outros) e `errors="raise"`.

        Exemplos
        --------
        ```python
            import pandas as pd
            data = {'col1': [123, None, 456, 789]}
            df = pd.DataFrame(data)
            df['col1'] = DataFrameUtils.to_str(df['col1'], max_length=5)
            print(df)
            col1
            0  00123
            1   <NA>
            2  00456
            3  00789

            print(df['col1'].dtype)
            object
        ```
        """
        # Verifica se o tipo é float e gera exceção se necessário
        if errors != "coerce" and pd.api.types.is_float_dtype(arr_dtype):
            raise TypeError(
                "Não é possível converter valores do tipo float para string. "
                "Apenas tipos inteiros são permitidos."
            )

        # Verifica se o tipo é boolean e gera exceção se necessário
        if errors != "coerce" and pd.api.types.is_bool_dtype(arr_dtype):
            raise TypeError(
                "Não é possível converter valores do tipo booleano para string."
                " Apenas tipos inteiros são permitidos."
            )

        # Verifica tipos não suportados e gera exceção
        if (
            errors != "coerce"
            and not pd.api.types.is_integer_dtype(arr_dtype)
            and not pd.api.types.is_object_dtype(arr_dtype)
        ):
            raise TypeError(
                f"Tipo de dado {arr_dtype.dtype} não suportado para conversão. "
                f"Apenas tipos inteiros são permitidos."
            )

        # Caso seja necessário aplicar a conversão
        # Se max_length é fornecido, preenche com zeros à esquerda
        if max_length is not None:
            # Converte objetos não numéricos para inteiros, tratando nulos
            arr_dtype = DataFrameUtils.to_int(arr_dtype)

            # Converte valores para string, preservando nulos
            arr_dtype_str = arr_dtype.astype(str).replace("<NA>", pd.NA)

            # Preenche com zeros à esquerda, mas preserva valores nulos
            return arr_dtype_str.apply(
                lambda x: x.zfill(max_length) if pd.notna(x) else x
            )

        # Caso max_length não seja fornecido, converte para string
        # diretamente
        return arr_dtype.fillna(pd.NA).astype(str)

    @staticmethod
    def get_max_length(df: pd.DataFrame, column_name: str) -> int:
        """
        Calcula o comprimento máximo de caracteres na coluna especificada do
        DataFrame.

        Parâmetros:
        -----------
        df : pd.DataFrame
            O DataFrame contendo os dados a serem analisados.
        column_name : str
            O nome da coluna para calcular o comprimento máximo.

        Retorna:
        --------
        int
            O comprimento máximo de caracteres encontrado na coluna
            especificada.

        Exemplo de Uso:
        ---------------
        max_length = DataIngestion.get_max_length(df,
        'feature_forma_farmaceutica')
        """
        # Calcula o comprimento máximo de caracteres na coluna especificada
        max_length = df[column_name].str.len().max()
        return max_length

    @staticmethod
    def json_normalize(list_contents: list, sep: str) -> pd.DataFrame:
        """
        Normaliza uma lista de dicionários JSON, expandindo estruturas
        aninhadas em colunas planas.

        Este método usa `pd.json_normalize` para converter uma lista de
        dicionários JSON em um DataFrame do pandas. Ele expande colunas que
        contêm dados aninhados em múltiplas colunas, utilizando o separador
        definido para concatenar os níveis aninhados no nome das colunas.

        Args:
            list_contents (list): Lista de dicionários JSON a ser normalizada.
            sep (str, opcional): Separador para os níveis aninhados.

        Returns:
            pd.DataFrame: Um DataFrame contendo os dados normalizados com
                          colunas planas, onde os nomes das colunas aninhadas
                          são concatenados usando o separador fornecido.

        Exemplo de Uso:
            data = [{"id": 1, "info": {"name": "Item1", "value": 100}},
                    {"id": 2, "info": {"name": "Item2", "value": 200}}]
            df = normalize_data(data, sep="__")
        """
        # Normaliza a lista de dicionários JSON, expandindo estruturas aninhadas
        return pd.json_normalize(list_contents, sep=sep)

    @staticmethod
    def handle_dict_columns_and_drop_duplicates(
        df: pd.DataFrame, primary_key: str
    ) -> pd.DataFrame:
        """
        Trata colunas com valores do tipo dict antes de aplicar drop_duplicates.

        Este método:
        1. Identifica colunas que possuem valores do tipo dict.
        2. Cria um DataFrame separado com as colunas dict e a primary key.
        3. Converte as colunas dict para string no DataFrame original.
        4. Aplica drop_duplicates no DataFrame original.
        5. Recupera as colunas dict utilizando a chave primary key.

        Parâmetros:
        -----------
        df : pd.DataFrame
            O DataFrame original a ser processado.
        primary_key : str
            O nome da coluna que será utilizada como chave primária.

        Retorna:
        --------
        pd.DataFrame
            O DataFrame resultante após o processamento e remoção de duplicatas.
        """
        # Garantir que a chave primária está presente no DataFrame
        if primary_key not in df.columns:
            raise DataFrameFormatError(
                f"A coluna '{primary_key}' não está presente no DataFrame."
            )

        # Identificar colunas que possuem valores do tipo dict
        dict_columns = [
            column
            for column in df.columns
            if df[column].apply(lambda x: isinstance(x, dict)).any()
        ]

        dict_df = None
        if dict_columns:
            # Criar um DataFrame separado com as colunas dict e a primary key
            dict_df = df[[primary_key] + dict_columns].copy()

            # Converter colunas dict para string no DataFrame original
            for column in dict_columns:
                df[column] = df[column].apply(
                    lambda x: json.dumps(x) if isinstance(x, dict) else x
                )

        # Aplicar drop_duplicates no DataFrame original
        df = df.drop_duplicates()

        if dict_df is not None:
            # Recuperar as colunas dict usando a chave primária
            dict_df = dict_df.drop_duplicates(subset=[primary_key])
            df = pd.merge(
                df, dict_df, on=primary_key, how="left", suffixes=("", "_dict")
            )

            # Remover colunas dict convertida em string do DataFrame original
            df.drop(columns=dict_columns, inplace=True)

            # Renomear as colunas com sufixo "_dict" obtidas do
            # dataframe dict_df
            df.rename(
                columns={
                    col: col.replace("_dict", "")
                    for col in df.columns
                    if col.endswith("_dict")
                },
                inplace=True,
            )

        return df

    @staticmethod
    def find_all_numeric(
        df: pd.DataFrame,
        col: Optional[str] = None,
        number_type: Literal["int", "float", "both"] = "both",
    ) -> List[Tuple[Hashable, str]]:
        """
        Procura todos os valores numéricos em um DataFrame, podendo buscar em
        uma coluna específica ou no DataFrame inteiro, com opção de  especificar
         o tipo de número.

        Parâmetros:
            df (pd.DataFrame): O DataFrame a ser analisado.
            col (str, opcional): Nome da coluna onde será feita a busca. Se
                None, a função verifica todas as  colunas.
            number_type (Literal["int", "float", "both"], opcional): Tipo de
                número a ser buscado. Valores possíveis: "int", "float" ou
                "both". O padrão é "both".

        Retorna:
            List[Tuple[Hashable,, str]]: Uma lista de tuplas contendo os índices
                das linhas e os nomes das colunas onde valores numéricos foram
                encontrados. Caso não encontre, retorna uma lista vazia.

        Exemplo:
        ```python
        import pandas as pd
        data = {
            "A": ["Texto", "Outro texto", "Mais texto", "Número aqui"],
            "B": [None, None, 123, None],
            "C": [None, 456.78, None, 789]
        }
        df = pd.DataFrame(data)

        # Procurando todos os valores numéricos na coluna "B"
        print(DataFrameUtils.find_all_numeric(df, col="B"))
        # Saída: [(2, "B")]

        # Procurando todos os valores numéricos no DataFrame inteiro
        print(DataFrameUtils.find_all_numeric(df, number_type="both"))
        # Saída: [(2, "B"), (1, "C"), (3, "C")]
        ```
        """

        def is_valid_number(value):
            """
            Verifica se o valor atende aos critérios de número de acordo com
            number_type.
            """
            if pd.isna(value):
                return False
            if number_type == "int":
                return isinstance(value, int)
            if number_type == "float":
                return isinstance(value, float)
            if number_type == "both":
                return isinstance(value, (int, float))
            return False

        results = []
        if col:
            # Busca apenas na coluna especificada
            for index, value in df[col].items():
                if is_valid_number(value):
                    results.append((index, col))
        else:
            # Busca em todas as colunas
            for col_name in df.columns:
                for index, value in df[col_name].items():
                    if is_valid_number(value):
                        results.append((index, col_name))
        return results

    @staticmethod
    def find_rows_with_dates(
        df: pd.DataFrame,
        col: Optional[str] = None,
        date_format: str = r"\d{2}/\d{2}/\d{4}",
    ) -> List[Tuple[Hashable, str]]:
        """
        Encontra linhas em um DataFrame que contêm datas no formato
        especificado, com a opção de buscar apenas em uma coluna específica.

        Parâmetros:
            df (pd.DataFrame): O DataFrame a ser analisado.
            date_format (str): Expressão regular para identificar datas. O
                padrão é `dd/mm/yyyy`.
            col (str, opcional): Nome da coluna onde será feita a busca. Se
                None, a busca será realizada em todas as colunas.

        Retorna:
            - List[Tuple[Hashable, str]]: Uma lista de tuplas no formato (
                índice, nome da coluna) para cada célula que contém uma data no
                formato especificado. Caso não encontre, retorna uma lista
                vazia.

        Exemplo:
            ```python
            import pandas as pd

            data = {
                "Coluna1": ["Texto", "15/04/2023", "Outro texto"],
                "Coluna2": ["10/10/2023", "Informação", "15/05/2024"],
            }
            df = pd.DataFrame(data)

            # Busca em todo o DataFrame
            resultados = DataFrameUtils.find_rows_with_dates(df)
            print(resultados)
            # Possível saída: [(0, 'Coluna2'), (1, 'Coluna1'), (2, 'Coluna2')]

            # Busca em uma coluna específica
            resultados_coluna = DataFrameUtils.find_rows_with_dates(
                df, col="Coluna2")
            print(resultados_coluna)
            # Possível saída: [(0, 'Coluna2'), (2, 'Coluna2')]
            ```
        """
        matches = []

        if col:
            if col not in df.columns:
                raise ValueError(f"A coluna '{col}' não existe no DataFrame.")

            for index, value in df[col].items():
                if isinstance(value, str) and re.search(date_format, value):
                    matches.append((index, str(col)))
        else:
            for index, row in df.iterrows():
                for column, value in row.items():
                    if isinstance(value, str) and re.search(date_format, value):
                        matches.append((index, str(column)))

        return matches if matches else []

    @staticmethod
    def find_rows_with_keywords(
        df: pd.DataFrame, keywords: list[str], col: Optional[str] = None
    ) -> List[Tuple[Hashable, str]]:
        """
        Encontra linhas em um DataFrame que contêm palavras-chave específicas,
        com a opção de buscar apenas em uma coluna.

        Parâmetros:
        -----------
        df : pd.DataFrame
            O DataFrame a ser analisado.

        keywords : list[str]
            Lista de palavras-chave a serem procuradas.

        col : str, opcional
            Nome da coluna onde será feita a busca. Se None, a busca será
            realizada em todas as colunas.

        Retorna:
        --------
        list[tuple[Hashable, str]]
            Uma lista de tuplas no formato (índice, nome da coluna) para cada
            célula que contém uma palavra-chave. Caso nenhuma correspondência
            seja encontrada, retorna uma lista vazia.

        Exemplo:
        --------
        ```python
        import pandas as pd

        data = {
            "Coluna1": ["Texto", "acesso ao sistema", "Outro texto"],
            "Coluna2": ["https://exemplo.com", "Informação", "Disponível"],
        }
        df = pd.DataFrame(data)

        # Busca em todo o DataFrame
        resultados = DataFrameUtils.find_rows_with_keywords(
            df, keywords=["acesso", "disponível", "https"]
        )
        print(resultados)
        # Saída:
        # [(0, 'Coluna2'), (1, 'Coluna1'), (2, 'Coluna2')]

        # Busca em uma coluna específica
        resultados_coluna = DataFrameUtils.find_rows_with_keywords(
            df, keywords=["acesso", "disponível"], col="Coluna1"
        )
        print(resultados_coluna)
        # Saída:
        # [(1, 'Coluna1')]
        ```

        Notas:
        ------
        - Se `col` for fornecido, a busca será restrita a essa coluna.
        - Caso contrário, a busca será feita em todas as colunas.
        - A busca é case-insensitive (não diferencia maiúsculas de minúsculas).
        """
        matches = []
        keywords_pattern = "|".join(map(re.escape, keywords))

        if col:
            # Verifica se a coluna especificada existe no DataFrame
            if col not in df.columns:
                raise DataFrameFormatError(
                    f"A coluna '{col}' não existe no DataFrame."
                )

            # Busca apenas na coluna especificada
            for index, value in df[col].items():
                if isinstance(value, str) and re.search(
                    rf"\b({keywords_pattern})\b", value, flags=re.IGNORECASE
                ):
                    matches.append((index, col))
        else:
            # Busca em todas as colunas
            for index, row in df.iterrows():
                for column, value in row.items():
                    if isinstance(value, str) and re.search(
                        rf"\b({keywords_pattern})\b", value, flags=re.IGNORECASE
                    ):
                        matches.append((index, str(column)))

        return matches if matches else []

    @staticmethod
    def remove_column_if_all_nan(
        df: pd.DataFrame, col_pos: int, inplace=False
    ) -> pd.DataFrame:
        """
        Remove uma coluna de um DataFrame se todos os seus valores forem NaN
        (não numéricos).

        Parâmetros
        ----------
        df : pd.DataFrame
            O DataFrame de onde a coluna será removida.
        col_pos : int
            A posição (índice) da coluna no DataFrame que será avaliada e
            possivelmente removida.
        inplace : bool, opcional
            Se True, a operação será feita diretamente no DataFrame original
            (padrão: False).
            Se False, um novo DataFrame será retornado sem a coluna removida.

        Retorna
        -------
        pd.DataFrame
            O DataFrame atualizado, caso `inplace` seja False. Caso contrário,
            retorna o próprio DataFrame modificado.

        Exceções
        --------
        IndexError
            Levantada se `col_pos` estiver fora do intervalo de índices de
            colunas disponíveis no DataFrame.

        Exemplos
        --------
        ```python
            import pandas as pd
            import numpy as np
            df = pd.DataFrame({
                'A': [1, 2, 3],
                'B': [np.nan, np.nan, np.nan],
                'C': [4, 5, 6]
            })
            df = drop_column(df, col_pos=1, inplace=False)
            print(df)
               A  C
            0  1  4
            1  2  5
            2  3  6

            drop_column(df, col_pos=0, inplace=True)
            print(df)
               C
            0  4
            1  5
            2  6
        ```
        """
        col_index = df.columns[col_pos]
        if df[col_index].isna().all():
            if inplace:
                df.drop(columns=[col_index], inplace=True)
                return df
            return df.drop(columns=[col_index])
        return df

    @staticmethod
    def to_int(arr_dtype: pd.Series) -> pd.Series:
        """
        Converte uma série do Pandas para o tipo inteiro nativo `Int64`,
        preservando valores nulos.

        O método verifica se a série especificada é do tipo inteiro
        (`integer dtype`). Caso não seja, tenta realizar a conversão de cada
        elemento da série para inteiro, substituindo valores nulos (`NaN`)
        por `pd.NA`.

        Parâmetros
        ----------
        arr_dtype : pd.Series
            A série Pandas que será convertida para o tipo inteiro `Int64`.

        Retorna
        -------
        pd.Series
            Uma série convertida para o tipo `Int64`, se a série original não
            for do tipo inteiro. Caso a série já seja do tipo inteiro, ela será
            retornada sem alterações.

        Exceções
        --------
        ValueError
            Levantado se a conversão falhar devido a dados incompatíveis.

        Exemplos
        --------
        ```python
            import pandas as pd
            import numpy as np
            data = pd.Series(['1', '2', None, '4'])
            result = to_int(data)
            print(result)
            0       1
            1       2
            2    <NA>
            3       4
            dtype: Int64
            print(result.dtype)
            Int64
        ```
        """
        # Verifica se a série já está no tipo inteiro
        if pd.api.types.is_integer_dtype(arr_dtype):
            return arr_dtype

        # Converte os valores não escalares
        def safe_convert_to_int(value):
            if pd.isna(value):
                return None
            if pd.api.types.is_scalar(value):
                try:
                    return int(value)
                except (ValueError, TypeError) as err:
                    raise DataFrameFormatError(
                        f"Valor  {value} inválido para conversão, error: {err}"
                    ) from err
            raise DataFrameFormatError(f"Valor não escalar encontrado: {value}")

        # Aplica a conversão segura e retorna como Int64
        return arr_dtype.apply(safe_convert_to_int).astype("Int64")

    @staticmethod
    def to_float(valor) -> float:
        """
        Converte um valor para float, considerando diferentes formatos de
        entrada.

        Args:
        valor: O valor a ser convertido para float (pode ser str, int ou float).

        Returns:
        float: O valor convertido para float.

        Raises:
        ConversionError: Se a conversão falhar.
        """
        # Verifica se o valor já é um float
        if isinstance(valor, float):
            return valor

        # Converte int para float
        if isinstance(valor, int):
            return float(valor)

        # Converte outros tipos para string, se necessário
        if not isinstance(valor, str):
            valor = str(valor)

        # Regex para capturar valores monetários
        pattern = r"R?\$?\s?(\d{1,3}(?:\.\d{3})*|\d+)(,\d{2})?"

        # Usa regex para encontrar o padrão
        match = re.search(pattern, valor)

        if match:
            try:
                # Extrai o valor numérico
                value = match.group(0)
                # Remove qualquer símbolo de moeda e espaço
                value = (
                    value.replace("R$", "").replace("$", "").replace(" ", "")
                )
                # Substitui vírgula por ponto
                value = value.replace(",", ".")
                # Remove pontos de milhar, se existirem
                if value.count(".") > 1:
                    value = value.replace(".", "", value.count(".") - 1)
                # Converte para float
                return float(value)
            except ValueError as err:
                # Levanta uma exceção específica se a conversão falhar
                raise DataFrameFormatError(
                    f"Erro ao converter '{valor}' para float: {err}"
                ) from err
        else:
            raise DataFrameFormatError(
                f"Nenhum valor encontrado na string: '{valor}'"
            )

    @staticmethod
    def find_first_row_with_keyword(df: pd.DataFrame, keyword: str) -> int:
        """
        Encontra o índice da primeira linha de um DataFrame que contém a
        palavra-chave em qualquer coluna.

        Parâmetros
        ----------
        df : pd.DataFrame
            O DataFrame onde a busca será realizada.
        keyword : str
            A palavra-chave a ser procurada nas colunas do DataFrame.

        Retorna
        -------
        int
            O índice da primeira linha onde a palavra-chave foi encontrada.
            Retorna -1 se a palavra-chave não for encontrada.

        Exemplos
        --------
        ```python
            import pandas as pd
            data = {
                'Nome': ['João Silva', 'Maria Oliveira', 'Carlos Souza'],
                'Idade': [34, 28, 45]
            }
            df = pd.DataFrame(data)
            print(df)
                        Nome  Idade
            0     João Silva     34
            1  Maria Oliveira     28
            2   Carlos Souza     45

            index = DataFrameUtils.find_first_row_with_keyword(df, 'Silva')
            print(index)
            0

            index = DataFrameUtils.find_first_row_with_keyword(df, 'Pereira')
            print(index)
            -1
        ```
        """
        # Cria uma máscara booleana indicando linhas com a palavra-chave
        mask = df.apply(
            lambda row: row.astype(str).str.contains(
                keyword, case=False, na=False
            ),
            axis=1,
        ).any(axis=1)

        # Verifica se existe alguma linha correspondente
        if not mask.any():
            return -1

        # Retorna o índice da primeira linha encontrada
        return mask.idxmax()

    @staticmethod
    def has_custom_index(df: pd.DataFrame) -> bool:
        """
        Verifica se o DataFrame possui um índice configurado explicitamente
        ou se o índice é diferente do padrão RangeIndex.

        Parâmetros:
        -----------
        df : pd.DataFrame
            O DataFrame a ser verificado.

        Retorna:
        --------
        bool
            True se o DataFrame possuir um índice configurado explicitamente
            ou diferente de RangeIndex, False caso contrário.
        """
        return df.index.name is not None or not df.index.equals(
            pd.RangeIndex(start=0, stop=len(df))
        )

    @staticmethod
    def to_uppercase(df: pd.DataFrame) -> pd.DataFrame:
        """
        Converte todas as strings em um DataFrame para letras maiúsculas de
        forma segura.

        Este método verifica cada elemento do DataFrame e converte os valores
        do tipo string para letras maiúsculas. Ele ignora valores nulos
        (`None`) e strings específicas como "None", além de tratar erros
        durante a conversão, garantindo que os dados sejam padronizados e
        consistentes para operações futuras.

        Parâmetros:
            df (pd.DataFrame): O DataFrame a ser processado.

        Retorna:
            pd.DataFrame: O DataFrame com as strings convertidas para letras
                          maiúsculas.

        Notas:
            - Strings contendo "None" (literal) não são convertidas para
                maiúsculas.
            - Valores nulos ou não string permanecem inalterados.
            - Caso ocorra um erro ao processar um valor, ele será retornado no
              formato original.

        Exemplo de Uso:
        ```python
        import pandas as pd
        data = {
            "col1": ["abc", None, "123", "None"],
            "col2": ["xyz", "123", "None", None],
        }
        df = pd.DataFrame(data)
        df = DataFrameUtils.to_uppercase(df)
        print(df)
           col1   col2
        0   ABC    XYZ
        1  None    123
        2   123   None
        3  None   None
        ```
        """

        def safe_uppercase(value: Any) -> Any:
            """
            Tenta converter um valor para letras maiúsculas se for uma string
            (exceto "none").

            Parâmetros:
                value (Any): O valor a ser processado.

            Retorna:
                Any: O valor convertido para letras maiúsculas, se possível;
                     caso contrário, o valor original.
            """
            try:
                if isinstance(value, str) and value.lower() != "none":
                    return value.upper()
            except (ValueError, TypeError) as err:
                logger.warning(
                    "Falha ao converter para maiúscula: %s. Retornando o "
                    "valor original: %s",
                    err,
                    value,
                )
            return value

        # Aplica a conversão segura a cada elemento do DataFrame
        return df.applymap(safe_uppercase)  # type: ignore

    @staticmethod
    def check_for_mixed_types(
        df: pd.DataFrame, w: Optional[List[warnings.WarningMessage]] = None
    ) -> List:
        """
        Detecta colunas com tipos mistos em um DataFrame e verifica se um
        DtypeWarning está presente.

        Esta função identifica colunas em um DataFrame que possuem tipos de
        dados mistos. Caso uma lista de warnings capturados seja fornecida,
        ela verifica se há DtypeWarning e exibe uma mensagem informativa se
        detectado.  A função retorna os nomes das colunas com tipos
        inconsistentes.

        Parâmetros:
            df (pd.DataFrame): O DataFrame a ser analisado.
            w (list, opcional): Uma lista de warnings capturados, normalmente
                                obtida de warnings.catch_warnings(record=True).
                                Se não fornecida, a análise será feita sem
                                contexto de warnings.

        Retorno:
            list: Uma lista com os nomes das colunas que possuem tipos mistos.

        Exemplo de Uso:
        ```python
            import pandas as pd
            import warnings
            dados = {
                "coluna1": ["abc", 123, None],
                "coluna2": [1.1, 2.2, "texto"],
                "coluna3": [True, False, None],
            }
            df = pd.DataFrame(dados)
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                colunas_mistas = DataFrameUtils.check_for_mixed_types(df, w)
            print("Colunas com tipos mistos:", colunas_mistas)
        ```
        """
        # Inicializa a lista para colunas com tipos mistos
        columns_mixed = []

        # Verifica se warnings foram fornecidos
        if w is not None:
            # Filtra os warnings para identificar DtypeWarning
            dtype_warnings = [
                warning
                for warning in w
                if issubclass(warning.category, pd.errors.DtypeWarning)
            ]
            columns_index_mixed = []
            if dtype_warnings:
                for dtype_warning in dtype_warnings:
                    warning_message = str(dtype_warning.message)
                    logger.warning(
                        "DtypeWarning detectado: %s. Analisando colunas com "
                        "possíveis tipos mistos...",
                        warning_message,
                    )
                    # Expressão regular para encontrar números entre parênteses
                    # após "Columns"
                    match = re.search(r"Columns \((.*?)\)", warning_message)
                    if match:
                        # Divide os números encontrados e converte para inteiros
                        columns_index_mixed.extend(
                            [
                                int(index.strip())
                                for index in match.group(1).split(",")
                            ]
                        )
                # Obtém os nomes das colunas com tipos mistos
                columns_mixed = [
                    df.columns[index] for index in columns_index_mixed
                ]
            return columns_mixed

        # Analisa o DataFrame em busca de colunas com tipos mistos
        for coluna in df.columns:
            # Mapeia os tipos de cada valor da coluna e obtém os tipos únicos
            tipos_unicos = df[coluna].map(type).unique()

            # Se houver mais de um tipo único, é uma coluna com tipos mistos
            if len(tipos_unicos) > 1:
                columns_mixed.append(coluna)

        return columns_mixed
