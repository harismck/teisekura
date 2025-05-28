import plotly.graph_objects as go

def plot_yearly(df, column, series_title, color="blue"):
    y_max = df[column].max() + 10
    mean = df[column].mean()
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["period"].to_list(),
            y=df[column].to_list(),
            mode="lines+markers",
            line=dict(width=3, color=color),
            name=series_title,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["period"].to_list(),
            y=[mean] * len(df["period"]),
            mode="lines",
            line=dict(width=2, dash="dash", color="gray"),
            name="Vidurkis",
        )
    )
    fig.update_layout(
        xaxis_title="Metai",
        width=650,
        height=600,
        xaxis=dict(tickfont=dict(size=14)),
        yaxis=dict(tickfont=dict(size=14), range=[0, y_max]),
        showlegend=True,
        legend=dict(
            x=1,
            y=1,
            xanchor="right",
            yanchor="top",
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,0,0,0)",
            font=dict(size=16),
        ),
    )
    return fig, mean


def plot_quarterly(df):
    y_max = max(
        df["isigalioja_count"].max(), df["negalioja_count"].max()
    )
    y_max += 10

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["period"].to_list(),
            y=df["isigalioja_count"].to_list(),
            mode="lines+markers",
            name="Įsigaliojusių įstatymų skaičius",
            line=dict(width=3),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["period"].to_list(),
            y=df["negalioja_count"].to_list(),
            mode="lines+markers",
            name="Nustojusių galioti įstatymų skaičius",
            line=dict(width=3, color="red"),
        )
    )

    fig.update_layout(
        xaxis_title="Ketvirtis",
        yaxis=dict(
            title="Įstatymų Skaičius",
            side="left",
            range=[0, y_max],
            tickfont=dict(size=16),
        ),
        xaxis=dict(showgrid=False, tickangle=45, tickfont=dict(size=16)),
        width=1400,
        height=600,
        legend=dict(
            x=1,
            y=1,
            xanchor="right",
            yanchor="top",
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,0,0,0)",
            font=dict(size=16),
        ),
    )
    return fig
