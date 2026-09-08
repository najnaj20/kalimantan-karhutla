"""Streamlit dashboard: Karhutla Kalimantan — hotspot analysis (NASA FIRMS).

Bilingual (ID/EN) with village/district search via OSM Nominatim.
"""
from __future__ import annotations
from math import asin, cos, radians, sin, sqrt
from pathlib import Path

import folium
import pandas as pd
import plotly.express as px
import plotly.io as pio
import requests
import streamlit as st
from streamlit_folium import st_folium

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"
BOUNDARIES = ROOT / "data" / "boundaries" / "idn_adm1.geojson"

st.set_page_config(page_title="Karhutla Kalimantan", layout="wide")

# ---------- dark theme ----------
pio.templates.default = "plotly_dark"

st.markdown("""
<style>
    /* === Global dark theme === */
    .stApp, .stSidebar, .st-emotion-cache-1y4p8pa, .st-emotion-cache-6qob1r {
        background-color: #0d1117 !important;
        color: #c9d1d9;
    }
    .stSidebar, .st-emotion-cache-1wrcr25 {
        background-color: #161b22 !important;
    }
    /* Metric cards */
    .stMetric {
        background: linear-gradient(135deg, #1c2128 0%, #161b22 100%);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .stMetric label, .stMetric [data-testid="stMetricLabel"] {
        color: #8b949e !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.5px;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #f0f6fc !important;
        font-size: 2rem !important;
        font-weight: 700;
    }
    .stMetric [data-testid="stMetricDelta"] {
        color: #e67e22 !important;
    }
    /* Metric cards hover */
    .stMetric:hover {
        border-color: #e67e22;
        box-shadow: 0 0 20px rgba(230, 126, 34, 0.15);
        transition: all 0.3s ease;
    }
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #f0f6fc !important;
    }
    h1 {
        background: linear-gradient(135deg, #f0f6fc, #e67e22);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    /* Subheader accent */
    h3 {
        border-left: 3px solid #e67e22;
        padding-left: 12px;
    }
    /* Dataframe */
    .stDataFrame, [data-testid="stDataFrame"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d;
        border-radius: 8px;
    }
    .stDataFrame table {
        background-color: #161b22 !important;
        color: #c9d1d9 !important;
    }
    .stDataFrame th {
        background-color: #1c2128 !important;
        color: #e67e22 !important;
        font-weight: 600;
    }
    .stDataFrame td {
        color: #c9d1d9 !important;
    }
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #e67e22, #d35400) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(230, 126, 34, 0.3);
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #f39c12, #e67e22) !important;
        box-shadow: 0 4px 16px rgba(230, 126, 34, 0.5);
    }
    /* Slider */
    .stSlider [data-baseweb="slider"] {
        background-color: #30363d !important;
    }
    .stSlider [data-baseweb="slider"] [role="slider"] {
        background-color: #e67e22 !important;
    }
    /* Select slider (date filter) */
    .stSelectSlider [data-baseweb="slider"] {
        background-color: #30363d !important;
    }
    /* Text input */
    .stTextInput input {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        color: #c9d1d9 !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus {
        border-color: #e67e22 !important;
        box-shadow: 0 0 0 2px rgba(230, 126, 34, 0.3);
    }
    /* Divider */
    hr {
        border-color: #30363d !important;
    }
    /* Caption / footer */
    .stCaption, .st-emotion-cache-1aehpvj, .st-emotion-cache-16idsys {
        color: #8b949e !important;
    }
    /* Success / info boxes */
    .stAlert {
        background-color: #1c2128 !important;
        border: 1px solid #30363d !important;
        color: #c9d1d9 !important;
    }
    .stAlert [data-testid="stAlert"] {
        background-color: #1c2128 !important;
    }
    /* Radio */
    .stRadio label {
        color: #c9d1d9 !important;
    }
    .stRadio [data-testid="stWidgetLabel"] {
        color: #8b949e !important;
    }
    /* Sidebar text */
    .stSidebar .st-emotion-cache-1aehpvj {
        color: #8b949e !important;
    }
    /* Metric delta icon colors */
    .st-emotion-cache-1wivap2 {
        color: #e67e22 !important;
    }
    /* Hero metric grid polish */
    .stMetric > div {
        gap: 2px;
    }
    /* Tab list styling (period selector) */
    .stTabs [role="tablist"] button {
        background: #161b22 !important;
        border: 1px solid #30363d !important;
        color: #8b949e !important;
        border-radius: 8px !important;
        margin-right: 6px !important;
        font-size: 0.8rem !important;
    }
    .stTabs [role="tablist"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #e67e22, #d35400) !important;
        color: #fff !important;
        border-color: #e67e22 !important;
    }
    /* Section divider glow */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, #30363d, transparent) !important;
    }
    /* Insight callout box */
    .insight-box {
        background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
        border: 1px solid #30363d;
        border-left: 4px solid #e67e22;
        border-radius: 10px;
        padding: 14px 18px;
        margin: 10px 0;
    }
    .insight-box .title {
        color: #e67e22;
        font-weight: 700;
        font-size: 0.8rem;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .insight-box .body {
        color: #c9d1d9;
        font-size: 0.88rem;
        margin-top: 4px;
        line-height: 1.5;
    }
    /* scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0d1117;
    }
    ::-webkit-scrollbar-thumb {
        background: #30363d;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #484f58;
    }
</style>
""", unsafe_allow_html=True)

