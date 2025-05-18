import plotly.graph_objects as go
import polars as pl
import streamlit as st

from utils import end_of_previous_quarter

st.set_page_config(layout="wide", page_title="Teisėkūra", page_icon="📄")

st.title("Teisėkūra Lietuvos Respublikos Seime")

st.markdown(
    """
    Ši vizualizacija apima visus nuo 2014 metų Lietuvos Respublikos Seimo priimtus ir kada nors galiojusius įstatymus.
    Domenų šaltinis - [teisės aktų registro atviri duomenys](https://data.gov.lt/datasets/2613/).
    """
)


@st.cache_data(ttl="24h")
def load_data(until):
    url = (
        "https://get.data.gov.lt/datasets/gov/lrsk/teises_aktai/Dokumentas/:format/csv?"
    )
    url += f"priemusi_inst='Lietuvos%20Respublikos%20Seimas'&registracija>='2014-01-01'&isigalioja<='{until}'&rusis='%C4%AEstatymas'"
    url += "&select(galioj_busena,tar_kodas,registracija,isigalioja,isigalioja_po_salygu,negalioja,negalioja_po_salygu)"

    return pl.read_csv(url)


until = end_of_previous_quarter().strftime("%Y-%m-%d")
df = load_data(until)

df = (
    df
    .with_columns(
        pl.coalesce(pl.col("isigalioja"), pl.col("isigalioja_po_salygu"))
        .str.strptime(pl.Date, "%Y-%m-%d", strict=False)
        .alias("isigalioja"),
        pl.coalesce(pl.col("negalioja"), pl.col("negalioja_po_salygu"))
        .str.strptime(pl.Date, "%Y-%m-%d", strict=False)
        .alias("negalioja"),
    ).drop("isigalioja_po_salygu", "negalioja_po_salygu")
    .with_columns(
        pl.col("isigalioja").dt.quarter().alias("isigalioja_ketvirtis"),
        pl.col("isigalioja").dt.year().alias("isigalioja_metai"),
        pl.col("negalioja").dt.quarter().alias("negalioja_ketvirtis"),
        pl.col("negalioja").dt.year().alias("negalioja_metai"),
    )
    .with_columns(
        (
            pl.col("isigalioja_metai").cast(pl.Utf8)
            + "-Q"
            + pl.col("isigalioja_ketvirtis").cast(pl.Utf8)
        ).alias("isigalioja_metai_ketvirtis"),
        (
            pl.col("negalioja_metai").cast(pl.Utf8)
            + "-Q"
            + pl.col("negalioja_ketvirtis").cast(pl.Utf8)
        ).alias("negalioja_metai_ketvirtis"),
    )
)


df_isigalioja = df.group_by(
    pl.col("isigalioja_metai_ketvirtis").alias("ketvirtis")
).len()
df_negalioja = df.group_by(pl.col("negalioja_metai_ketvirtis").alias("ketvirtis")).len()

df_quarterly = (
    df_isigalioja.join(df_negalioja, on="ketvirtis", how="left")
    .rename({"len": "isigalioja_count", "len_right": "negalioja_count"})
    .fill_null(0)
    .sort("ketvirtis")
)

prev_quarter = df_quarterly[-1]

st.divider()

col1, col2, col3 = st.columns([3, 3, 6])
with col1:
    st.metric(
        label=f"{prev_quarter['ketvirtis'].item()} įsigaliojusių įstatymų skaičius",
        value=prev_quarter["isigalioja_count"],
    )

with col2:
    st.metric(
        label=f"{prev_quarter['ketvirtis'].item()} nustojusių galioti įstatymų skaičius",
        value=prev_quarter["negalioja_count"],
    )

with col3:
    st.metric(
        label=f"Nuo 2014 m. išleistų ir tebegaliojančių įstatymų skaičius",
        value=df.filter(pl.col("galioj_busena") == "galioja").shape[0],
    )


y_max = (
    df_quarterly.select(
        pl.max_horizontal(
            [pl.col("isigalioja_count"), pl.col("negalioja_count")]
        ).alias("max_count")
    )
    .max()
    .item()
)
y_max += 10

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_quarterly["ketvirtis"].to_list(),
        y=df_quarterly["isigalioja_count"].to_list(),
        mode="lines+markers",
        name="Įsigaliojusių įstatymų skaičius",
        line=dict(width=3),
    )
)

fig.add_trace(
    go.Scatter(
        x=df_quarterly["ketvirtis"].to_list(),
        y=df_quarterly["negalioja_count"].to_list(),
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
        showgrid=False,
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

st.plotly_chart(fig)
