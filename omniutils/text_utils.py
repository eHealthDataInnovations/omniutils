import logging
import re
import unicodedata
from codecs import decode  # pylint: disable=no-name-in-module
from datetime import datetime
from typing import List, Optional, Union

logger = logging.getLogger(__name__)

STOPWORDS = ["do", "de", "da"]


class TextUtils:
    @staticmethod
    def normalize_str(
        text: str, special_char: str = "", space_char: str = "_"
    ) -> str:
        """
        Normaliza uma string, removendo acentos e caracteres especiais,
        e substitui espaços por um caractere específico.

        *** Útil para criar strings sanitizadas ou uniformizadas para uso como
        identificadores únicos (ex.: chaves de banco de dados, URLs,
        nomes de arquivos). ***

        Esta função transforma a string para letras minúsculas, remove
        acentos e caracteres especiais, substitui espaços por um caractere
        definido (como "_"), e mantém apenas letras, números e underscores.
        Quando nenhum caractere é especificado em `special_char`, os
        caracteres especiais são removidos.

        Parâmetros:
            text (str): A string a ser normalizada.
            special_char (str): O caractere que substituirá caracteres
                especiais. Caso não seja especificado (ou seja vazio), os
                caracteres especiais serão removidos.
            space_char (str): O caractere que substituirá espaços em branco.
                O padrão é "_".

        Retorna:
            str: A string normalizada, sem acentos e caracteres especiais, com
                 espaços substituídos pelo caractere especificado.

        Exemplo:
        ```python
            normalize_str("Olá Mundo!", "_", "-")
            # "ola-mundo"
            normalize_str("São Paulo - 2023!", "_", "_")
            # "sao_paulo_2023"
            normalize_str("Coração & Saúde!", "_", "_")
            # "coracao_saude"
            normalize_str("Arquivo com espaço.pdf", "-", "+")
            # "arquivo+com+espaco-pdf"
        ```
        """
        # Substituir espaços pelo caractere especificado
        text = text.replace(" ", space_char).lower()
        # Remover acentos e aplicar substituições de caracteres especiais
        # Permitir apenas letras, números e underscores
        return re.sub(
            r"[^A-Za-z0-9_]+",
            special_char,
            unicodedata.normalize("NFKD", text),
        )

    @staticmethod
    def normalize_text(text):
        """
        Normalize o texto removendo acentos, convertendo para letras minúsculas
        e eliminando espaços extras no início e no final.

        *** Útil em casos onde a preservação da estrutura do texto (incluindo
        caracteres especiais) é importante. ***

        Esta função é útil para padronizar strings antes de comparações,
        garantindo que diferenças de acentuação, capitalização ou espaços
        não impactem os resultados.

        Parâmetros
        ----------
        text : str
            O texto a ser normalizado. Caso não seja uma string, será retornado
            o valor original.

        Retorna
        -------
        str
            O texto normalizado, sem acentos, em letras minúsculas e sem espaços
            nas extremidades. Caso `text` não seja uma string, retorna o valor
            original sem alterações.

        Exemplos
        --------
         ```python
            TextUtils.normalize_text("Coração")
            # Saída: 'coracao'
            TextUtils.normalize_text("São Paulo - 2023!")
            # Saída: "sao paulo - 2023!"
            TextUtils.normalize_text(None)
            # Saída: None
            TextUtils.normalize_text(123)
            # Saída: 123
        ``´
        """
        if isinstance(text, str):
            return (
                "".join(
                    c
                    for c in unicodedata.normalize("NFD", text)
                    if unicodedata.category(c) != "Mn"
                )
                .lower()
                .strip()
            )
        return text

    @staticmethod
    def tokenize_and_sort(text: str) -> str:
        """
        Tokeniza uma string em palavras, ordena as palavras em ordem alfabética
        e retorna uma nova string com os tokens ordenados, separados por espaço.

        Esta função é útil para comparar strings sem levar em conta a ordem
        das palavras, padronizando a string em letras minúsculas e eliminando
        espaços extras antes e depois.

        Parâmetros
        ----------
        text : str
            A string a ser tokenizada e ordenada. Caso não seja uma string,
            o valor original será retornado.

        Retorna
        -------
        str
            Uma nova string com as palavras da entrada ordenadas em ordem
            alfabética e separadas por espaço. Caso `text` não seja uma string,
            retorna o valor original.

        Exemplos
        --------
        tokenize_and_sort("O rato roeu a roupa do rei de Roma")
        # Saída: 'a do de o raio rei roma roupa roeu'

        tokenize_and_sort("  Python é incrível!  ")
        # Saída: 'e incrivel python'

        tokenize_and_sort(None)
        # Saída: None

        tokenize_and_sort(123)
        # Saída: 123
        """
        if isinstance(text, str):
            return " ".join(sorted(text.lower().strip().split()))
        return text

    @staticmethod
    def extract_numbers_with_keywords(
        text, keywords: Optional[list[str]] = None
    ):
        """
        Extrai números associados a palavras-chave em um texto.

        Este método busca números no texto que estejam associados a
        palavras-chave específicas, como "mg", "ml", "g", etc. Ele é útil para
        identificar valores numéricos seguidos por unidades de medida ou outras
        palavras-chave relevantes.

        Parâmetros:
            text (str): O texto no qual será feita a busca.
            keywords (list): Lista de palavras-chave a serem procuradas no
                             texto. Por padrão, ["mg", "mg/ml", "ml", "g"].

        Retorna:
            list: Uma lista de strings contendo os números encontrados e suas
                  respectivas palavras-chave. Cada elemento é formatado como
                  "número palavra-chave".

        Exemplo de Uso:
            TextUtils.extract_numbers_with_keywords(
                    "O medicamento contém 500 mg e 10 ml por dose.",
                    keywords=["mg", "ml"]
                )
            ['500 MG', '10 ML']

        Detalhes da Implementação:
            - O padrão de regex identifica números no formato "123" ou "123,45"
              seguidos por qualquer palavra-chave definida.
            - As palavras-chave são definidas como um padrão opcional a ser
              buscado imediatamente após o número.
            - Os resultados são retornados em letras maiúsculas para
              uniformidade.

        Fluxo:
            1. Cria um padrão de regex para identificar números seguidos por
               palavras-chave fornecidas.
            2. Para cada número encontrado, verifica se há uma palavra-chave
               associada.
            3. Retorna uma lista de pares "número palavra-chave".

        Notas:
            - A regex utiliza o modificador `re.IGNORECASE` para tornar a busca
              insensível a maiúsculas/minúsculas.
            - O método suporta números com vírgulas como separador decimal.
        """

        if keywords is None:
            keywords = ["mg", "mg/ml", "ml", "g"]

        keywords_pattern = "|".join(map(re.escape, keywords))
        pattern = rf"(\d+(?:,\d+)?)\s*(?=\b(?:{keywords_pattern})\b)"
        matches = re.finditer(pattern, text, re.IGNORECASE)
        results = []
        for match in matches:
            number = match.group(1)
            keyword_match = re.search(
                rf"\b(?:{keywords_pattern})\b",
                text[match.end()],
                re.IGNORECASE,
            )
            keyword = keyword_match.group(0).upper() if keyword_match else None
            results.append(f"{number} {keyword}")
        return results

    @staticmethod
    def remove_numeric_suffix(text: str) -> str:
        """
        Remove sufixos numéricos ou sobrescritos de um texto.

        Este método identifica e remove caracteres numéricos no final de um
        texto. Ele é útil em situações onde números como "1", "2", "3" ou
        sobrescritos ("¹", "²", "³") aparecem no final de strings e devem ser
        eliminados.

        Parâmetros:
            text (str): O texto no qual o sufixo numérico será removido.

        Retorna:
            str: O texto sem o sufixo numérico. Caso nenhum sufixo seja
                 encontrado, o texto original é retornado.

        Exemplo de Uso:
            TextUtils.remove_numeric_suffix("Capítulo 3")
            # Saída: 'Capítulo'

            TextUtils.remove_numeric_suffix("Referência²")
            # Saída: 'Referência'

            TextUtils.remove_numeric_suffix("Texto sem número")
            # Saída: 'Texto sem número'

        Detalhes da Implementação:
            - Um padrão de regex é utilizado para identificar números e
              caracteres sobrescritos (`¹`, `²`, `³`) no final do texto.
            - Caso um padrão seja encontrado, ele é substituído por uma string
              vazia.
            - Se não houver correspondência, o texto original é retornado.

        Notas:
            - O método suporta números padrão (`0-9`) e sobrescritos Unicode.
            - O regex utiliza `$` para garantir que o número esteja no final da
              string.
        """
        pattern = r"[0-9¹²³]$"
        if re.search(pattern, text):
            return re.sub(pattern, "", text)
        return text

    @staticmethod
    def extract_text_between_parentheses(text, keyword=None, stopwords=None):
        """
        Extrai texto entre parênteses de uma string, opcionalmente buscando uma
        palavra-chave antes dos parênteses e ignorando stopwords.

        Este método busca conteúdo entre parênteses em um texto e pode,
        opcionalmente:
        - Buscar apenas conteúdo associado a uma palavra-chave específica.
        - Ignorar palavras indesejadas (stopwords) que aparecem após a
          palavra-chave.

        Parâmetros:
            text (str): O texto de entrada no qual será feita a busca.
            keyword (str, opcional): Uma palavra-chave para delimitar o início
                da busca.
            stopwords (list, opcional): Uma lista de palavras a serem ignoradas
                após a palavra-chave. Se não fornecida, será utilizado um
                conjunto padrão definido em `STOPWORDS`.

        Retorna:
            str: O texto extraído entre os parênteses, ou após a palavra-chave,
            sem as stopwords.

        Raises:
            ValueError: Se o padrão especificado não for encontrado no texto.

        Exemplo de Uso:
            ```
                text = "Produto: (ABC-123) esse texto após o caracter ')' "
                       "será removido."
                print(TextUtils.extract_text_between_parentheses(text,
                      keyword="Produto")
                )
                # Saída: 'ABC-123'

                text = "Produto: esse texto antes do caracter '(' tem que "
                       "incluir na stopword (ABC-123) para o teste."
                print(TextUtils.extract_text_between_parentheses(text,
                    keyword="Produto",
                    stopwords=[" ", "esse", "texto", "antes",  "do",
                    "caracter", "'('", "tem que incluir na stopword"] )
                )
                # Saída: 'ABC-123'
            ```

        Detalhes:
            - **Busca básica**: Quando `keyword` não é fornecida, o método
              procura pelo primeiro conteúdo entre parênteses.
            - **Busca com palavra-chave**: Se `keyword` é fornecida, o método
              busca pela palavra-chave e extrai o conteúdo entre parênteses
              associado a ela.
            - **Ignorando stopwords**: Quando uma lista de stopwords é
              fornecida, essas palavras são ignoradas no processamento.

        Padrões:
            - **Com `keyword`**: `{keyword} ... (conteúdo)` ou `{keyword}
              ... conteúdo`
            - **Sem `keyword`**: `(...conteúdo...)`

        Fluxo:
            1. Se `keyword` for fornecida:
                - Procura a palavra-chave no texto e busca por parênteses ou
                  outros tokens subsequentes.
                - Ignora stopwords, se fornecidas.
            2. Se `keyword` não for fornecida:
                - Procura por qualquer conteúdo entre parênteses no texto.
            3. Retorna o conteúdo encontrado.
            4. Caso o padrão não seja encontrado, levanta um erro `ValueError`.

        Observações:
            - A busca é insensível a maiúsculas/minúsculas (`re.IGNORECASE`).
            - O método considera a estrutura do texto, removendo espaços extras
              ao redor do conteúdo extraído.
        """
        if stopwords is None:
            stopwords = STOPWORDS
        stopwords_pattern = "|".join(map(re.escape, stopwords))
        if keyword:
            pattern = rf"{re.escape(keyword)}\s*(?::\s*)?(?:{stopwords_pattern})*\s*(?:\((?P<conteudo1>[^)]+)\)|(?P<conteudo2>\S+.*))"  # pylint: disable=line-too-long  # noqa: E501
        else:
            pattern = r"\((?P<conteudo>[^)]+)\)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if keyword:
                return (
                    match.group("conteudo1") or match.group("conteudo2")
                ).strip()
            return match.group("conteudo").strip()
        raise ValueError(f"Padrão não encontrado na string: '{text}'")

    @staticmethod
    def extract_content_after_keyword(
        text: str,
        keyword: str,
        stopwords: Optional[list[str]] = None,
        special_chars_pattern: Optional[str] = None,
    ) -> str:
        """
        Extrai o conteúdo após uma palavra-chave em um texto, removendo
        stopwords e caracteres especiais, se especificado.

        Esta função localiza a primeira ocorrência de uma palavra-chave em um
        texto, extrai o conteúdo subsequente e remove palavras indesejadas
        (stopwords). Opcionalmente, remove caracteres especiais definidos por
        uma expressão regular.

        Parâmetros:
            text (str): Texto de entrada.
            keyword (str): Palavra-chave após a qual o conteúdo será extraído.
            stopwords (list, opcional): Lista de palavras a serem ignoradas
                após a palavra-chave. Se não fornecido, será usado um conjunto
                padrão.
            special_chars_pattern (str, opcional): Expressão regular para
                remover caracteres especiais do conteúdo extraído. Se não
                fornecido, nenhum caractere especial será removido.

        Retorna:
            str: Conteúdo extraído após a palavra-chave, sem stopwords e
                 caracteres especiais, se especificado. Retorna uma string
                 vazia se a palavra-chave não for encontrada.

        Detalhes da Implementação:
            - **Palavra-chave**: O método localiza a palavra-chave usando
              `re.search` com correspondência insensível a
               maiúsculas/minúsculas.
            - **Stopwords**: Palavras indesejadas são ignoradas utilizando um
              padrão de regex construído com base na lista fornecida.
            - **Remoção de caracteres especiais**: Se um padrão for
              especificado, ele será aplicado ao conteúdo extraído.
            - **Conteúdo**: O texto após a palavra-chave é retornado limpo de
              stopwords e caracteres especiais.

        Fluxo:
            1. Constrói um padrão regex para localizar a palavra-chave e o
               conteúdo subsequente, ignorando stopwords.
            2. Realiza a busca pelo padrão no texto.
            3. Extrai o conteúdo encontrado e aplica remoções adicionais, se
               necessário.
            4. Retorna o conteúdo extraído ou uma string vazia se a
               palavra-chave não for encontrada.

        Notas:
            - O padrão regex é flexível para lidar com diferentes formatos de
              texto (e.g., "chave: valor", "chave valor").
            - Stopwords e caracteres especiais devem ser bem definidos para
              evitar remoções desnecessárias ou erradas.
        """
        if stopwords is None:
            stopwords = STOPWORDS

        stopwords_pattern = "|".join(map(re.escape, stopwords))

        # Constrói a regex para capturar o conteúdo após a palavra-chave,
        # ignorando caracteres e stopwords especificadas
        pattern = rf"{re.escape(keyword)}\s*(?::\s*)?(?:{stopwords_pattern})\
        *\s*(?P<conteudo>\S+.*)"

        # Usa regex para encontrar o padrão, ignorando maiúsculas/minúsculas
        match = re.search(pattern, text, re.IGNORECASE)

        # Verifica se houve correspondência
        if match:
            content = match.group("conteudo").strip()
            if special_chars_pattern:
                content = re.sub(special_chars_pattern, "", content)
            return content
        return ""

    @staticmethod
    def extract_number_after_keyword(
        text: str, keyword: Optional[str] = None
    ) -> float:
        """
        Extrai um número localizado após uma palavra-chave específica em uma
        string.

        Este método busca e extrai o primeiro número que aparece após uma
        palavra-chave fornecida. Se nenhuma palavra-chave for especificada, ele
        busca pelo primeiro número no formato esperado na string.

        Parâmetros
        ----------
        text : str
            O texto no qual o número será buscado.
        keyword : str, opcional
            A palavra-chave após a qual o número deve ser buscado. Se não
            fornecida, o método busca por qualquer número na string.

        Retorna
        -------
        float
            O número extraído, convertido para o formato `float`.

        Exceções
        --------
        ValueError
            - Levantado se nenhum padrão correspondente for encontrado na
              string.
            - Levantado se ocorrer uma falha ao converter o número extraído
              para `float`.

        Detalhes do Processamento
        -------------------------
        1. Se uma palavra-chave for fornecida:
            - Procura por números que aparecem imediatamente após a
              palavra-chave.
            - O número pode estar cercado por caracteres como parênteses ou
              espaços.
        2. Se nenhuma palavra-chave for fornecida:
            - Procura pelo primeiro número no texto, considerando formatos como:
              - `1.234,56`
              - `1234,56`
              - `1234`
        3. Converte o número encontrado para `float`, substituindo pontos por
           espaços decimais e vírgulas por pontos.
        4. Retorna o número como um valor `float`.

        Exemplos
        --------
        ```python
        assert extract_number_after_keyword(
            "O valor é 1.234,56.") == 1234.56
        assert extract_number_after_keyword(
            "Custo: 1234.") == 1234.0
        assert extract_number_after_keyword(
            "Custo R$ 13,8, total: R$ 1.234,80", keyword="Custo") == 13.8
        assert extract_number_after_keyword(
            "Custo: 12567") == 12567.0
        assert extract_number_after_keyword(
            "Valor 1235, total: R$ 123,34", keyword="total") == 123.34
        ```

        Dependências
        ------------
        - `re` : Usado para criar expressões regulares e buscar padrões no
        texto.

        """
        if keyword:
            # Regex para capturar número após palavra-chave
            pattern = rf"{re.escape(keyword)}.*?(?P<number>\d+(?:[.,]\d+)*)"
        else:
            # Regex genérico para capturar o primeiro número, incluindo ponto
            # final opcional
            pattern = r"(?P<number>\d+(?:[.,]\d+)*)"  # Modified regex

        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Trata separadores decimais e de milhar
            number_str = (
                match.group("number").replace(".", "").replace(",", ".")
            )
            try:
                return float(number_str)
            except ValueError as err:
                raise ValueError(
                    f"Falha ao converter o número: " f"'{number_str}'"
                ) from err
        else:
            raise ValueError(f"Padrão não encontrado na string: '{text}'")

    @staticmethod
    def extract_number_after_last_x(text: str) -> float:
        """
        Extrai o número imediatamente após a última ocorrência da letra "X" em
        um texto.

        Este método utiliza uma expressão regular para localizar números após
        a letra "X", onde o número pode incluir separadores como `.` ou `,`.
        O último número correspondente encontrado é convertido para o tipo
        `float` e retornado.

        Parâmetros
        ----------
        text : str
            O texto no qual o número será procurado.

        Retorna
        -------
        float
            O número extraído após a última ocorrência da letra "X".

        Exceções
        --------
        - Levanta `ValueError` se:
            - Nenhuma ocorrência do padrão for encontrada no texto.

        Detalhes
        --------
        - A busca é case-insensitive (não diferencia maiúsculas de minúsculas).
        - O número extraído pode conter separadores decimais no formato
          `.` ou `,`, que são convertidos para um formato padrão antes da
          conversão para `float`.

        Exemplo
        -------
        texto = "Este item foi multiplicado por X 2,5 e depois ajustado "
                    "por X 3."
        numero = TextUtils.extract_number_after_last_x(texto)
        print(numero)
        # Saída: 3.0

        Notas
        -----
        - O método pode ser usado para processar strings onde informações
          numéricas seguem uma notação com "X".
        """
        # Padrão para capturar a letra "X" seguida de um número
        pattern = r"X\s*(?P<number>\d+(?:[\.,]\d+)?)"

        # Encontra todas as correspondências no texto
        matches = list(re.finditer(pattern, text, re.IGNORECASE))

        if matches:
            # Seleciona a última correspondência
            match = matches[-1]
            number_str = (
                match.group("number").replace(".", "").replace(",", ".")
            )
            return float(number_str)

        raise ValueError(f"Padrão não encontrado na string: '{text}'")

    @staticmethod
    def extract_keywords_and_dates(
        text: str, keywords: Optional[list[str]] = None
    ) -> list[str]:
        """
        Extrai palavras-chave e datas de um texto.

        Este método identifica palavras-chave específicas e datas no formato
        `dd/mm/yyyy` em um texto, retornando uma lista contendo as ocorrências
        encontradas.

        Parâmetros
        ----------
        text : str
            O texto de entrada no qual as palavras-chave e as datas serão
            extraídas.

        Retorna
        -------
        List[str]
            Uma lista contendo as palavras-chave e/ou as datas encontradas no
            texto. As datas são retornadas no formato `dd/mm/yyyy`.

        Detalhes
        --------
        - O método utiliza um regex para localizar palavras-chave específicas:
          `acesso`, `disponível`, `https`, `www`.
        - Também identifica datas no formato `dd/mm/yyyy`.
        - A busca é case-insensitive (não diferencia maiúsculas de minúsculas).
        - Cada palavra-chave ou data encontrada é adicionada à lista de
          resultados.

        Exemplo
        -------
        ```
            texto = "O sistema está disponível em https://exemplo.com desde"
                        "15/04/2023."
            resultados = TextUtils.extract_keywords_and_dates(texto)
            print(resultados)
            # Saída: ['disponível', 'https', '15/04/2023']
        ```

        Notas
        -----
        - Palavras-chave e datas que ocorrem mais de uma vez serão listadas
          repetidamente na saída.
        - O método é útil para processar textos em busca de informações-chave,
          como URLs, palavras específicas e datas relevantes.
        """
        if not keywords:
            keywords = ["acesso", "disponível", "http", "https", "www"]

        # Criação do padrão para palavras-chave e datas no formato dd/mm/yyyy
        keywords_pattern = "|".join(map(re.escape, keywords))
        regex = rf"(?:\b({keywords_pattern})\b|(\d{{2}})/(\d{{2}})/(\d{{4}}))"

        # Encontra todas as correspondências no texto
        matches = re.findall(regex, text, re.IGNORECASE)

        results = []
        for match in matches:
            if match[0]:  # Palavra-chave encontrada
                results.append(match[0])
            else:  # Data encontrada
                results.append(f"{match[1]}/{match[2]}/{match[3]}")

        return results

    @staticmethod
    def remove_illegal_characters(text):
        """
        Remove caracteres ilegais de uma string.

        Este método remove caracteres considerados ilegais, como os caracteres
        de controle na faixa ASCII de 0 a 31. Esses caracteres geralmente não
        são exibíveis e podem causar problemas ao processar dados textuais.

        Parâmetros
        ----------
        text : str
            A string de entrada da qual os caracteres ilegais serão removidos.

        Retorna
        -------
        str
            A string limpa, sem os caracteres ilegais.

        Detalhes
        --------
        - O método define uma lista de caracteres ilegais
          (`ILLEGAL_CHARACTERS`), que inclui caracteres de controle ASCII de
          0 a 31.
        - Para cada caractere na lista, o método remove suas ocorrências na
          string de entrada.

        Exemplos
        --------
        ```
            texto_entrada = "Olá\x00Mundo"
            texto_limpo = remove_illegal_characters(texto_entrada)
            print(texto_limpo)
            # Saída: "OláMundo"
        ```

        Notas
        -----
        - Se o texto de entrada não for uma string, o método o retornará sem
          alterações.
        - A lista de caracteres ilegais pode ser expandida conforme necessário.
        """
        # Lista de caracteres ilegais com descrições
        illegal_characters = [
            chr(0),  # Null
            chr(1),  # Início de cabeçalho
            chr(2),  # Início de texto
            chr(3),  # Fim de texto
            chr(4),  # Fim de transmissão
            chr(5),  # Consulta
            chr(6),  # Reconhecimento
            chr(7),  # Sinal sonoro (bell)
            chr(8),  # Backspace
            chr(9),  # Tabulação horizontal
            chr(10),  # Line feed (nova linha)
            chr(11),  # Tabulação vertical
            chr(12),  # Form feed
            chr(13),  # Retorno de carro
            chr(14),  # Shift out
            chr(15),  # Shift in
            chr(16),  # Data link escape
            chr(17),  # Controle de dispositivo 1
            chr(18),  # Controle de dispositivo 2
            chr(19),  # Controle de dispositivo 3
            chr(20),  # Controle de dispositivo 4
            chr(21),  # Negative acknowledgment
            chr(22),  # Synchronous idle
            chr(23),  # End of transmission block
            chr(24),  # Cancel
            chr(25),  # End of medium
            chr(26),  # Substituto
            chr(27),  # Escape
            chr(28),  # Separador de arquivo
            chr(29),  # Separador de grupo
            chr(30),  # Separador de registro
            chr(31),  # Separador de unidade
        ]

        if isinstance(text, str):
            for char in illegal_characters:
                text = text.replace(char, "")
        return text

    @staticmethod
    def extract_until_empty(lista: list) -> list[str]:
        """
        Retorna os itens de uma lista antes do primeiro item vazio ('') e remove
        todos os itens vazios da lista.

        Se houver um item vazio, retorna todos os elementos até a primeira
        ocorrência de um item vazio, excluindo os itens vazios subsequentes. Se
        não houver item vazio, retorna a lista inteira sem os itens vazios.

        Parâmetros:
            lista (list): A lista de itens.

        Retorna:
            list[str]: Sublista com itens antes do primeiro item vazio ou a
                       lista inteira sem itens vazios se nenhum item vazio
                       existir.

        Exemplo:
        ```
            extract_until_empty(["a", "", "b", "c"])
            # Saída: ["a"]
            extract_until_empty(["a", "b", "c"])
            # Saída: ["a", "b", "c"]
        ```
        """
        if "" in lista:
            empty_index = lista.index("")
            return [item for item in lista[:empty_index] if item != ""]

        return [item for item in lista if item != ""]

    @staticmethod
    def ensure_utf8(text: str) -> str:
        """
        Garante que o texto fornecido esteja em formato UTF-8, decodificando
        sequências de escape Unicode, se presentes.

        Este método verifica se o texto contém sequências de escape Unicode
        (padrões no formato `\\uXXXX`). Se detectar essas sequências, ele
        decodifica o texto usando a codificação `unicode_escape`, convertendo
        os códigos para caracteres UTF-8 correspondentes. Após a decodificação,
        o texto é garantido como UTF-8.

        Parâmetros:
            text (str): O texto de entrada que pode conter caracteres Unicode
                        escapados.

        Retorna:
            str: O texto decodificado em UTF-8, com qualquer sequência de escape
                 Unicode convertida para seu caractere correspondente.

        Exemplo de Uso:
        ```
            ensure_utf8("Hello \\u00E9")
            # Saída: 'Hello é'
        ```

        Detalhes da Implementação:
            1. Usa uma expressão regular (`\\uXXXX`) para detectar sequências de
               escape Unicode no texto.
            2. Se essas sequências são encontradas, decodifica o texto com
               `unicode_escape` para converter as sequências para caracteres
               reais.
            3. Finalmente, o texto é re-encodado e decodificado em UTF-8 para
               garantir a compatibilidade com essa codificação.

        Observação:
            Esse método é especialmente útil para strings que incluem códigos
            Unicode escapados, como `\\u00E9` para `é`.
        """
        # Expressão regular para encontrar padrões unicode escapados (\uXXXX)
        unicode_escape_pattern = re.compile(r"\\u[0-9a-fA-F]{4}")

        # Se a string contém caracteres unicode escapados, decodificá-la
        if unicode_escape_pattern.search(text):
            text = decode(text, "unicode_escape")

        # Certificar-se de que a string esteja em formato UTF-8
        return text.encode("utf-8").decode("utf-8")

    @staticmethod
    def to_number_str(value: Union[int, float, str]) -> str:
        """
        Converte um valor para uma representação numérica em string, removendo
        zeros desnecessários após o ponto decimal se o número for inteiro.

        Esta função tenta converter o valor fornecido para um número `float`. Se
        a conversão for bem-sucedida e o valor representar um número inteiro, o
        valor é retornado como uma string de número inteiro
        (ex: "3" em vez de "3.0").
        Se o valor representar um número de ponto flutuante, ele é retornado
        como uma string com os decimais preservados. Caso o valor não possa ser
        convertido para `float`, ele é retornado em seu formato original.

        Parâmetros:
            value (Any): O valor a ser convertido para uma string numérica, se
                         possível.

        Retorna:
            str: O valor convertido para uma string numérica, com zero decimal
                 removido para inteiros.
            Any: O valor original, caso não seja possível convertê-lo para um
                 número.

        Exemplos:
        ```
            print(TextUtils.to_number_str(3.0))
            print(TextUtils.to_number_str(3.5))
            print(TextUtils.to_number_str("3.0"))
            print(TextUtils.to_number_str("abc"))
            print(TextUtils.to_number_str("0000025.3000000"))
            # Saída:
            # 3
            # 3.5
            # 3
            # abc
            # 25.3
        ```

        Detalhes da Implementação:
            1. Converte o valor para `float`. Se for bem-sucedido:
                - Verifica se o valor é um inteiro (ex: 3.0).
                - Se sim, converte-o para `int` e retorna como string.
                - Se não, retorna o `float` como string, preservando os
                decimais.
            2. Caso a conversão para `float` falhe, retorna o valor original.
        """
        try:
            # Tentar converter o valor para float
            float_value = float(value)
            if float_value.is_integer():
                # Remover zeros desnecessários convertendo para int se possível
                return str(int(float_value))

            # Não é inteiro, retorna float.
            return str(float_value)
        except ValueError as err:
            logger.warning(
                "Falha ao converter valor: %s. Retornando o valor "
                "original: %s.",
                err,
                value,
            )
        return str(value)

    @staticmethod
    def replace_comma_with_dot(text: str) -> str:
        """
        Substitui vírgulas por pontos decimais em números dentro de um texto.

        Este método identifica sequências numéricas no texto que utilizam
        vírgulas como separador decimal e as converte para o formato decimal de
        ponto, permitindo que os números estejam no formato adequado para
        operações numéricas em sistemas que utilizam o ponto como separador
        decimal.

        Parâmetros:
            text (str): Texto de entrada contendo números com vírgulas.

        Retorna:
            str: Texto com os números ajustados para utilizar ponto decimal como
                 separador.

        Exemplo de Uso:
            replace_comma_with_dot("O valor é 1,23 e 45,6.")
            'O valor é 1.23 e 45.6.'

        Detalhes da Implementação:
            - O método utiliza uma expressão regular para encontrar padrões de
              números no formato `<número>,<número>` e substitui a vírgula pelo
              ponto decimal.
        """
        # Substitui as vírgulas entre números por pontos decimais.
        return re.sub(r"(\d+),(\d+)", r"\1.\2", text)

    @staticmethod
    def remove_dot_between_numbers(text: str) -> str:
        """
        Remove pontos decimais entre números num texto, unindo os dígitos.

        Este método é útil em contextos onde os pontos decimais entre números
        foram inseridos de forma inadequada e devem ser removidos. O método
        encontra padrões de números no formato `<número>.<número>` e remove o
        ponto, deixando os números unidos sem separação.

        Parâmetros:
            text (str): Texto de entrada contendo números com pontos.

        Retorna:
            str: Texto com os pontos removidos entre números.

        Exemplo de Uso:
            remove_dot_between_numbers("O valor é 1.234 e 56.789.")
            'O valor é 1234 e 56789.'

        Detalhes da Implementação:
            - O método usa uma expressão regular para identificar padrões de
              números no formato `<número>.<número>` e substitui o ponto por uma
               string vazia,  efetivamente removendo o ponto.
        """
        # Substitui o ponto entre números por uma string vazia.
        return re.sub(r"(\d)\.(\d)", r"\1\2", text)

    @staticmethod
    def remove_special_characters_preserving_accents(texto):
        """
        Remove caracteres especiais de um texto, como ":", "(", ")", "-", "_",
        "/", mas preserva espaço e letras com acentos e cedilha.

        Parâmetros:
        -----------
        texto : str
            O texto do qual os caracteres especiais serão removidos.

        Retorna:
        --------
        str
            O texto com os caracteres especiais removidos, mantendo acentos.

        Nota:
        -----
        A expressão regular usada no re.sub remove apenas caracteres que não
        sejam letras (incluindo letras com acentos dentro do intervalo Unicode
        (À-ÿ), números ('\\w') ou espaços (\\s). Como os espaços estão
        explicitamente permitidos pela classe de caracteres \\s, eles
        permanecem no texto final.
        """
        # Substituir caracteres que não são letras com acentos, números ou
        # espaços
        clear_text = re.sub(r"[^\w\sÀ-ÿ]", "", texto)
        return clear_text

    @staticmethod
    def find_word_in_text(
        text: str, key_words: list
    ) -> tuple[Optional[str], str]:
        """
        Busca uma palavra-chave em um texto com base em um dicionário.

        Parâmetros:
            key_words (list): Lista de palavras ou tuplas com palavras para
                buscar.
            text (str): O texto no qual a busca será realizada.

        Retorna:
            tuple: Uma tupla contendo a palavra encontrada (ou None) e o texto
                sem a palavra encontrada.

        Exemplo de Uso:
        ```
            key_words = ['caixa', 'blister', 'frascos']
            text = "Valor da caixa com 120 comprimidos"

            resultado = TextUtils.find_word_in_text(text, key_words)
            print(resultado)
            # Saída: ('caixa', 'Valor da com 120 comprimidos')
        ```
        """
        # Cria um padrão regex com todas as palavras do dicionário
        pattern = (
            r"\b(" + "|".join(re.escape(word) for word in key_words) + r")\b"
        )

        # Procura no texto
        match = re.search(pattern, text, flags=re.IGNORECASE)

        if match:
            found_word = match.group(1)
            text_without_word = re.sub(
                pattern, "", text, count=1, flags=re.IGNORECASE
            ).strip()
            return found_word, text_without_word

        return None, text

    @staticmethod
    def extract_http_address(text: str) -> list[str]:
        """
        Extrai todos os endereços HTTP(S) de um texto fornecido.

        Parâmetros:
            text (str): Texto contendo um ou mais endereços HTTP(S).

        Retorna:
            list[str]: Lista de URLs encontradas no texto. Caso não encontre,
            retorna uma lista vazia.

        Exemplo:
        ```python
            text = "Cliquefarma. Disponível em: "
            "https://www.cliquefarma.com.br/medicamentos/especiais/"
            "zytiga-250mg-120-comprimidos. "
            "Acesso em: 26/01/2024."
            urls = extract_http_address(text)
            print(urls)

            # Saída:
            # ['https://www.cliquefarma.com.br/medicamentos/especiais'
               '/zytiga-250mg-120-comprimidos']
        ```
        """
        # Expressão regular para capturar URLs HTTP e HTTPS
        url_pattern = r"https?://[^\s]+"
        return re.findall(url_pattern, text)

    @staticmethod
    def extract_all_dates_as_datetime(
        text: str, date_pattern: str = r"\b\d{2}/\d{2}/\d{4}\b"
    ) -> List[datetime]:
        """
        Extrai todas as datas de um texto e as converte para objetos datetime.

        Parâmetros:
        -----------
        text : str
            O texto de entrada no qual as datas serão procuradas.

        date_pattern : str, opcional
            O padrão de expressão regular para identificar as datas.

        Retorna:
        --------
        List[datetime]
            Uma lista contendo as datas encontradas, convertidas para objetos
            datetime. Se nenhuma data for encontrada, retorna uma lista vazia.

        Exemplo:
        --------
        ```python
            text = "Hoje é 21/12/2024, o prazo final é 25/12/2024. "
                   "Outra data: 01/01/2025."
            dates = TextUtils.extract_all_dates_as_datetime(text)
            print(dates)
            # Saída: [datetime.datetime(2024, 12, 21, 0, 0),
            #         datetime.datetime(2024, 12, 25, 0, 0),
            #         datetime.datetime(2025, 1, 1, 0, 0)]
        """
        # Busca todas as datas no formato especificado
        raw_dates = re.findall(date_pattern, text)
        datetime_dates = []
        for date in raw_dates:
            try:
                # Converte a string de data para um objeto datetime
                datetime_dates.append(datetime.strptime(date, "%d/%m/%Y"))
            except ValueError as err:
                # Ignora datas inválidas
                print(f"Erro ao converter '{date}' para datetime: {err}")
        return datetime_dates
