import importlib.resources

import pandas as pd
import pytest

from . import resources


@pytest.fixture
def cell_colors() -> pd.DataFrame:
    with importlib.resources.path(resources, "cell_colors.csv") as fh:
        return pd.read_csv(fh)


@pytest.fixture
def cell_values() -> pd.DataFrame:
    with importlib.resources.path(resources, "percentages.csv") as fh:
        return pd.read_csv(fh)


@pytest.fixture
def text_color() -> pd.DataFrame:
    with importlib.resources.path(resources, "text_color.csv") as fh:
        return pd.read_csv(fh)