# ---------- i18n strings ----------
TEXT = {
    "sidebar_title": {"id": "Bahasa", "en": "Language"},
    "lang_labels": {"id": "Indonesian", "en": "English"},
    "caption_data": {
        "id": "Data: NASA FIRMS VIIRS 375m + MODIS C6.1 · {min} – {max} · lisensi CC BY",
        "en": "Data: NASA FIRMS VIIRS 375m + MODIS C6.1 · {min} – {max} · CC BY",
    },
    "metric_total": {"id": "Total Hotspot (7 hari)", "en": "Total Hotspots (7 days)"},
    "metric_days": {"id": "Hari Cakupan", "en": "Days Covered"},
    "metric_days_val": {"id": "{n} hari", "en": "{n} days"},
    "metric_worst": {"id": "Provinsi Terparah", "en": "Worst Province"},
    "metric_worst_val": {"id": "{n:,} titik", "en": "{n:,} points"},
    "metric_peak": {"id": "Puncak Harian", "en": "Daily Peak"},
    "map_title": {"id": "🗺️ Peta Hotspot", "en": "🗺️ Hotspot Map"},
    "map_filter": {"id": "Filter tanggal", "en": "Filter date"},
    "map_empty": {"id": "Tidak ada hotspot pada tanggal ini.", "en": "No hotspots on this date."},
    "map_tooltip": {"id": "Provinsi", "en": "Province"},
    "map_popup_frp": {"id": "FRP", "en": "FRP"},
    "search_label": {"id": "🔍 Cari desa / kecamatan", "en": "🔍 Search village / district"},
    "search_placeholder": {"id": "Contoh: Pangkalan Bun, Sampit...", "en": "E.g.: Pangkalan Bun, Sampit..."},
    "search_btn": {"id": "Cari", "en": "Search"},
    "search_radius": {"id": "Radius pencarian", "en": "Search radius"},
    "search_km": {"id": "{n} km", "en": "{n} km"},
    "search_result": {
        "id": "📍 **{n} hotspot** dalam radius **{r} km** dari **{place}**",
        "en": "📍 **{n} hotspot(s)** within **{r} km** of **{place}**",
    },
    "search_none": {
        "id": "Tidak ada hotspot dalam radius {r} km dari lokasi tersebut. Coba perbesar radius.",
        "en": "No hotspots within {r} km of that location. Try increasing the radius.",
    },
    "search_notfound": {
        "id": "Lokasi '{q}' tidak ditemukan. Coba nama desa atau kecamatan lain.",
        "en": "Location '{q}' not found. Try a different village or district name.",
    },
    "search_error": {
        "id": "Gagal mencari lokasi. Coba lagi nanti.",
        "en": "Failed to search location. Please try again later.",
    },
    "clear_btn": {"id": "✕ Hapus pencarian", "en": "✕ Clear search"},
    "side_table_title": {"id": "📊 Ringkasan Provinsi", "en": "📊 Province Summary"},
    "side_table_subtitle": {"id": "({n} hari, hasil pencarian)", "en": "({n} days, search results)"},
    "col_province": {"id": "Provinsi", "en": "Province"},
    "col_hotspot": {"id": "Hotspot", "en": "Hotspots"},
    "col_frp_mean": {"id": "FRP rata-rata", "en": "Avg FRP"},
    "col_frp_max": {"id": "FRP max", "en": "Max FRP"},
    "col_pct": {"id": "Porsi %", "en": "Share %"},
    "band_title": {"id": "🔥 Intensitas (FRP)", "en": "🔥 Intensity (FRP)"},
    "band_x": {"id": "Kelas Intensitas", "en": "Intensity Class"},
    "band_y": {"id": "Jumlah Hotspot", "en": "Hotspot Count"},
    "trend_title": {"id": "📈 Tren Hotspot", "en": "📈 Hotspot Trend"},
    "trend_daily": {"id": "Hotspot per Hari (semua sensor)", "en": "Hotspots per Day (all sensors)"},
    "trend_top3": {"id": "Top 3 Provinsi per Hari", "en": "Top 3 Provinces per Day"},
    "x_date": {"id": "Tanggal", "en": "Date"},
    "y_hotspot": {"id": "Jumlah Hotspot", "en": "Hotspot Count"},
    "heat_title": {"id": "🗓️ Heatmap Provinsi × Hari", "en": "🗓️ Province × Day Heatmap"},
    "heat_x": {"id": "Tanggal", "en": "Date"},
    "heat_y": {"id": "Provinsi", "en": "Province"},
    "heat_c": {"id": "Hotspot", "en": "Hotspots"},
    "footer": {
        "id": "Sumber: NASA FIRMS (VIIRS 375m & MODIS C6.1) via Humanitarian Data Exchange (HDX), "
        "CC BY. Batas admin: geoBoundaries / HDX COD. Pencarian desa: OpenStreetMap Nominatim. "
        "Proyek portofolio — bukan alat peringatan dini resmi.",
        "en": "Source: NASA FIRMS (VIIRS 375m & MODIS C6.1) via Humanitarian Data Exchange (HDX), "
        "CC BY. Admin boundaries: geoBoundaries / HDX COD. Village search: OpenStreetMap Nominatim. "
        "Portfolio project — not an official early-warning system.",
    },
}

