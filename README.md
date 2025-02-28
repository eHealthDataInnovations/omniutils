# OmniUtils

OmniUtils é uma biblioteca Python que consolida uma série de módulos utilitários usados em diversos projetos. Ela fornece funcionalidades para:

- **Processamento de texto:** Normalização, tokenização, extração de números, remoção de caracteres ilegais e muito mais.
- **Manipulação de DataFrames:** Filtragem, conversão de tipos, normalização de dados e extração de informações.
- **Operações com arquivos:** Renomear arquivos e extensões, copiar, sanitizar nomes de arquivos, listar e limpar diretórios.
- **Manipulação de datas:** Conversão de componentes de datas (dia, mês, ano) para objetos `datetime`.
- **Operações com Excel:** Verificação de figuras em arquivos Excel usando `openpyxl`.
- **Interação com APIs e web:** Realiza requisições HTTP com retry, manipula cache de requisições, extrai conteúdo HTML com BeautifulSoup e obtém informações de data de modificação a partir do GitHub.
- **Outros utilitários:** Funções para expandir dicionários recursivamente, verificação de configurações e rastreamento de chamadas (com suporte ao pycallgraph2).

A biblioteca foi construída para evitar a repetição de código entre projetos, permitindo que você mantenha uma única fonte de utilitários confiáveis e testados.

## Instalação

Como a OmniUtils é uma coleção de módulos Python, você pode simplesmente cloná-la e incluí-la no seu projeto. Por exemplo:

```bash
git clone https://github.com/seu-usuario/omniutils.git
```

Em seguida, adicione o diretório da biblioteca ao seu `PYTHONPATH` ou instale-a localmente usando:

```bash
pip install -e /caminho/para/omniutils
```

## Estrutura do Projeto

A biblioteca está organizada em vários módulos, cada um focado em um conjunto específico de funcionalidades:

- **text_utils.py:**  
  Contém funções para normalização de strings, tokenização, extração de números com palavras-chave, remoção de sufixos numéricos, extração de conteúdo entre parênteses, tratamento de endereços HTTP, e outras operações de processamento de texto.

- **dataframe_utils.py:**  
  Fornece métodos para filtrar, converter e transformar dados em DataFrames do pandas. Inclui funções para filtrar linhas por palavras-chave, identificar linhas com valores NaN, converter colunas para tipos numéricos ou strings, normalizar dados e lidar com colunas contendo dicionários.

- **date_utils.py:**  
  Contém funções para converter componentes de data (dia, nome do mês, ano) em objetos `datetime` e outras operações relacionadas à data.

- **dictionary_utils.py:**  
  Possui métodos para expandir recursivamente dicionários que contêm listas, transformando estruturas aninhadas em uma lista de dicionários com chaves compostas.

- **excel_operator.py:**  
  Fornece operações básicas com arquivos Excel utilizando a biblioteca `openpyxl`, como a verificação da presença de figuras (imagens) em planilhas.

- **exceptions.py:**  
  Define exceções personalizadas para o processamento de dados, facilitando o tratamento de erros específicos dentro dos módulos da biblioteca.

- **file_operator.py:**  
  Oferece métodos para manipulação de arquivos e diretórios, incluindo renomear arquivos (totalmente ou parcialmente), alterar extensões, extrair partes de caminhos, copiar arquivos, verificar a existência de arquivos e limpar diretórios.

- **github.py:**  
  Contém funções para interagir com a API do GitHub, como obter a data da última modificação de um arquivo em um repositório.

- **graph_tracer (GraphTracerAbstract e decorators):**  
  Fornece classes e decorators para rastrear a execução de funções e gerar diagramas de chamadas usando o `pycallgraph2`.

- **check_settings.py:**  
  Inclui uma função que carrega o arquivo de configurações (settings.py) de um projeto.

## Exemplos de Uso

### Normalização de Texto

```python
from omniutils.text_utils import TextUtils

texto = "São Paulo - 2023!"
resultado = TextUtils.normalize_str(texto, special_char="", space_char="_")
print(resultado)  # Saída: "sao_paulo_2023"
```

### Filtragem de DataFrame

```python
import pandas as pd
from omniutils.dataframe_utils import DataFrameUtils

data = {
    "Nome": ["Alice", "Bob", "Carlos", "Diana"],
    "Descrição": [
        "Gerente de projetos",
        "Engenheiro de dados",
        "Analista de sistemas",
        "Desenvolvedora full-stack"
    ]
}
df = pd.DataFrame(data)
resultado = DataFrameUtils.filter_rows_by_keywords(df, ["dados", "projetos"], "Descrição")
print(resultado)
```

### Conversão de Data

```python
from omniutils.date_utils import DateUtils

dt = DateUtils.to_datetime(15, "março", 2023)
print(dt)  # Saída: 2023-03-15 00:00:00
```

### Renomeando Arquivos

```python
from omniutils.file_operator import FileOperator

novo_caminho = FileOperator.rename_file("/caminho/para/arquivo.txt", insert_text="v2")
print(novo_caminho)
```

### Obtenção da Data de Última Modificação no GitHub

```python
from omniutils.github import get_last_modified_date

data_modificacao = get_last_modified_date("arquivo.txt", token="seu_token", owner="seu_owner", repo="seu_repo")
print(data_modificacao)
```

###  Rastreamento de Chamadas com GraphTracerAbstract
```python
from omniutils.graph_tracer import GraphTracerAbstract

class MyGraphTracer(GraphTracerAbstract):
    @classmethod
    def get_trace_filter(cls):
        # Retorna um filtro que inclui funções do seu pacote
        from pycallgraph2 import GlobbingFilter
        return GlobbingFilter(include=["omniutils.*"], exclude=["omniutils.tests.*"])

    @classmethod
    def get_trace_grouper(cls):
        # Retorna um agrupador de funções conforme sua preferência
        from pycallgraph2 import Grouper
        return Grouper(groups={"Core": "omniutils.*"})

    @classmethod
    def my_function(cls, x, y):
        return x + y

    @classmethod
    @GraphTracerAbstract.trace_graph
    def traced_function(cls, a, b):
        result = cls.my_function(a, b)
        return result

# Exemplo de uso:
resultado = MyGraphTracer.traced_function(5, 10)
print(resultado)
```


## Requisitos

- Python 3.10 ou superior
- Bibliotecas dependentes:
  - `requests`
  - `requests_cache`
  - `beautifulsoup4`
  - `htmldate`
  - `pandas`
  - `openpyxl`
  - `pycallgraph2`
  - Entre outras (consulte o arquivo `requirements.txt` para detalhes)

## Contribuição

Contribuições são bem-vindas! Se você deseja melhorar a OmniUtils ou adicionar novas funcionalidades, por favor, siga as diretrizes do nosso [CONTRIBUTING.md](CONTRIBUTING.md).

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## Contato

Para dúvidas, sugestões ou reportar problemas, abra uma _issue_ no repositório ou entre em contato através do [jailtoncarlos@gmail.com](mailto:jailtoncarlos@gmail.com).
