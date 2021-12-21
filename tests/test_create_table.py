"""Test dots_and_lines module."""

from __future__ import annotations

import textwrap

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from matplotlib.figure import Figure

import mpl_table
from mpl_table import api



def sample_dataframes():
    """
    Create sample dataframes for testing.

    Not used anywhere, just left this here in case it's of use elsewhere/later on.
    """
    np_random = np.random.default_rng(1)
    nonsense = (
        "this is just some random text "
        "that can be used to create some sample data with "
        "nothing else to it really"
    )
    nrow = 5
    ncol = 5
    cell_values = pd.DataFrame(
        np.round(  # type: ignore[no-untyped-call]
            np_random.random((nrow, ncol)) * 100, 1
        ),
        columns=[f"col_{x}" for x in range(ncol)],
    )
    font_color = cell_values.applymap(lambda x: "white" if x < 20 else "black")
    color_map = mpl.cm.get_cmap(name="RdYlGn", lut=1000)
    df_cell_colors = cell_values.applymap(lambda x: color_map(int(x * 10)))

    # List containing the meaning of each of the rows in the output table.
    meaning_column = [
        "\n".join(
            textwrap.wrap(
                " ".join(
                    np_random.choice(nonsense.split(), np_random.integers(10, 50))
                ),
                60,
            )
        )[:148]
        for _ in range(nrow)
    ]
    cell_values = (
        cell_values.applymap(lambda x: f"{x}%\n({np_random.integers(0,100)}% total)")
        .assign(row_header=meaning_column)
        .set_index("row_header")
        .reset_index()
    )
    df_cell_colors = (
        df_cell_colors.assign(row_header="#f2f2f2")
        .set_index("row_header")
        .reset_index()
    )
    font_color = (
        font_color.assign(row_header="black").set_index("row_header").reset_index()
    )
    return df_cell_colors, cell_values, font_color


@pytest.mark.mpl_image_compare
def test_table_image(
    cell_colors,
    cell_values,
    text_color,
) -> Figure:
    fig, ax = plt.subplots(figsize=(35, 10))
    default = api.PlotParams()
    ax = mpl_table.table_with_row_headers(
        ax=ax,
        cell_colors=cell_colors,
        cell_values=cell_values,
        row_header="row_header",
        font_colors=text_color,
        default_params=default,
    )
    return fig


@pytest.mark.mpl_image_compare
def test_table_image_no_font_color_df(
    cell_colors,
    cell_values,
) -> Figure:
    fig, ax = plt.subplots(figsize=(35, 10))
    default = api.PlotParams()
    ax = mpl_table.table_with_row_headers(
        ax=ax,
        cell_colors=cell_colors,
        cell_values=cell_values,
        row_header="row_header",
        default_params=default,
    )
    return fig