# province english name → localized
PROV_EN = {
    "West Kalimantan": "Kalimantan Barat",
    "Central Kalimantan": "Kalimantan Tengah",
    "East Kalimantan": "Kalimantan Timur",
    "South Kalimantan": "Kalimantan Selatan",
    "North Kalimantan": "Kalimantan Utara",
}

BAND_EN = {"Rendah": "Low", "Sedang": "Medium", "Tinggi": "High", "Ekstrem": "Extreme"}
BAND_COLOR = {
    "Rendah": "#2ecc71",
    "Sedang": "#f1c40f",
    "Tinggi": "#e67e22",
    "Ekstrem": "#e74c3c",
}

PROV_WARNA = {
    "West Kalimantan": "#d62728",
    "Central Kalimantan": "#ff7f0e",
    "South Kalimantan": "#2ca02c",
    "East Kalimantan": "#1f77b4",
    "North Kalimantan": "#9467bd",
}


# ---------- helpers ----------
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine distance in km between two (lat,lon) pairs."""
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * asin(sqrt(a))


def T(key: str) -> str:
    return TEXT[key][lang]


def loc_prov(name: str) -> str:
    return PROV_EN.get(name, name) if lang == "id" else name


def loc_band(name: str) -> str:
    return BAND_EN.get(name, name) if lang == "en" else name


# ---------- data ----------
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


@st.cache_data(show_spinner=False, ttl=3600)
def geocode_location(query: str):
    """Geocode a place name via OSM Nominatim. Returns dict with lat, lon, display_name or None."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "limit": 1, "countrycodes": "ID"}
    headers = {"User-Agent": "KarhutlaDashboard/1.0 (hackathon project)"}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data:
            return {
                "lat": float(data[0]["lat"]),
                "lon": float(data[0]["lon"]),
                "display_name": data[0]["display_name"],
            }
        return None
    except Exception:
        return None


