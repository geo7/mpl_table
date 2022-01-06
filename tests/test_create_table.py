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
        font_colors=text_color,
        plot_params=default,
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
        plot_params=default,
    )
    return fig


@pytest.mark.mpl_image_compare
def test_table_with_no_row_headers(
    cell_colors,
    cell_values,
    text_color,
):
    # Just want to get rid of the row_header column.
    cell_colors = cell_colors.iloc[:, 1:]
    font_colors = text_color.iloc[:, 1:]
    cell_values = cell_values.iloc[:, 1:]

    fig, ax = plt.subplots(figsize=(15, 5), ncols=1)
    plot_params = mpl_table.PlotParams()

    # Here we're removing the different settings between the row_header column and the
    # rest of the table, typically there would be different font weights / alignment etc.
    plot_params.cell_sizes.row_header_col_width = plot_params.cell_sizes.numb_col_width
    plot_params.font_settings.text_align_row_header = (
        plot_params.font_settings.text_align_table
    )
    plot_params.font_settings.fontweight_row_header = (
        plot_params.font_settings.fontweight_table
    )

    plot_params.fontsizes.heading = 15
    plot_params.fontsizes.table = 12

    # this is the spacing from the left of the cell to the text.
    plot_params.spacing.txt_disp_offset = plot_params.spacing.value_disp_offset

    mpl_table.table_with_row_headers(
        cell_colors=cell_colors,
        cell_values=cell_values,
        font_colors=font_colors,
        ax=ax,
    )
    return fig


@pytest.mark.mpl_image_compare
def test_table_with_no_row_headers_and_no_column_headers(
    cell_colors,
    cell_values,
    text_color,
):

    cell_colors = cell_colors.iloc[1:, 1:]
    font_colors = text_color.iloc[1:, 1:]
    cell_values = cell_values.iloc[1:, 1:]

    fig, ax = plt.subplots(figsize=(6, 6), ncols=1)

    plot_params = mpl_table.PlotParams()
    plot_params.cell_sizes.row_header_col_width = plot_params.cell_sizes.numb_col_width
    plot_params.font_settings.text_align_row_header = (
        plot_params.font_settings.text_align_table
    )
    plot_params.font_settings.fontweight_row_header = (
        plot_params.font_settings.fontweight_table
    )
    plot_params.fontsizes.heading = 10
    plot_params.fontsizes.table = 7
    # this is the spacing from the left of the cell to the text.
    plot_params.spacing.txt_disp_offset = plot_params.spacing.value_disp_offset
    plot_params.display_options.column_headers = False
    plot_params.spacing.row = plot_params.spacing.col

    mpl_table.table_with_row_headers(
        cell_colors=cell_colors,
        cell_values=cell_values,
        font_colors=font_colors,
        ax=ax,
    )
    return fig


@pytest.mark.mpl_image_compare
def test_subplots_1(
    cell_colors,
    cell_values,
    text_color,
):
    cell_colors = cell_colors.iloc[1:, 1:]
    font_colors = text_color.iloc[1:, 1:]
    cell_values = cell_values.iloc[1:, 1:]

    fig, axis = plt.subplots(figsize=(16, 6), ncols=2)

    ax = axis[0]
    plot_params = mpl_table.PlotParams()
    plot_params.cell_sizes.row_header_col_width = plot_params.cell_sizes.numb_col_width
    plot_params.font_settings.text_align_row_header = (
        plot_params.font_settings.text_align_table
    )
    plot_params.fontsizes.heading = 10
    plot_params.fontsizes.table = 12
    plot_params.font_settings.fontweight_table = "normal"
    plot_params.font_settings.fontweight_row_header = "normal"
    plot_params.spacing.txt_disp_offset = plot_params.spacing.value_disp_offset
    plot_params.display_options.column_headers = False
    plot_params.spacing.row = plot_params.spacing.col
    mpl_table.table_with_row_headers(
        cell_colors=cell_colors,
        cell_values=cell_values,
        font_colors=font_colors,
        ax=ax,
    )

    ax = axis[1]
    np_random = np.random.default_rng(1)
    (
        pd.DataFrame(
            [np.arange(0, 10) + np_random.normal(2, 0.5, 10) for _ in range(3)],
        ).T.plot(
            ax=ax,
            color=["red", "green", "gray"],
            linewidth=3,
            alpha=0.65,
        )
    )
    ax.grid(0.2, alpha=0.2)
    fig.suptitle("Some Subplots", fontsize=25)
    return fig
