from datetime import date

import plotly.graph_objects as go
import polars as pl
import streamlit as st

from utils import aggregate_by_period, load_and_preprocess_data
from plots import plot_yearly, plot_quarterly, plot_yearly_cumulative

st.set_page_config(layout="wide", page_title="Teisėkūra", page_icon="📄")

st.title("Teisėkūra Lietuvos Respublikos Seime")


@st.cache_data(ttl="24h")
def load_data_cached(until):
    return load_and_preprocess_data(until)


until = date.today().strftime("%Y-%m-%d")
df = load_data_cached(until)

###
# Summary
###
summary_cols = st.columns([6, 3, 3])

with summary_cols[0]:
    st.markdown(
        """
        Šios vizualizacijos imtis - visi nuo 2014 metų Lietuvos Respublikos Seime įregistruoti ir kada nors galioję įstatymai.
        Domenų šaltinis - [teisės aktų registro atviri duomenys](https://data.gov.lt/datasets/2613/).
            """
    )

with summary_cols[1]:
    st.metric(
        label=f"Nuo 2014 m. išleistų ir tebegaliojančių įstatymų skaičius",
        value=df.filter(pl.col("galioj_busena") == "galioja").shape[0],
    )

with summary_cols[2]:
    st.metric(
        label=f"Nuo 2014 m. išleistų ir nustojusių galioti įstatymų skaičius",
        value=df.filter(pl.col("galioj_busena") == "negalioja").shape[0],
    )


st.divider()

###
# Yearly plots
###
df_excl_this_year = df.filter(pl.col("isigalioja_year") != date.today().year)
df_yearly = aggregate_by_period(df_excl_this_year, "year")
prev_year = df_yearly[-1]
isigalioja_mean = df_yearly["isigalioja_count"].mean()
negalioja_mean = df_yearly["negalioja_count"].mean()

yearly_plot_cols = st.columns([2, 5, 5])

with yearly_plot_cols[0]:
    st.markdown(
        """
        ### Tendencija pagal metus
    """
    )

    st.metric(
        label=f"Praėjusiais metais įsigaliojusių įstatymų skaičius",
        value=prev_year["isigalioja_count"],
    )

    st.metric(
        label=f"Praėjusiais metais nustojusių galioti įstatymų skaičius",
        value=prev_year["negalioja_count"],
    )

with yearly_plot_cols[1]:
    fig, means = plot_yearly(df_yearly)
    st.plotly_chart(fig)

with yearly_plot_cols[2]:
    fig = plot_yearly_cumulative(
        df_yearly, "galioja_count", "Galiojančių įstatymų skaičius"
    )
    st.plotly_chart(fig)


st.divider()

## Quarterly plots
df_quarterly = aggregate_by_period(df, "quarter")
prev_quarter = df_quarterly[-2]

quarterly_plot_cols = st.columns([2, 10])

with quarterly_plot_cols[0]:
    st.markdown(
        """
    ### Tendencija pagal ketvirtį
    """
    )

    st.metric(
        label=f"Praeitą ketvirtį įsigaliojusių įstatymų skaičius",
        value=prev_quarter["isigalioja_count"],
    )

    st.metric(
        label=f"Praeitą ketvirtį nustojusių galioti įstatymų skaičius",
        value=prev_quarter["negalioja_count"],
    )

with quarterly_plot_cols[1]:
    fig = plot_quarterly(df_quarterly)
    st.plotly_chart(fig)