# ---------- language toggle ----------
lang = st.sidebar.radio(TEXT["sidebar_title"]["en"], ["English", "Indonesian"],
                        index=0, format_func=lambda x: x)
lang = "en" if lang == "English" else "id"


df, gjson = load_data()
aggs = load_aggs()

# ---------- session state ----------
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "search_coords" not in st.session_state:
    st.session_state.search_coords = None  # {"lat": ..., "lon": ..., "display_name": ...}
if "search_radius" not in st.session_state:
    st.session_state.search_radius = 10.0

# ---------- header ----------
total_all = len(df)
days = df["acq_date"].dt.date.nunique()
worst = aggs["province"].iloc[0]
peak = aggs["daily"].loc[aggs["daily"]["hotspot"].idxmax()]

st.title("🔥 Karhutla Kalimantan — Wildfire Hotspot Analysis (NASA FIRMS)")

# ---------- ENSO / climate context (signature datajoget-style) ----------
ENSO = {
    "label": {"en": "CLIMATE CONTEXT · EL NIÑO 2026", "id": "KONTEKS IKLIM · EL NIÑO 2026"},
    "oni": "JJA 2026: +1.80 °C",
    "phase": {"en": "Strong El Niño", "id": "El Niño Kuat"},
    "body": {
        "en": (
            "Equatorial Pacific sea-surface temperature anomalies drive Indonesia's "
            "fire season. The 2026 El Niño (ONI +1.80 °C in JJA 2026, climbing from "
            "-0.39 in DJF) deepens the dry season across Kalimantan — suppressing "
            "monsoon rains and elevating peat-fire risk. The 29 Aug hotspot peak "
            "lines up with this drying signal."
        ),
        "id": (
            "Anomali suhu permukaan laut Pasifik ekuatorial mengendalikan musim "
            "kebakaran Indonesia. El Niño 2026 (ONI +1,80 °C pada JJA 2026, naik dari "
            "-0,39 di DJF) memperpanjang musim kering di Kalimantan — menekan hujan "
            "monsun dan meningkatkan risiko kebakaran gambut. Puncak hotspot 29 Agt "
            "selaras dengan sinyal kekeringan ini."
        ),
    },
    "source": "NOAA Climate Prediction Center · ONI (Oceanic Niño Index)",
}

