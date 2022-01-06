"""Create table using Matplotlib."""
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
    heading_cell = "red"
    heading_font = "white"
    table_font = "black"


@dataclass
class FontSize:
    heading = 25
    table = 18


@dataclass
class FontSettings:
    text_align = "left"
    text_align_row_header = "left"
    text_align_table = "center"
    fontweight = "normal"
    # Row header font weight is usually normal whereas the table cells have bold font.
    fontweight_row_header = "normal"
    fontweight_table = "bold"
    fontweight_heading = "bold"


@dataclass
class Spacing:
    row = 0.03
    col = 0.01
    # These are offsets for different column types - if it's a row_header column the text
    # should be flush to the left of the cell, whereas the others (eg percentages within
    # the rest of the data) will be centered within the cell rather than left aligned.
    txt_disp_offset = 0.02
    value_disp_offset = 0.5


@dataclass
class CellSizes:
    row_header_col_width = 1.0
    # Not sure there would ever be any sense in there being different heights for the
    # row_header and other cells here, it would render pretty oddly as a table.
    row_header_col_height = 0.5
    numb_col_height = 0.5
    numb_col_width = 0.4
    height = 0.5


@dataclass
class PlotValues:
    # Feel there's a better name than "PlotValues" for this, "CellValues" might be
    # clearer.
    cell_alpha = 0.85


@dataclass
class DisplayOptions:
    column_headers = True


@dataclass
class PlotParams:
    colors = Colors()
    fontsizes = FontSize()
    font_settings = FontSettings()
    spacing = Spacing()
    cell_sizes = CellSizes()
    plot_values = PlotValues()
    display_options = DisplayOptions()


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
    cell_colors: pd.DataFrame,
    cell_values: pd.DataFrame,
    font_colors: pd.DataFrame | None = None,
    ax: plt.Axes,
    plot_params: PlotParams = PlotParams(),
) -> plt.Axes:
    """
    Create custom table.

    Adjust `plot_params` if the default settings aren't suitable.

    Assumes that the first column of the dataframes contain the row_header information.
    Where a row_header is typically a sentance or so explaining what the row within the
    table represents.
    """
    # Simple checks on the input data.
    if not all(cell_values.columns == cell_colors.columns):
        raise ValueError(
            (
                "Expect `cell_values.columns"
                " == cell_colors.columns`, "
                f"cell_values.columns : {cell_values.columns}, "
                f"cell_colors.columns : {cell_colors.columns}"
            )
        )

    # Should consider making this access more consistent as there's currently the case of
    # there being a row from a dataframe or something else when there's a header row
    # instead. Could just have the header row as part of a dataframe/matrix instead and
    # then an index or something which determined what type of row it was? Though that
    # might make things more clunky usage wise.
    if font_colors is None:
        font_colors = cell_colors.applymap(lambda _: plot_params.colors.table_font)

    # height/width of cells columns is consistent across all rows - typically the
    # row_header column will be wider to accomodate the explanation.
    column_widths: list[float] = [plot_params.cell_sizes.row_header_col_width] + [
        plot_params.cell_sizes.numb_col_width
    ] * (len(cell_values.columns) - 1)
    column_heights: list[float] = [plot_params.cell_sizes.row_header_col_height] + [
        plot_params.cell_sizes.numb_col_height
    ] * (len(cell_values.columns) - 1)

    # Want an index for all rows as well as the header row.
    row_indices = list(range(len(cell_colors) + 1))
    # Final row plotted is the header row.
    header_row_values = [False] * len(cell_colors) + [True]

    # Each cell value is offset so that text isn't plotted right on the edge - text cell
    # (first column) it left aligned, whereas the others are centered. This doesn't
    # change if it's a heading or a table value.
    display_offset = [plot_params.spacing.txt_disp_offset] + [
        plot_params.spacing.value_disp_offset
    ] * (cell_colors.shape[1] - 1)

    # All value columns have text alignment center except for the row_header column,
    # which are left aligned.
    text_align = [plot_params.font_settings.text_align_row_header] + [
        plot_params.font_settings.text_align_table
    ] * (cell_values.shape[1] - 1)

    for row_i, header_val in zip(row_indices, header_row_values):
        if header_val and not plot_params.display_options.column_headers:
            # If not plotting the column headers then just break here.
            break
        # Lot of if's here as the heading row (with column names) has different
        # formatting to the rest... there's probably a cleaner way of going about this.
        row_values = (
            cell_values.iloc[row_i, :].to_list()
            if not header_val
            else list(cell_values.columns)
        )
        row_colors = (
            cell_colors.iloc[row_i, :].to_list()
            if not header_val
            else [plot_params.colors.heading_cell for _ in cell_values]
        )
        row_font_color = (
            font_colors.iloc[row_i, :].to_list()
            if not header_val
            else plot_params.colors.heading_font
        )
        row_font_size = (
            plot_params.fontsizes.table
            if not header_val
            else plot_params.fontsizes.heading
        )
        row_font_weight = (
            [plot_params.font_settings.fontweight_row_header]
            + (
                [plot_params.font_settings.fontweight_table]
                * (cell_values.shape[1] - 1)
            )
            if not header_val
            else [plot_params.font_settings.fontweight_heading] * cell_values.shape[1]
        )

        plot_row(
            ax=ax,
            column_widths=column_widths,
            column_heights=column_heights,
            y_value=(
                row_i * plot_params.cell_sizes.height + plot_params.spacing.row * row_i
            ),
            colors=row_colors,
            values=row_values,
            font_color=row_font_color,
            cell_gap=plot_params.spacing.col,
            fontsize=row_font_size,
            patch_alpha=plot_params.plot_values.cell_alpha,
            display_offset=display_offset,
            font_weight=row_font_weight,
            text_align=text_align,
        )

    format_axis(ax=ax)
    ax.autoscale(tight=True)
    return ax
