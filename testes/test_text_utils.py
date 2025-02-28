from datetime import datetime

import pytest  # type: ignore # pylint: disable=import-error

from omniutils.text_utils import TextUtils


def test_normalize_str():
    result = TextUtils.normalize_str(
        "Olá Mundo!", special_char="", space_char="_"
    )
    # Espera: acentos removidos, letras minúsculas, espaços substituídos por "_"
    assert result == "ola_mundo"


def test_normalize_text():
    result = TextUtils.normalize_text("Coração")
    assert result == "coracao"


def test_tokenize_and_sort():
    result = TextUtils.tokenize_and_sort("O rato roeu a roupa do rei de Roma")
    # Note que a ordem pode variar conforme o split; aqui o teste espera a
    # ordenação alfabética
    expected = "a de do o rato rei roeu roma roupa"
    assert result == expected


def test_extract_numbers_with_keywords():
    text = "O medicamento contém 500 mg e 10 ml por dose."
    result = TextUtils.extract_numbers_with_keywords(
        text, keywords=["mg", "ml"]
    )
    assert "500 MG" in result
    assert "10 ML" in result


def test_remove_numeric_suffix():
    assert TextUtils.remove_numeric_suffix("Capítulo 3") == "Capítulo "
    assert TextUtils.remove_numeric_suffix("Referência²") == "Referência"


def test_extract_text_between_parentheses():
    text = "Produto: (ABC-123) esse texto após"
    result = TextUtils.extract_text_between_parentheses(text)
    assert result == "ABC-123"


def test_extract_content_after_keyword1():
    text = "Valor da caixa: 120 comprimidos."
    special_chars_pattern = r'[\[\]{}\\(),.:;!?@#%^&*+=~`|<>"\'-]'
    result = TextUtils.extract_content_after_keyword(
        text,
        keyword="Valor",
        stopwords=["da", "caixa"],
        special_chars_pattern=special_chars_pattern,
    )
    # Aqui, dependendo da implementação, o resultado pode ser "120 comprimidos"
    # (sem caracteres especiais)
    assert "120" in result and "comprimidos" in result


def test_extract_content_after_keyword2():
    text = "Produto: válido [ABC-123], especial - em estoque."
    special_chars_pattern = r"[\\[\\],.-]"
    result = TextUtils.extract_content_after_keyword(
        text,
        keyword="Produto",
        stopwords=["válido", "especial", "em"],
        special_chars_pattern=special_chars_pattern,
    )
    # Espera-se que o resultado seja "ABC123 estoque"
    assert result == "ABC123 estoque"


def test_extract_number_after_keyword():
    result = TextUtils.extract_number_after_keyword(
        "Custo: 1.234,56", keyword="Custo"
    )
    assert result == 1234.56


def test_extract_number_after_last_x():
    result = TextUtils.extract_number_after_last_x(
        "Multiplicado por X 2,5 e depois X 3"
    )
    assert result == 3.0


def test_replace_comma_with_dot():
    result = TextUtils.replace_comma_with_dot("O valor é 1,23")
    assert result == "O valor é 1.23"


def test_remove_dot_between_numbers():
    result = TextUtils.remove_dot_between_numbers("O valor é 1.234 e 56.789")
    assert result == "O valor é 1234 e 56789"


def test_to_number_str():
    assert TextUtils.to_number_str(3.0) == "3"
    assert TextUtils.to_number_str("3.5") == "3.5"
    assert TextUtils.to_number_str("0000025.3000000") == "25.3"


def test_ensure_utf8():
    result = TextUtils.ensure_utf8("Hello \\u00E9")
    assert result == "Hello é"


def test_extract_http_address():
    text = ("Acesse https://www.example.com e "
            "http://teste.com para mais informações.")
    urls = TextUtils.extract_http_address(text)
    assert "https://www.example.com" in urls
    assert "http://teste.com" in urls


def test_extract_all_dates_as_datetime():
    text = "Datas: 21/12/2024, 25/12/2024 e 01/01/2025."
    dates = TextUtils.extract_all_dates_as_datetime(text)
    expected_dates = [
        pytest.approx(datetime(2024, 12, 21)),
        pytest.approx(datetime(2024, 12, 25)),
        pytest.approx(datetime(2025, 1, 1)),
    ]
    for datetime_value, exp in zip(dates, expected_dates):
        assert datetime_value == exp