with st.container():
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #1c2128 0%, #2a1a0a 100%);
            border: 1px solid #30363d;
            border-left: 4px solid #e67e22;
            border-radius: 12px;
            padding: 18px 22px;
            margin: 6px 0 12px;
        ">
            <div style="font-size:0.75rem;letter-spacing:1.5px;color:#e67e22;font-weight:700;text-transform:uppercase;">
                {ENSO['label'][lang]}
            </div>
            <div style="font-size:1.05rem;color:#f0f6fc;font-weight:600;margin-top:4px;">
                {ENSO['phase'][lang]} · {ENSO['oni']}
            </div>
            <div style="font-size:0.88rem;color:#c9d1d9;margin-top:8px;line-height:1.5;">
                {ENSO['body'][lang]}
            </div>
            <div style="font-size:0.72rem;color:#8b949e;margin-top:8px;">
                🛰️ Source: {ENSO['source']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.caption(T("caption_data").format(
    min=df["acq_date"].min().strftime("%d %b %Y"),
    max=df["acq_date"].max().strftime("%d %b %Y"),
))

c1, c2, c3, c4 = st.columns(4)
c1.metric(T("metric_total"), f"{total_all:,}")
c2.metric(T("metric_days"), T("metric_days_val").format(n=days))

# determine what to show in worst & peak — honour search filter if active
if st.session_state.search_coords is not None:
    search_mask = (
        df.apply(
            lambda r: haversine_km(
                r["latitude"], r["longitude"],
                st.session_state.search_coords["lat"],
                st.session_state.search_coords["lon"],
            )
            <= st.session_state.search_radius,
            axis=1,
        )
    )
    df_filtered = df[search_mask]
    if len(df_filtered):
        w = df_filtered.groupby("provinsi").size().reset_index(name="hotspot").sort_values("hotspot", ascending=False).iloc[0]
        pk = df_filtered.groupby(df_filtered["acq_date"].dt.date).size().reset_index(name="hotspot").sort_values("hotspot", ascending=False).iloc[0]
        worst_name = w["provinsi"]
        worst_val = int(w["hotspot"])
        peak_date = str(pk.iloc[0])
        peak_val = int(pk["hotspot"])
    else:
        worst_name = "—"
        worst_val = 0
        peak_date = "—"
        peak_val = 0
else:
    worst_name = worst["provinsi"]
    worst_val = int(worst["hotspot"])
    peak_date = peak["tanggal"]
    peak_val = int(peak["hotspot"])

c3.metric(T("metric_worst"), loc_prov(worst_name), T("metric_worst_val").format(n=worst_val))
c4.metric(T("metric_peak"), peak_date, T("metric_worst_val").format(n=peak_val))

st.divider()

# ---------- map + side panel ----------
col_map, col_side = st.columns([3, 2], gap="large")

with col_map:
    st.subheader(T("map_title"))

    # --- search section ---
    sc1, sc2 = st.columns([4, 1])
    with sc1:
        search_input = st.text_input(
            T("search_label"),
            value=st.session_state.search_query,
            placeholder=T("search_placeholder"),
            label_visibility="collapsed",
        )
    with sc2:
        search_clicked = st.button(T("search_btn"), use_container_width=True)

    if search_clicked and search_input.strip():
        st.session_state.search_query = search_input.strip()
        result = geocode_location(st.session_state.search_query)
        if result:
            st.session_state.search_coords = result
        else:
            st.session_state.search_coords = None
            st.warning(T("search_notfound").format(q=st.session_state.search_query))
    elif search_clicked and not search_input.strip():
        st.session_state.search_query = ""
        st.session_state.search_coords = None

    # default search state (used below even when inactive)
    search_hits = 0
    src = None
    mask = None

    # --- search controls when active ---
    if st.session_state.search_coords is not None:
        src = st.session_state.search_coords
        rcol1, rcol2 = st.columns([3, 1])
        with rcol1:
            st.session_state.search_radius = st.slider(
                T("search_radius"),
                min_value=1, max_value=50, value=int(st.session_state.search_radius), step=1,
                format=T("search_km").format(n="%d"),
            )
        with rcol2:
            if st.button(T("clear_btn"), use_container_width=True):
                st.session_state.search_query = ""
                st.session_state.search_coords = None
                st.rerun()

        # compute distance for every point
        distances = df.apply(
            lambda r: haversine_km(r["latitude"], r["longitude"], src["lat"], src["lon"]),
            axis=1,
        )
        mask = distances <= st.session_state.search_radius
        search_hits = int(mask.sum())
        if search_hits:
            st.success(T("search_result").format(
                n=search_hits,
                r=st.session_state.search_radius,
                place=src["display_name"][:70],
            ))
        else:
            st.info(T("search_none").format(r=st.session_state.search_radius))

    # --- date filter (applies to search results or full data) ---
    tanggal_opsi = sorted(df["acq_date"].dt.date.unique())
    pilih = st.select_slider(T("map_filter"), tanggal_opsi, value=tanggal_opsi[-1])

    # build subset: date filter + optional search filter
    subset = df[df["acq_date"].dt.date == pilih]
    if src is not None and search_hits > 0 and mask is not None:
        subset = subset[mask.loc[subset.index]]

    # --- map ---
    if src is not None and search_hits > 0:
        map_center = [src["lat"], src["lon"]]
        zoom = 11
    else:
        map_center = [-1.5, 114.5]
        zoom = 6

    m = folium.Map(location=map_center, zoom_start=zoom, tiles="CartoDB dark_matter")
    folium.GeoJson(
        gjson,
        name="provinsi",
        style_function=lambda f: {
            "fillColor": PROV_WARNA.get(f["properties"].get("shapeName"), "#cccccc"),
            "color": "#888888",
            "weight": 1.5,
            "fillOpacity": 0.1,
        },
        tooltip=folium.GeoJsonTooltip(fields=["shapeName"], aliases=[T("map_tooltip")]),
    ).add_to(m)

    # search radius circle
    if st.session_state.search_coords is not None:
        folium.Circle(
            location=[src["lat"], src["lon"]],
            radius=st.session_state.search_radius * 1000,
            color="#3498db",
            fill=True,
            fill_opacity=0.05,
            weight=2,
            tooltip=f"{st.session_state.search_radius} km",
        ).add_to(m)
        folium.Marker(
            location=[src["lat"], src["lon"]],
            popup=src["display_name"][:100],
            icon=folium.Icon(icon="crosshairs", prefix="fa", color="blue"),
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
                    f"{T('map_popup_frp')}: {row['frp']:.0f} MW<br>"
                    f"{loc_prov(row['provinsi'])}<br>{row['acq_datetime']}"
                ),
            ).add_to(m)
        cmap.add_to(m)
        cmap.caption = "FRP (MW)"
    else:
        st.info(T("map_empty"))

    st_folium(m, width="100%", height=520)

