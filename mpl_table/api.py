"""Create heatmap table."""
from __future__ import annotations

from dataclasses import dataclass

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# --------------------------------------------------------------------------------------
# Default parameters.
@dataclass
class Colors:
    color_empty_cell = "#f2f2f2"
    color_heading = "red"
    color_heading_font = "white"
    color_table_font = "black"


@dataclass
class FontSize:
    fontsize_heading = 25
    fontsize_table = 18


@dataclass
class FontSettings:
    text_align = "left"
    fontweight = "normal"


@dataclass
class Spacing:
    spacing_row = 0.03
    spacing_col = 0.01
    # These are offsets for different column types - if it's a text column the text
    # should be flush to the left of the cell, whereas the others (percentages within the
    # rest of the data) will be centered within the cell rather than left aligned.
    txt_disp_offset = 0.02
    value_disp_offset = 0.5


@dataclass
class CellSizes:
    text_col_width = 1.0
    text_col_height = 0.5
    numb_col_height = 0.5
    numb_col_width = 0.4
    height = 0.5


@dataclass
class PlotValues:
    cell_alpha = 0.85


@dataclass
class PlotParams:
    colors = Colors()
    fontsizes = FontSize()
    spacing = Spacing()
    cell_sizes = CellSizes()
    plot_values = PlotValues()


class TableCell:  # pylint: disable=too-many-instance-attributes
    """Class representing a cell within the output table."""

    def __init__(
        self,
        width: float,
        height: float,
        x_pos: float,
        y_pos: float,
        color: str,
        value: str,
        font_color: str,
        display_x_offset: float,
        display_y_offset: float,
        text_align: str,
        fontweight: str,
        fontsize: int,
        patch_alpha: float,
    ):
        self.width = width
        self.height = height
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.color = color
        self.value = value

        self.patch_alpha = patch_alpha
        self.font_color = font_color
        # Text positioning - this will change depending on whether the cell is a text
        # cell or a value cell
        self.text_x_pos = x_pos + (display_x_offset * width)
        self.text_y_pos = y_pos + (display_y_offset * height)
        self.text_align = text_align

        self.fontweight = fontweight
        self.fontsize = fontsize

    def draw(self, *, ax: plt.Axes) -> None:
        ax.add_patch(
            mpl.patches.Rectangle(
                (self.x_pos, self.y_pos),
                width=self.width,
                height=self.height,
                color=self.color,
                alpha=self.patch_alpha,
            )
        )
        ax.text(
            # want to have all text in the center of the cells.
            x=self.text_x_pos,
            y=self.text_y_pos,
            s=self.value,
            horizontalalignment=self.text_align,
            # don't think there's a need for _not_ aligning text vertically in the
            # centre.
            verticalalignment="center",
            fontsize=self.fontsize,
            color=self.font_color,
            fontweight=self.fontweight,
        )


def format_axis(
    *,
    ax: plt.Axes,
) -> None:
    ax.axes.get_xaxis().set_visible(False)
    ax.axes.get_yaxis().set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_visible(False)


def plot_row(  # pylint: disable=too-many-locals
    *,
    ax: plt.Axes,
    fontsize: int,
    cell_gap: float,
    patch_alpha: float,
    y_value: float,
    column_widths: list[float],
    column_heights: list[float],
    colors: list[str],
    values: list[str],
    font_color: list[str],
    display_offset: list[float],
    font_weight: list[str],
    text_align: list[str],
) -> plt.Axes:
    """
    Plot a single row of the table.

    Values are passed in for a particular row - so `column_names` is each of the columns
    relating to the

    """
    computed_cells: list[TableCell] = []

    info_data = pd.DataFrame(
        {
            "cell_color": colors,
            "cell_value": values,
            "column_width": column_widths,
            "column_height": column_heights,
            # Don't need the last element from this array - want to have the x_loc as the
            # far left side of the patch to draw, which will exclude the final patches
            # largest x-value (will just plot from the left side of the last patch).
            "cell_x_loc": np.cumsum([0.0] + column_widths)[:-1],
            "font_color": font_color,
            "disp_offset": display_offset,
            "font_weight": font_weight,
            "text_align": text_align,
        }
    )

    for row in info_data.itertuples():
        # account for a bit of spacing around the cells.
        cell_width_gapped = row.column_width - cell_gap

        soft_cell = TableCell(
            width=cell_width_gapped,
            height=row.column_height,
            x_pos=row.cell_x_loc,
            y_pos=y_value,
            color=row.cell_color,
            value=row.cell_value,
            patch_alpha=patch_alpha,
            font_color=row.font_color,
            display_x_offset=row.disp_offset,
            # It's assumed that things will be centered within the cells atm, maybe this
            # could be parameterised though.
            display_y_offset=0.5,
            text_align=row.text_align,
            fontweight=row.font_weight,
            fontsize=fontsize,
        )
        computed_cells.append(soft_cell)

    # Draw row of cells.
    for cell in computed_cells:
        cell.draw(ax=ax)

    return ax


