# Definição do tipo para os meses
from datetime import datetime, date
from typing import Literal, Union, Optional

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

DataOuString = Union[str, date, datetime]


class DateUtils:
    """
    Conjunto de métodos utilitários para operações envolvendo datas.
    """

    @staticmethod
    def to_datetime(day: int, month: MonthType, year: int) -> datetime:
        """
        Converte uma data, representada por dia, nome do mês e ano, para um
        objeto datetime.

        Este método converte o nome do mês (em formato de string, como
        "janeiro", "fevereiro", etc.) para o número correspondente (1 para
        janeiro, 2 para fevereiro, etc.) utilizando o dicionário `MONTH_PARSER`.
         Se o nome do mês não for encontrado no dicionário, um ValueError é
        levantado.

        Parâmetros:
            day (int): O dia do mês (1-31).
            month (MonthType): O nome do mês em português (por exemplo,
                "janeiro", "fevereiro", etc.).
            year (int): O ano (por exemplo, 2023).

        Retorna:
            datetime: Um objeto datetime representando a data informada.

        Exceções:
            ValueError: Se o nome do mês fornecido não for reconhecido no
                dicionário `MONTH_PARSER`.

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

    @staticmethod
    def parse_datetime(value: DataOuString,
                       fmt: Optional[str] = None) -> datetime:
        """
        Converte o valor fornecido para um objeto datetime, utilizando um
        formato específico se fornecido, ou o padrão ISO 8601 caso contrário.

        Se o valor for uma string e um formato (fmt) for especificado, a
        conversão será feita com datetime.strptime. Caso fmt seja None, o método
         tentará utilizar datetime.fromisoformat. Se a string não contiver
        informações de horário, será feita a conversão como data e combinada
        com o horário mínimo.

        Parâmetros:
            value: Valor a ser convertido (pode ser uma string, date ou
                   datetime).
            fmt: (Opcional) String com o formato a ser utilizado para conversão.
                 Exemplo: "%d/%m/%Y %H:%M:%S". Se None, utiliza-se o padrão
                 ISO 8601.

        Retorna:
            datetime: Objeto datetime resultante da conversão.

        Exceções:
            ValueError: Se o valor não estiver em um formato compatível para
            conversão.
        """
        if isinstance(value, str):
            if fmt is not None:
                # Utiliza o formato especificado para conversão
                try:
                    return datetime.strptime(value, fmt)
                except ValueError as e:
                    raise ValueError(
                        f"Falha ao converter usando o formato '{fmt}': {e}")
            else:
                # Tenta converter a string como datetime usando o padrão ISO
                # 8601
                try:
                    return datetime.fromisoformat(value)
                except ValueError:
                    # Caso não contenha informação de horário, tenta converter
                    # como date
                    try:
                        d = date.fromisoformat(value)
                        return datetime.combine(d, datetime.min.time())
                    except ValueError:
                        raise ValueError("Impossível converter para datetime: "
                                         "string com formato inválido.")
        elif isinstance(value, date):
            return datetime.combine(value, datetime.min.time())
        elif isinstance(value, datetime):
            return value
        else:
            raise ValueError("Impossível converter para datetime, o valor "
                             "fornecido não é de um tipo reconhecido.")