with col_side:
    # province table (respects search)
    if st.session_state.search_coords is not None and search_hits > 0:
        prov_agg = subset.groupby("provinsi").agg(
            hotspot=("frp", "count"),
            frp_mean=("frp", "mean"),
            frp_max=("frp", "max"),
        ).reset_index().sort_values("hotspot", ascending=False)
        prov_title = T("side_table_title")
    else:
        prov_agg = aggs["province"].copy()
        prov_title = T("side_table_title")

    if len(prov_agg):
        prov_agg["persen"] = (prov_agg["hotspot"] / prov_agg["hotspot"].sum() * 100).round(1)
        prov_agg["provinsi"] = prov_agg["provinsi"].map(loc_prov)
        prov_disp = prov_agg.rename(
            columns={
                "provinsi": T("col_province"),
                "hotspot": T("col_hotspot"),
                "frp_mean": T("col_frp_mean"),
                "frp_max": T("col_frp_max"),
                "persen": T("col_pct"),
            }
        )
        prov_disp[T("col_frp_mean")] = prov_disp[T("col_frp_mean")].round(1)
        prov_disp[T("col_frp_max")] = prov_disp[T("col_frp_max")].round(1)
        st.subheader(prov_title)
        st.dataframe(prov_disp, hide_index=True, width="stretch")
    else:
        st.subheader(prov_title)
        st.dataframe(pd.DataFrame(), hide_index=True, width="stretch")

    st.subheader(T("band_title"))
    bands = aggs["bands"].copy()
    bands["frp_band_loc"] = bands["frp_band"].map(loc_band)
    fig_b = px.bar(
        bands,
        x="frp_band_loc",
        y="count",
        color="frp_band_loc",
        color_discrete_map={loc_band(k): v for k, v in BAND_COLOR.items()},
        labels={"frp_band_loc": T("band_x"), "count": T("band_y")},
    )
    fig_b.update_layout(height=260, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_b, width="stretch")

st.divider()

# ---------- trend charts ----------
st.subheader(T("trend_title"))
t1, t2 = st.columns(2)

