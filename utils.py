from datetime import date, timedelta

import polars as pl
import plotly.graph_objects as go


def end_of_previous_quarter(for_date=None):
    for_date = for_date or date.today()
    q_start_month = (for_date.month - 1) // 3 * 3 + 1
    q_start = for_date.replace(month=q_start_month, day=1)
    return q_start - timedelta(days=1)


def load_data(until):
    url = (
        "https://get.data.gov.lt/datasets/gov/lrsk/teises_aktai/Dokumentas/:format/csv?"
    )
    url += f"priemusi_inst='Lietuvos%20Respublikos%20Seimas'&registracija>='2014-01-01'&isigalioja<='{until}'&rusis='%C4%AEstatymas'"
    url += "&select(galioj_busena,tar_kodas,registracija,isigalioja,isigalioja_po_salygu,negalioja,negalioja_po_salygu)"

    return pl.read_csv(url)


def load_and_preprocess_data(until):
    df = load_data(until)
    df = (
        df.filter(pl.col("isigalioja") >= "2014-01-01")
        .with_columns(
            pl.coalesce(pl.col("isigalioja"), pl.col("isigalioja_po_salygu"))
            .str.strptime(pl.Date, "%Y-%m-%d", strict=False)
            .alias("isigalioja"),
            pl.coalesce(pl.col("negalioja"), pl.col("negalioja_po_salygu"))
            .str.strptime(pl.Date, "%Y-%m-%d", strict=False)
            .alias("negalioja"),
        )
        .drop("isigalioja_po_salygu", "negalioja_po_salygu")
        .with_columns(
            pl.col("isigalioja").dt.quarter().alias("isigalioja_quarter"),
            pl.col("isigalioja").dt.year().alias("isigalioja_year"),
            pl.col("negalioja").dt.quarter().alias("negalioja_quarter"),
            pl.col("negalioja").dt.year().alias("negalioja_year"),
        )
        .with_columns(
            (
                pl.col("isigalioja_year").cast(pl.Utf8)
                + "-Q"
                + pl.col("isigalioja_quarter").cast(pl.Utf8)
            ).alias("isigalioja_quarter"),
            (
                pl.col("negalioja_year").cast(pl.Utf8)
                + "-Q"
                + pl.col("negalioja_quarter").cast(pl.Utf8)
            ).alias("negalioja_quarter"),
        )
    )

    return df


def aggregate_by_period(df, period):
    df_isigalioja = df.group_by(pl.col(f"isigalioja_{period}").alias("period")).len()
    df_negalioja = df.group_by(pl.col(f"negalioja_{period}").alias("period")).len()

    return (
        df_isigalioja.join(df_negalioja, on="period", how="left")
        .rename({"len": "isigalioja_count", "len_right": "negalioja_count"})
        .fill_null(0)
        .sort("period")
    )
