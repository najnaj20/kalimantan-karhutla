"""Streamlit dashboard: Karhutla Kalimantan — hotspot analysis (NASA FIRMS)."""
from __future__ import annotations

from pathlib import Path

import folium
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"
BOUNDARIES = ROOT / "data" / "boundaries" / "idn_adm1.geojson"

st.set_page_config(page_title="Karhutla Kalimantan", layout="wide")

PROV_WARNA = {
    "West Kalimantan": "#d62728",
    "Central Kalimantan": "#ff7f0e",
    "South Kalimantan": "#2ca02c",
    "East Kalimantan": "#1f77b4",
    "North Kalimantan": "#9467bd",
}


@st.cache_data(show_spinner=False)
def load_data() -> tuple[pd.DataFrame, dict]:
    df = pd.read_csv(PROC / "kalimantan_hotspots.csv", parse_dates=["acq_date"])
    gjson = __import__("json").loads(BOUNDARIES.read_text())
    return df, gjson


@st.cache_data(show_spinner=False)
def load_aggs() -> dict[str, pd.DataFrame]:
    return {
        "daily": pd.read_csv(PROC / "agg_daily.csv"),
        "province": pd.read_csv(PROC / "agg_province.csv"),
        "province_daily": pd.read_csv(PROC / "agg_province_daily.csv", index_col=0),
        "bands": pd.read_csv(PROC / "agg_bands.csv"),
        "daynight": pd.read_csv(PROC / "agg_daynight.csv"),
        "top3_daily": pd.read_csv(PROC / "agg_top3_daily.csv", parse_dates=["tanggal"]),
    }


df, gjson = load_data()
aggs = load_aggs()

# ---------- header ----------
total = len(df)
days = df["acq_date"].dt.date.nunique()
worst = aggs["province"].iloc[0]
peak = aggs["daily"].loc[aggs["daily"]["hotspot"].idxmax()]

st.title("🔥 Karhutla Kalimantan — Analisis Hotspot (NASA FIRMS)")
st.caption(
    f"Data: NASA FIRMS VIIRS 375m + MODIS C6.1 · {df['acq_date'].min():%d %b %Y} – {df['acq_date'].max():%d %b %Y} · lisensi CC BY"
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Hotspot (7 hari)", f"{total:,}")
c2.metric("Hari Cakupan", f"{days} hari")
c3.metric("Provinsi Terparah", worst["provinsi"], f"{int(worst['hotspot']):,} titik")
c4.metric("Puncak Harian", f"{peak['tanggal']}", f"{int(peak['hotspot']):,} titik")

st.divider()

# ---------- map + side panel ----------
col_map, col_side = st.columns([3, 2], gap="large")

with col_map:
    st.subheader("🗺️ Peta Hotspot")
    tanggal_opsi = sorted(df["acq_date"].dt.date.unique())
    pilih = st.select_slider("Filter tanggal", tanggal_opsi, value=tanggal_opsi[-1])
    subset = df[df["acq_date"].dt.date == pilih]

    m = folium.Map(location=[-1.5, 114.5], zoom_start=6, tiles="CartoDB positron")

    folium.GeoJson(
        gjson,
        name="provinsi",
        style_function=lambda f: {
            "fillColor": PROV_WARNA.get(f["properties"].get("shapeName"), "#cccccc"),
            "color": "#444444",
            "weight": 1.2,
            "fillOpacity": 0.08,
        },
        tooltip=folium.GeoJsonTooltip(fields=["shapeName"], aliases=["Provinsi"]),
    ).add_to(m)

    if len(subset):
        cmap = folium.LinearColormap(
            ["#2ecc71", "#f1c40f", "#e67e22", "#e74c3c"], vmin=0, vmax=300
        )
        for _, row in subset.iterrows():
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=2.2,
                color=None,
                fill=True,
                fill_color=cmap(min(row["frp"], 300)),
                fill_opacity=0.65,
                popup=(
                    f"FRP: {row['frp']:.0f} MW<br>{row['provinsi']}<br>"
                    f"{row['acq_datetime']}"
                ),
            ).add_to(m)
        cmap.add_to(m)
        cmap.caption = "FRP (MW)"
    else:
        st.info("Tidak ada hotspot pada tanggal ini.")

    st_folium(m, width="100%", height=520)

with col_side:
    st.subheader("📊 Ringkasan Provinsi (7 hari)")
    prov = aggs["province"].copy()
    prov["persen"] = (prov["hotspot"] / prov["hotspot"].sum() * 100).round(1)
    prov_disp = prov.rename(
        columns={
            "provinsi": "Provinsi",
            "hotspot": "Hotspot",
            "frp_mean": "FRP rata-rata",
            "frp_max": "FRP max",
            "persen": "Porsi %",
        }
    )
    prov_disp["FRP rata-rata"] = prov_disp["FRP rata-rata"].round(1)
    prov_disp["FRP max"] = prov_disp["FRP max"].round(1)
    st.dataframe(prov_disp, hide_index=True, width="stretch")

    st.subheader("🔥 Intensitas (FRP)")
    bands = aggs["bands"]
    fig_b = px.bar(
        bands,
        x="frp_band",
        y="count",
        color="frp_band",
        color_discrete_map={
            "Rendah": "#2ecc71",
            "Sedang": "#f1c40f",
            "Tinggi": "#e67e22",
            "Ekstrem": "#e74c3c",
        },
        labels={"frp_band": "Kelas Intensitas", "count": "Jumlah Hotspot"},
    )
    fig_b.update_layout(height=260, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_b, width="stretch")

st.divider()

# ---------- trend charts ----------
st.subheader("📈 Tren Hotspot")
t1, t2 = st.columns(2)

with t1:
    daily = aggs["daily"]
    daily["tanggal"] = pd.to_datetime(daily["tanggal"])
    fig_d = px.line(
        daily,
        x="tanggal",
        y="hotspot",
        markers=True,
        labels={"tanggal": "Tanggal", "hotspot": "Jumlah Hotspot"},
        title="Hotspot per Hari (semua sensor)",
    )
    fig_d.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_d, width="stretch")

with t2:
    top3 = aggs["top3_daily"]
    fig_t = px.line(
        top3,
        x="tanggal",
        y="hotspot",
        color="provinsi",
        markers=True,
        color_discrete_map=PROV_WARNA,
        labels={"tanggal": "Tanggal", "hotspot": "Jumlah Hotspot", "provinsi": "Provinsi"},
        title="Top 3 Provinsi per Hari",
    )
    fig_t.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_t, width="stretch")

st.divider()

# ---------- heatmap + footer ----------
st.subheader("🗓️ Heatmap Provinsi × Hari")
fig_h = px.imshow(
    aggs["province_daily"].astype(int),
    labels=dict(x="Tanggal", y="Provinsi", color="Hotspot"),
    aspect="auto",
    color_continuous_scale="YlOrRd",
    text_auto=True,
)
fig_h.update_layout(height=380, margin=dict(l=10, r=10, t=30, b=10))
st.plotly_chart(fig_h, width="stretch")

st.caption(
    "Sumber: NASA FIRMS (VIIRS 375m & MODIS C6.1) via Humanitarian Data Exchange (HDX), "
    "CC BY. Batas admin: geoBoundaries / HDX COD. "
    "Proyek portofolio — bukan alat peringatan dini resmi."
)