with t1:
    daily = aggs["daily"].copy()
    daily["tanggal"] = pd.to_datetime(daily["tanggal"])
    fig_d = px.line(
        daily,
        x="tanggal",
        y="hotspot",
        markers=True,
        labels={"tanggal": T("x_date"), "hotspot": T("y_hotspot")},
        title=T("trend_daily"),
    )
    fig_d.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_d, width="stretch")

with t2:
    top3 = aggs["top3_daily"].copy()
    top3["provinsi"] = top3["provinsi"].map(loc_prov)
    fig_t = px.line(
        top3,
        x="tanggal",
        y="hotspot",
        color="provinsi",
        markers=True,
        color_discrete_map=PROV_WARNA,
        labels={"tanggal": T("x_date"), "hotspot": T("y_hotspot"), "provinsi": T("col_province")},
        title=T("trend_top3"),
    )
    fig_t.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_t, width="stretch")

st.divider()

# ---------- heatmap + footer ----------
st.subheader(T("heat_title"))
heat = aggs["province_daily"].astype(int)
heat.index = [loc_prov(x) for x in heat.index] if lang == "id" else heat.index
fig_h = px.imshow(
    heat,
    labels=dict(x=T("heat_x"), y=T("heat_y"), color=T("heat_c")),
    aspect="auto",
    color_continuous_scale="YlOrRd",
    text_auto=True,
)
fig_h.update_layout(height=380, margin=dict(l=10, r=10, t=30, b=10))
st.plotly_chart(fig_h, width="stretch")

# ---------- "Inspect a Period" timeline tabs (datajoget-style) ----------
st.divider()
st.subheader({"en": "🗓️ Inspect a Period", "id": "🗓️ Pilih Periode"}[lang])

periods = [
    {"key": "all", "label": {"en": "All 2026", "id": "Semua 2026"}, "span": None},
    {"key": "el_nino_rise", "label": {"en": "El Niño Rise (Apr–Jun)", "id": "Naik El Niño (Apr–Jun)"}, "span": ("2026-04-01", "2026-06-30")},
    {"key": "peak", "label": {"en": "Peak (Aug)", "id": "Puncak (Agt)"}, "span": ("2026-08-01", "2026-08-31")},
    {"key": "recent", "label": {"en": "Recent (last 7d)", "id": "Terbaru (7h)"}, "span": None},
]
tabs = st.tabs([p["label"][lang] for p in periods])
for i, p in enumerate(periods):
    with tabs[i]:
        if p["span"]:
            pmask = (df["acq_date"] >= p["span"][0]) & (df["acq_date"] <= p["span"][1])
        elif p["key"] == "recent":
            latest = df["acq_date"].max()
            pmask = df["acq_date"] >= (latest - pd.Timedelta(days=7))
        else:
            pmask = pd.Series([True] * len(df))
        pdf = df[pmask]
        if len(pdf):
            pc = len(pdf)
            pworst = pdf.groupby("provinsi").size().idxmax()
            pworst_n = int(pdf.groupby("provinsi").size().max())
            ppeak = pdf.groupby(pdf["acq_date"].dt.date).size().idxmax()
            ppeak_n = int(pdf.groupby(pdf["acq_date"].dt.date).size().max())
            insight = {
                "en": f"**{pc:,}** hotspots across this window. Worst province: **{loc_prov(pworst)}** ({pworst_n:,}). "
                      f"Peak day: **{ppeak}** ({ppeak_n:,}).",
                "id": f"**{pc:,}** hotspot di rentang ini. Provinsi terparah: **{loc_prov(pworst)}** ({pworst_n:,}). "
                      f"Hari puncak: **{ppeak}** ({ppeak_n:,}).",
            }[lang]
            st.markdown(
                f'<div class="insight-box"><div class="title">{T("metric_total")}</div>'
                f'<div class="body">{insight}</div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.info({"en": "No data in this window.", "id": "Tidak ada data di rentang ini."}[lang])

st.caption(T("footer"))