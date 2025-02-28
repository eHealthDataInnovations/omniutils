# Contribuindo para o OmniUtils

Agradecemos seu interesse em contribuir para o OmniUtils! Sua ajuda é muito importante para tornar essa biblioteca cada vez melhor. Siga as diretrizes abaixo para que possamos integrar suas contribuições de forma organizada e consistente.

---

## Como Contribuir

### 1. Abrir Issues

- **Reportar Bugs:** Se você encontrar algum bug, por favor, abra uma issue descrevendo o problema, incluindo informações sobre o ambiente (versão do Python, sistema operacional, etc.) e passos para reproduzir o erro.
- **Solicitar Funcionalidades:** Se você tem uma ideia para uma nova funcionalidade, abra uma issue para debater a proposta antes de iniciar a implementação.

### 2. Fork e Pull Request

1. Faça um fork do repositório e clone-o localmente.
2. Crie uma branch para sua feature ou correção de bug:
   ```bash
   git checkout -b minha-feature
   ```
3. Faça as alterações necessárias seguindo as diretrizes de código e testes.
4. Certifique-se de que todos os testes passem.
5. Commit suas alterações com mensagens claras e descritivas:
   ```bash
   git commit -m "Descreva brevemente a feature ou correção"
   ```
6. Envie sua branch para o seu fork:
   ```bash
   git push origin minha-feature
   ```
7. Abra um Pull Request no repositório original, explicando as alterações e os motivos para a mudança.

### 3. Código e Estilo

- **Consistência:** Mantenha a consistência com o estilo de código já existente na biblioteca. Utilize `flake8` e `black` (ou as ferramentas que o projeto já utiliza) para garantir a formatação.
- **Documentação:** Atualize ou adicione a documentação dos métodos e classes conforme necessário. Exemplo de formatação para docstrings:
  ```python
  def minha_funcao(param1: int) -> str:
      """
      Descrição breve do que a função faz.

      Parâmetros:
          param1 (int): Descrição do parâmetro.

      Retorna:
          - str: Descrição do valor retornado.

      Exemplos de uso:
      ```python
      resultado = minha_funcao(10)
      print(resultado)  # Exemplo de saída
      ```
      """
      ...
  ```
- **Testes:** Se possível, inclua testes unitários para suas alterações ou novas funcionalidades. Isso ajuda a manter a estabilidade do projeto.

### 4. Revisão de Código

- Todos os Pull Requests serão revisados por um ou mais mantenedores do projeto. Esteja preparado para responder perguntas ou fazer ajustes conforme sugerido.

### 5. Comunicação

- Se tiver dúvidas, sinta-se à vontade para abrir uma issue ou participar das discussões no repositório.
- Mantenha sempre uma comunicação clara e respeitosa com a comunidade.

---

## Licença

Ao contribuir com este projeto, você concorda que suas contribuições serão licenciadas sob os termos da [MIT License](LICENSE).

---

Agradecemos sua colaboração e esperamos suas contribuições!

Equipe OmniUtils
