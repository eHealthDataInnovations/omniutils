import functools
import inspect
import logging
from abc import ABC, abstractmethod  # pylint: disable=no-name-in-module
from typing import Callable, Optional, Tuple

logger = logging.getLogger(__name__)


class StackLoggerAbstract(ABC):
    """
    Classe abstrata para rastreamento (logging) da pilha de chamadas de funções.

    Esta classe fornece métodos utilitários para extrair informações da pilha de
    chamadas (como nomes de módulo, função e linha) e um decorador que, ao
    envolver uma função, registra detalhes da execução (argumentos, retorno e
    a hierarquia de chamadas) filtrados de acordo com o framework em uso.

    Para utilizar esta classe, é necessário implementar o método abstrato
    `get_framework_name` que deve retornar o nome do framework (ou pacote
    principal) a ser considerado na filtragem da pilha de chamadas.
    """

    @abstractmethod
    def get_framework_name(self) -> str:
        """
        Retorna o nome do framework a ser utilizado para filtrar os frames da
        pilha.

        Retorna:
            - str: Nome do framework, por exemplo, "medication_framework".

        Exemplos de uso:
        ```python
        class MyStackLogger(StackLoggerAbstract):
            def get_framework_name(self) -> str:
                return "medication_framework"
        ```
        """

    @staticmethod
    def get_module_name(
        frame_info: inspect.FrameInfo,
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Obtém o nome do pacote e do módulo a partir das informações de um frame.

        Parâmetros:
            - frame_info (inspect.FrameInfo): Informações de um frame da pilha
                de chamadas.

        Retorna:
            - tuple: Uma tupla contendo o nome do pacote e o nome do módulo,
                respectivamente.

        Exemplos de uso:
        ```python
        import inspect
        frame_info = inspect.stack()[0]
        package, module = StackLoggerAbstract.get_module_name(frame_info)
        print(package, module)
        ```
        """
        package_name = None
        module_name = None
        module = inspect.getmodule(frame_info[0])
        if module:
            module_name_parts = module.__name__.split(".")
            package_name = module_name_parts[0]
            module_name = module_name_parts[-1]
        return package_name, module_name

    @staticmethod
    def get_class_name(frame_info: inspect.FrameInfo) -> Optional[str]:
        """
        Obtém o nome da classe a partir das informações de um frame, caso
        exista.

        Parâmetros:
            - frame_info (inspect.FrameInfo): Informações de um frame da pilha
            de chamadas.

        Retorna:
            - Optional[str]: O nome da classe se presente; caso contrário, None.

        Exemplos de uso:
        ```python
        import inspect
        frame_info = inspect.stack()[0]
        class_name = StackLoggerAbstract.get_class_name(frame_info)
        print(class_name)
        ```
        """
        instance = frame_info.frame.f_locals.get("self", None)
        if instance:
            return instance.__class__.__name__
        return None

    def stack_log(self, func: Callable) -> Callable:
        """
        Decorador para registrar informações detalhadas da pilha de chamadas ao
        executar uma função.

        Ao envolver uma função com este decorador, a execução registra no log:
          - A hierarquia de chamadas (linha, módulo e nome da função) de forma
            filtrada, considerando apenas os frames cujo pacote corresponda ao
            framework definido.
          - Os argumentos passados para a função e o valor de retorno.

        Parâmetros:
            - func (Callable): A função a ser decorada.

        Retorna:
            - Callable: A função decorada que, ao ser chamada, registra as
                informações da pilha de chamadas e seu comportamento.

        Exemplos de uso:
        ```python
        class MyStackLogger(StackLoggerAbstract):
            def get_framework_name(self) -> str:
                return "medication_framework"

        logger_instance = MyStackLogger()

        @logger_instance.stack_log
        def soma(a, b):
            return a + b

        resultado = soma(2, 3)
        print(resultado)  # Saída: 5
        ```
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            framework_name = self.get_framework_name()
            names = []
            stack = inspect.stack()

            for frame_info in stack:
                lineno = frame_info.lineno
                package_name, module_name = self.get_module_name(frame_info)
                function_name = frame_info.function
                # Ignora o próprio wrapper para evitar recursividade na
                # impressão
                if module_name and function_name and function_name != "wrapper":
                    name = f"[{lineno}]{module_name}.{function_name}"
                    if package_name == framework_name:
                        names.append(name)

            lineno_func = inspect.getsourcelines(func)[1]
            module_name_func = func.__module__.split(".")[-1]
            name_func = f"[{lineno_func}]{module_name_func}.{func.__name__}"
            names.insert(0, name_func)
            names.reverse()

            logger.debug("%s", " > ".join(names), extra={"verbose": 1})
            logger.debug(
                "args: %s, kwargs: %s", args, kwargs, extra={"verbose": 2}
            )

            result = func(*args, **kwargs)

            logger.debug("retorno: %s", result, extra={"verbose": 2})
            return result

        return wrapper
