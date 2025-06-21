from pathlib import Path

import pandas as pd
import plotly.express as px


def _fig(csvs, df, row_name):
    """Helps make plotly graphs for duration and memory performance."""

    fig = px.bar(
        df,
        title=row_name,
        x=row_name,
        y="test",
        color="success_rate",
        color_continuous_midpoint=0.5,  # forces bar to show 0 to 1.
        color_continuous_scale=["red", "green"],
        orientation="h",
        hover_data=list(df.columns.values),
        height=25 * len(df),
    )

    fig.add_vline(
        df[row_name].mean(),
        line_dash="dash",
        annotation_text="mean",
        annotation_position="top right",
        annotation_font_style="italic",
        annotation_bgcolor="white",
    )

    # sort bar.
    fig.update_layout(yaxis={"categoryorder": "total ascending"})

    return fig


def _csvs_and_df():
    """Returns CSV paths and a Pandas dataframe of aggregated tests."""

    test_location = Path(__file__).parent.parent.joinpath("results")
    csvs = list(test_location.rglob("*.csv"))
    assert csvs, "No CSVs to aggregate."

    dfs = [pd.read_csv(f) for f in csvs]
    df = pd.concat(dfs)
    df = df.groupby(["test"], as_index=False).agg(
        average_duration=("duration", "mean"),
        average_memory=("memory", "mean"),
        success_rate=(
            "success",
            lambda series: sum(1 for i in series if i) / len(series),
        ),
    )

    # add z_score columns for duration and memory.
    d_mean, d_std = df["average_duration"].mean(), df["average_duration"].std()
    df["z_duration"] = [(d - d_mean) / d_std for d in df["average_duration"]]

    m_mean, m_std = df["average_memory"].mean(), df["average_memory"].std()
    df["z_memory"] = [(m - m_mean) / m_std for m in df["average_memory"]]

    return csvs, df


def aggregate():
    """Prints a CSV string of aggregated test data."""

    _, df = _csvs_and_df()
    return df.to_csv(index=False)


def correlate():
    """Prints a CSV string of Pearson-correlated test data."""

    _, df = _csvs_and_df()
    return df.corr(numeric_only=True).to_csv()


def graph():
    """Creates graphs of aggregated test results."""

    csvs, df = _csvs_and_df()

    # bar charts for average duration and memory.
    _fig(csvs, df, "average_duration").show()
    _fig(csvs, df, "average_memory").show()

    # scatter graph for z-scores.
    fig = px.scatter(
        df,
        x="z_duration",
        y="z_memory",
        color="success_rate",
        color_continuous_midpoint=0.5,
        color_continuous_scale=["red", "green"],
        hover_data=list(df.columns.values),
    )
    fig.show()

    return
