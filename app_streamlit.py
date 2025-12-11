from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATA_PATH = Path(__file__).parent / "data" / "btcusd_1-min_data.csv"

RESAMPLE_LABELS = {
    "1 minute": "1min",
    "5 minutes": "5min",
    "15 minutes": "15min",
    "1 heure": "1H",
    "4 heures": "4H",
    "1 jour": "1D",
}


def load_data() -> pd.DataFrame | None:
    """Load the expected dataset."""

    if not DATA_PATH.exists():
        return None

    dtypes = {
        "Timestamp": "float64",
        "Open": "float32",
        "High": "float32",
        "Low": "float32",
        "Close": "float32",
        "Volume": "float32",
    }

    df = pd.read_csv(
        DATA_PATH,
        usecols=list(dtypes.keys()),
        dtype=dtypes,
    )
    df["Date"] = pd.to_datetime(df["Timestamp"], unit="s", errors="coerce")
    df = df.dropna(subset=["Date"]).sort_values("Date").set_index("Date")
    return df


@st.cache_data(show_spinner=False)
def get_data() -> pd.DataFrame | None:
    return load_data()


def resample_data(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    """Aggregate the minute data to the requested frequency."""

    if rule == "1min":
        return df

    agg = {
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum",
    }
    grouped = df.resample(rule).agg(agg).dropna(how="all")
    return grouped.dropna(subset=["Close"])


def plot_price(df: pd.DataFrame) -> None:
    """Render the interactive price curve."""

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Close"],
            mode="lines",
            line=dict(color="#1f77b4", width=1.5),
            name="Clôture",
        )
    )
    fig.update_layout(
        title="BTC-USD — courbe de prix",
        xaxis_title="Date",
        yaxis_title="Prix (USD)",
        hovermode="x unified",
        height=420,
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_price_volume(df: pd.DataFrame) -> None:
    """Render a combined price/volume view with shared filters."""

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Close"],
            mode="lines",
            name="Clôture",
            line=dict(color="#0d6efd", width=1.8),
            yaxis="y1",
        )
    )
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["Volume"],
            name="Volume",
            marker_color="#adb5bd",
            opacity=0.55,
            yaxis="y2",
        )
    )
    fig.update_layout(
        title="Prix et volume agrégés",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Prix (USD)", side="left"),
        yaxis2=dict(
            title="Volume (BTC)",
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        bargap=0,
        height=460,
    )
    st.plotly_chart(fig, use_container_width=True)


def show_metrics(df: pd.DataFrame) -> None:
    """Display simple summary metrics for the current selection."""

    latest_close = df["Close"].iloc[-1]
    change = df["Close"].pct_change().iloc[-1]
    change_pct = 0.0 if pd.isna(change) else change * 100
    daily_vol = df["Volume"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Clôture la plus récente", f"${latest_close:,.2f}", f"{change_pct:+.2f}% vs précéd.")
    col2.metric("Clôture min / max", f"${df['Close'].min():,.2f} / ${df['Close'].max():,.2f}")
    col3.metric("Volume total", f"{daily_vol:,.0f} BTC")


def main() -> None:
    st.set_page_config(page_title="Mini-projet Bitcoin", layout="wide")
    st.title("📈 Dashboard Bitcoin - Mini-projet 8PRO408")
    st.caption("Courbe de prix interactive et vue prix/volume avec filtres temporels.")

    df = get_data()
    if df is None:
        st.error(
            "Le fichier `btcusd_1-min_data.csv` est introuvable dans le dossier `data/`. "
            "Placez-le depuis Kaggle puis relancez l'application."
        )
        st.stop()

    min_date = df.index.min().date()
    max_date = df.index.max().date()

    st.sidebar.header("Filtres temporels")
    start_date = st.sidebar.date_input("Date de début", min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("Date de fin", max_date, min_value=min_date, max_value=max_date)

    if start_date > end_date:
        st.warning("La date de début dépasse la date de fin.")
        st.stop()

    rule_label = st.sidebar.selectbox("Granularité", list(RESAMPLE_LABELS.keys()), index=4)
    rule = RESAMPLE_LABELS[rule_label]

    filtered = df.loc[str(start_date): str(end_date)]
    if filtered.empty:
        st.warning("Aucune donnée sur cette période.")
        st.stop()

    sampled = resample_data(filtered, rule)
    if sampled.empty:
        st.warning("La granularité choisie ne contient pas de points pour cette période.")
        st.stop()

    st.header("Courbe de prix")
    plot_price(sampled)
    show_metrics(sampled)

    st.header("Prix et volume")
    st.caption("Les volumes sont agrégés selon la même granularité que la courbe de prix.")
    plot_price_volume(sampled)

    with st.expander("Statistiques descriptives"):
        stats = sampled[["Open", "High", "Low", "Close", "Volume"]].describe().T
        st.dataframe(stats, use_container_width=True)

    st.markdown("---")
    st.caption("Projet Bitcoin — Streamlit 8PRO408")


if __name__ == "__main__":
    main()