def table_with_row_headers(
    *,
    format_dataframe: pd.DataFrame,
    percentage_dataframe: pd.DataFrame,
    font_color_dataframe: pd.DataFrame | None = None,
    ax: plt.Axes,
    default_params: PlotParams = PlotParams(),
    # Currently need to pass the row_header column as there are some things handled
    # differently depending on whether it's the row_header column or not (row_header
    # column will typically have different dimensions to the rest of the columns).
    row_header: str,
) -> plt.Axes:
    """
    Create custom heatmap.

    If the default settings aren't appropriate there might be some need to adjust the
    default parameters, for example if the text column width is too large you might do
    something similar to:

    Assumes that the dataframe is structured so that the first column to plot is a column
    containing text descriptions of the values within those rows.
    """
    # Simple checks on the input data.
    if not all(percentage_dataframe.columns == format_dataframe.columns):
        raise ValueError(
            (
                "Expect `percentage_dataframe.columns"
                " == format_dataframe.columns`, "
                f"percentage_dataframe.columns : {percentage_dataframe.columns}, "
                f"format_dataframe.columns : {format_dataframe.columns}"
            )
        )
    if not percentage_dataframe.columns[0] == row_header:
        raise ValueError(
            "Expect the first column to be the row_header column, "
            f"row_header given is {row_header}, first"
            f" column is {percentage_dataframe.columns[0]}"
        )

    # Should consider making this access more consistent as there's currently the case of
    # there being a row from a dataframe or something else when there's a header row
    # instead. Could just have the header row as part of a dataframe/matrix instead and
    # then an index or something which determined what type of row it was? Though that
    # might make things more clunky usage wise.
    if font_color_dataframe is None:
        font_color_dataframe = format_dataframe.applymap(
            lambda _: default_params.colors.color_table_font
        )

    column_widths = [default_params.cell_sizes.text_col_width] + [
        default_params.cell_sizes.numb_col_width
    ] * (len(percentage_dataframe.columns) - 1)
    column_heights = [default_params.cell_sizes.text_col_height] + [
        default_params.cell_sizes.numb_col_height
    ] * (len(percentage_dataframe.columns) - 1)

    # Want an index for all rows as well as the header row.
    row_indices = list(range(len(format_dataframe) + 1))
    # Final row plotted is the header row.
    header_row_values = [False] * len(format_dataframe) + [True]

    # Each cell value is offset so that text isn't plotted right on the edge - text cell
    # (first column) it left aligned, whereas the others are centered. This doesn't
    # change if it's a heading or a table value.
    display_offset = [default_params.spacing.txt_disp_offset] + [
        default_params.spacing.value_disp_offset
    ] * (format_dataframe.shape[1] - 1)

    # All value columns have text alignment center except for the row_header column,
    # which are left aligned.
    text_align = ["left"] + ["center"] * (percentage_dataframe.shape[1] - 1)

    for row_i, header_val in zip(row_indices, header_row_values):
        # Lot of if's here as the heading row (with column names) has different
        # formatting to the rest... there's probably a cleaner way of going about this.
        values = (
            percentage_dataframe.iloc[row_i, :].to_list()
            if not header_val
            else list(percentage_dataframe.columns)
        )
        cell_colors = (
            format_dataframe.iloc[row_i, :].to_list()
            if not header_val
            else [default_params.colors.color_heading for _ in percentage_dataframe]
        )
        font_color = (
            font_color_dataframe.iloc[row_i, :].to_list()
            if not header_val
            else default_params.colors.color_heading_font
        )
        font_size = (
            default_params.fontsizes.fontsize_table
            if not header_val
            else default_params.fontsizes.fontsize_heading
        )
        font_weight = (
            ["normal"] + (["bold"] * (percentage_dataframe.shape[1] - 1))
            if not header_val
            else ["bold"] * percentage_dataframe.shape[1]
        )

        plot_row(
            ax=ax,
            column_widths=column_widths,
            column_heights=column_heights,
            y_value=(
                row_i * default_params.cell_sizes.height
                + default_params.spacing.spacing_row * row_i
            ),
            colors=cell_colors,
            values=values,
            font_color=font_color,
            cell_gap=default_params.spacing.spacing_col,
            fontsize=font_size,
            patch_alpha=default_params.plot_values.cell_alpha,
            display_offset=display_offset,
            font_weight=font_weight,
            text_align=text_align,
        )

    format_axis(ax=ax)
    ax.autoscale(tight=True)
    return ax
