import functools
import logging
import os
from abc import ABC, abstractmethod
from typing import Callable

from pycallgraph2 import Color, Config, GlobbingFilter, Grouper, PyCallGraph
from pycallgraph2.output import GraphvizOutput

logger = logging.getLogger(__name__)


class GraphTracerAbstract(ABC):
    """
    Classe abstrata que define a interface e a configuração para o rastreamento
    de chamadas de funções utilizando pycallgraph2 e Graphviz.

    Esta classe fornece os métodos necessários para configurar e gerar diagramas
    de rastreamento (call graphs) do fluxo de execução de funções. Os métodos
    abstratos `get_trace_filter` e `get_trace_grouper` devem ser implementados
    pelas classes filhas para definir os filtros e agrupadores específicos do
    rastreamento.

    Métodos:
        - get_trace_filter() -> GlobbingFilter:
            Retorna o filtro (GlobbingFilter) para o rastreamento.
        - get_trace_grouper() -> Grouper:
            Retorna o agrupador (Grouper) para o rastreamento.
        - _rainbow(node) -> Color:
            Calcula a cor de um nó do diagrama com base na fração de tempo de
            execução.
        - get_graphviz() -> GraphvizOutput:
            Retorna uma instância configurada de GraphvizOutput para gerar o
            diagrama.
        - get_config() -> Config:
            Retorna a configuração (Config) para o pycallgraph2, com filtros e
            agrupadores.
        - trace_graph(func) -> Callable:
            Decorator que gera um diagrama de rastreamento da execução da funçã
            o decorada.
    """

    graphviz: GraphvizOutput = None
    config: Config = None

    @abstractmethod
    @classmethod
    def get_trace_filter(cls) -> GlobbingFilter:
        """
        Define e retorna o filtro de rastreamento para o pycallgraph2.

        Deve ser implementado nas classes filhas para especificar quais módulos
        ou funções devem ser incluídos (ou excluídos) no rastreamento.

        Retorna:
            GlobbingFilter: Objeto que configura os filtros de rastreamento.
        """
        pass

    @abstractmethod
    @classmethod
    def get_trace_grouper(cls) -> Grouper:
        """
        Define e retorna o agrupador para o pycallgraph2.

        Deve ser implementado nas classes filhas para agrupar funções do
        rastreamento conforme a lógica de negócio desejada.

        Retorna:
            Grouper: Objeto que configura o agrupamento das chamadas.
        """
        pass

    @classmethod
    def rainbow(cls, node) -> Color:
        """
        Calcula a cor de um nó do diagrama com base na fração de tempo de
        execução.

        A cor é definida usando o modelo HSV, onde o matiz é proporcional à
        fração de tempo (variando de 0 a 0.8), resultando em uma sequência de
        cores que vão do vermelho, laranja, amarelo, verde, ciano, azul até
        roxo.

        Parâmetros:
            node: Objeto que representa um nó no diagrama, devendo possuir o
                  atributo `time.fraction` que indica a fração do tempo de
                  execução.

        Retorna:
            Color: Um objeto Color configurado com base na fração de tempo.

        Exemplos de uso:
        ```python
        from graph_tracer import MyGraphTracer  # Supondo implementação concreta

        # Supondo que 'node' possua o atributo time.fraction com valor 0.5,
        # a chamada abaixo retornará uma cor correspondente a um matiz
        # intermediário.
        cor = MyGraphTracer._rainbow(node)
        print(cor)
        ```
        """
        return Color.hsv(node.time.fraction * 0.8, 0.4, 0.9)

    @classmethod
    def get_graphviz(cls) -> GraphvizOutput:
        """
        Retorna uma instância configurada de GraphvizOutput para gerar o
        diagrama.

        Se a instância ainda não estiver definida, cria uma nova instância de
        GraphvizOutput, atribui a função de cor dos nós utilizando o método
        `_rainbow` e a retorna.

        Retorna:
            GraphvizOutput: Instância configurada para saída do Graphviz.

        Exemplos de uso:
        ```python
        from graph_tracer import MyGraphTracer  # Supondo implementação concreta

        graphviz = MyGraphTracer.get_graphviz()
        print(graphviz.output_file)  # Exibe o arquivo de saída configurado
        ```
        """
        if cls.graphviz is None:
            cls.graphviz = GraphvizOutput()
            cls.graphviz.node_color_func = cls.rainbow
        return cls.graphviz

    @classmethod
    def get_config(cls) -> Config:
        """
        Retorna a configuração do pycallgraph2 (objeto Config) para
        rastreamento de chamadas.

        Se a configuração ainda não estiver definida, cria uma nova instância
        de Config, atribuindo os filtros e agrupadores definidos pelos métodos
        abstratos `get_trace_filter()` e `get_trace_grouper()`.

        Retorna:
            Config: Instância de configuração para pycallgraph2.

        Exemplos de uso:
        ```python
        from graph_tracer import MyGraphTracer  # Supondo implementação concreta

        config = MyGraphTracer.get_config()
        print(config.trace_filter)
        ```
        """
        if cls.config is None:
            config = Config()
            config.trace_filter = cls.get_trace_filter()
            config.trace_grouper = cls.get_trace_grouper()
            cls.config = config
        return cls.config

    @classmethod
    def trace_graph(cls, func: Callable):
        """
        Decorator que gera um diagrama de rastreamento (call graph) da execução
        da função decorada.

        Ao aplicar este decorator, a função decorada terá seu fluxo de chamadas
        rastreado pelo pycallgraph2. O diagrama é salvo em um arquivo PNG cujo
        nome é derivado do nome completo da função (módulo + qualname). Durante
        a execução, o diagrama é gerado com a configuração definida em
        `get_config()` e a saída do Graphviz definida em `get_graphviz()`.

        Parâmetros:
            func (Callable): A função a ser rastreada.

        Retorna:
            Callable: A função decorada que, ao ser chamada, gera o diagrama de
            rastreamento.

        Exemplos de uso:
        ```python
        from graph_tracer import MyGraphTracer  # Supondo implementação concreta

        class MyGraphTracer(GraphTracerAbstract):
            @classmethod
            def get_trace_filter(cls) -> GlobbingFilter:
                # Retorne um GlobbingFilter adequado, por exemplo:
                from pycallgraph2 import GlobbingFilter
                return GlobbingFilter(include=["meupacote.*"])

            @classmethod
            def get_trace_grouper(cls) -> Grouper:
                # Retorne um Grouper adequado, por exemplo:
                from pycallgraph2 import Grouper
                return Grouper(groups={"MeuGrupo": "meupacote.*"})

        @MyGraphTracer.trace_graph
        def minha_funcao(x, y):
            return x + y

        resultado = minha_funcao(3, 4)
        # O diagrama de rastreamento será salvo em 'meumodulo.minha_funcao.png'
        print(resultado)  # Saída: 7
        ```
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            full_method_name = f"{func.__module__}.{func.__qualname__}"

            graphviz = cls.get_graphviz()
            graphviz.output_file = f"{full_method_name}.png"
            graphviz.graph_attributes["graph"]["label"] = full_method_name

            logger.debug(
                f"Graphviz - gerando diagrama do trace da função "
                f"{full_method_name}..."
            )

            with PyCallGraph(output=graphviz, config=cls.get_config()):
                result = func(*args, **kwargs)

            logger.debug(
                f"Diagrama salvo em {os.path.abspath(graphviz.output_file)}"
            )
            return result

        return wrapper
