import openpyxl


class ExcelOperator:
    """
    Classe utilitária para operações relacionadas a arquivos Excel.
    """

    @staticmethod
    def check_figures_in_excel(file_path):
        """
        Verifica se um arquivo Excel contém imagens (figuras) em suas planilhas.

        Este método carrega um arquivo Excel utilizando a biblioteca openpyxl e percorre
        todas as planilhas (sheets) para determinar se existem imagens incorporadas.
        A verificação é feita com base no atributo interno `_images` de cada planilha.

        Parâmetros:
            file_path (str): O caminho completo para o arquivo Excel a ser verificado.

        Retorna:
            tuple:
                - bool: True se pelo menos uma imagem for encontrada em alguma planilha;
                        False caso contrário.
                - list[str]: Uma lista contendo os nomes das planilhas que possuem imagens.

        Exemplo de uso:
        ```python
        from excel_operator import ExcelOperator

        # Defina o caminho para o arquivo Excel
        caminho_arquivo = "dados.xlsx"

        # Verifique se o arquivo contém imagens e obtenha os nomes das planilhas com figuras
        figuras_encontradas, planilhas_com_figuras = ExcelOperator.check_figures_in_excel(caminho_arquivo)

        if figuras_encontradas:
            print("Imagens encontradas nas seguintes planilhas:")
            for planilha in planilhas_com_figuras:
                print(planilha)
        else:
            print("Nenhuma imagem encontrada no arquivo Excel.")
        ```
        """
        workbook = openpyxl.load_workbook(file_path)
        figures_found = False
        sheet_names_with_figures = []
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            if sheet._images:
                figures_found = True
                sheet_names_with_figures.append(sheet_name)
        return figures_found, sheet_names_with_figures
