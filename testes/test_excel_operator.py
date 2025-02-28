import openpyxl

from omniutils.excel_operator import ExcelOperator


def test_check_figures_in_excel_no_images(tmp_path):
    # Cria uma nova planilha sem imagens
    work_book = openpyxl.Workbook()
    sheet = work_book.active
    sheet.title = "Sheet1"
    file_path = tmp_path / "test.xlsx"
    work_book.save(file_path)

    figures_found, sheet_names = ExcelOperator.check_figures_in_excel(
        str(file_path)
    )

    # Como não há imagens, figures_found deve ser False e a lista de folhas com
    # imagens deve estar vazia.
    assert figures_found is False
    assert not sheet_names
