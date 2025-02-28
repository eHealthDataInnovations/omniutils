import pandas as pd
import numpy as np
import pytest
from omniutils.dataframe_utils import DataFrameUtils
from omniutils.exceptions import DataFrameFormatError

def test_filter_rows_by_keywords():
    data = {
        "Nome": ["Alice", "Bob", "Carlos", "Diana"],
        "Descrição": ["Gerente de projetos", "Engenheiro de dados", "Analista de sistemas", "Desenvolvedora full-stack"]
    }
    df = pd.DataFrame(data)
    result = DataFrameUtils.filter_rows_by_keywords(df, ["dados", "projetos"], "Descrição")
    assert not result.empty
    with pytest.raises(DataFrameFormatError):
        DataFrameUtils.filter_rows_by_keywords(df, ["dados"], "Inexistente")

def test_find_next_all_nan_row():
    data = {
        "A": [1, 2, np.nan, np.nan, 5],
        "B": [np.nan, 2, np.nan, np.nan, np.nan],
        "C": [3, np.nan, np.nan, np.nan, np.nan],
    }
    df = pd.DataFrame(data)
    idx = DataFrameUtils.find_next_all_nan_row(df, start_idx=1)
    assert idx == 2
