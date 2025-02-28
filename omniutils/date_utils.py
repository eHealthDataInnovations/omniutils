# Definição do tipo para os meses
from datetime import datetime
from typing import Literal

MonthType = Literal[
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
]

MONTH_PARSER = {
    "janeiro": 1,
    "fevereiro": 2,
    "março": 3,
    "abril": 4,
    "maio": 5,
    "junho": 6,
    "julho": 7,
    "agosto": 8,
    "setembro": 9,
    "outubro": 10,
    "novembro": 11,
    "dezembro": 12,
}


class DateUtils:
    """
    Conjunto de métodos utilitários para operações envolvendo datas.
    """

    @staticmethod
    def to_datetime(day: int, month: MonthType, year: int) -> datetime:
        """
        Converte uma data, representada por dia, nome do mês e ano, para um objeto datetime.

        Este método converte o nome do mês (em formato de string, como "janeiro", "fevereiro", etc.)
        para o número correspondente (1 para janeiro, 2 para fevereiro, etc.) utilizando o dicionário
        `MONTH_PARSER`. Se o nome do mês não for encontrado no dicionário, um ValueError é levantado.

        Parâmetros:
            day (int): O dia do mês (1-31).
            month (MonthType): O nome do mês em português (por exemplo, "janeiro", "fevereiro", etc.).
            year (int): O ano (por exemplo, 2023).

        Retorna:
            datetime: Um objeto datetime representando a data informada.

        Exceções:
            ValueError: Se o nome do mês fornecido não for reconhecido no dicionário `MONTH_PARSER`.

        Exemplos de uso:
        ```python
        from date_utils import DateUtils

        # Converter a data 15 de março de 2023 para um objeto datetime
        dt = DateUtils.to_datetime(15, "março", 2023)
        print(dt)  # Saída: 2023-03-15 00:00:00
        ```
        """
        # Converte o mês para número
        month_number = MONTH_PARSER.get(month.lower())
        if not month_number:
            raise ValueError(f"Nome do mês '{month}' inválido.")

        return datetime(year, month_number, day)
