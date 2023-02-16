from typing import Optional

import matplotlib.figure as mpl
import pandas as pd
from prefect import task

from cell_abm_pipeline.utilities.plot import make_grid_figure


@task
def plot_volume_average(
    keys: list[str],
    data: dict[str, pd.DataFrame],
    reference: Optional[pd.DataFrame] = None,
    region: Optional[str] = None,
) -> mpl.Figure:
    fig, gridspec, indices = make_grid_figure(keys)
    value = f"volume.{region}" if region else "volume"

    for i, j, key in indices:
        ax = fig.add_subplot(gridspec[i, j])
        ax.set_title(key)
        ax.set_xlabel("Time (hrs)")
        ax.set_ylabel("Average volume ($\\mu m^3$)")

        volume = data[key].groupby(["SEED", "time"])[value].mean()
        mean = volume.groupby(["time"]).mean()
        std = volume.groupby(["time"]).std()
        time = mean.index

        if reference is not None:
            ref_volume_mean = reference[value].mean()
            ref_volume_std = reference[value].std()
            ref_label = f"reference ({ref_volume_mean:.1f} $\\pm$ {ref_volume_std:.1f} $\\mu m^3$)"
            ax.plot(time, [reference[value].mean()] * len(time), c="#555", lw=0.5, label=ref_label)

        label = f"simulated ({mean.mean():.1f} $\\pm$ {std.mean():.1f} $\\mu m^3$)"
        ax.plot(time, mean, c="#000", label=label)
        ax.fill_between(time, mean - std, mean + std, facecolor="#bbb")

        ax.legend()

    return fig
