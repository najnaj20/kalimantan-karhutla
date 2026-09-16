"""Streamlit dashboard — Peta Karhutla Indonesia.

Map-centric, ramah orang awam: satu peta besar + dua pilihan sederhana
(layer titik api / kualitas udara) + pemilih wilayah pulau.
"""
from __future__ import annotations

import json
from pathlib import Path

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(page_title="Peta Karhutla Indonesia", page_icon="🔥", layout="wide")

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"
BOUNDARIES = ROOT / "data" / "boundaries" / "idn_adm1.geojson"

ISLANDS = ["Semua (Indonesia)", "Sumatra", "Java", "Bali & Nusa Tenggara",
           "Kalimantan", "Sulawesi", "Maluku & Papua"]

ISLAND_CENTER = {
    "Semua (Indonesia)": (-2.5, 118.0, 5),
    "Sumatra": (0.5, 103.0, 5),
    "Java": (-7.3, 110.5, 7),
    "Bali & Nusa Tenggara": (-8.6, 118.0, 7),
    "Kalimantan": (-0.5, 114.0, 6),
    "Sulawesi": (-1.5, 121.0, 6),
    "Maluku & Papua": (-3.0, 135.5, 5),
}

PROV_ID = {
    "Aceh": "Aceh", "Bali": "Bali", "Bangka-Belitung Islands": "Kep. Bangka Belitung",
    "Banten": "Banten", "Bengkulu": "Bengkulu", "Central Java": "Jawa Tengah",
    "Central Kalimantan": "Kalimantan Tengah", "Central Sulawesi": "Sulawesi Tengah",
    "East Java": "Jawa Timur", "East Kalimantan": "Kalimantan Timur",
    "East Nusa Tenggara": "Nusa Tenggara Timur", "Gorontalo": "Gorontalo",
    "Jakarta Special Capital Region": "DKI Jakarta", "Jambi": "Jambi",
    "Lampung": "Lampung", "Maluku": "Maluku", "North Kalimantan": "Kalimantan Utara",
    "North Maluku": "Maluku Utara", "North Sulawesi": "Sulawesi Utara",
    "North Sumatra": "Sumatera Utara", "Papua": "Papua", "Riau": "Riau",
    "Riau Islands": "Kep. Riau", "South Kalimantan": "Kalimantan Selatan",
    "South Sulawesi": "Sulawesi Selatan", "South Sumatra": "Sumatera Selatan",
    "Southeast Sulawesi": "Sulawesi Tenggara",
    "Special Region of Yogyakarta": "DI Yogyakarta", "West Java": "Jawa Barat",
    "West Kalimantan": "Kalimantan Barat", "West Nusa Tenggara": "Nusa Tenggara Barat",
    "West Papua": "Papua Barat", "West Sulawesi": "Sulawesi Barat", "West Sumatra": "Sumatera Barat",
}

# kategori ISPU -> warna marker udara
def ispu_color_for(aqi: float) -> str:
    if aqi <= 50: return "#2ecc71"
    if aqi <= 100: return "#f1c40f"
    if aqi <= 200: return "#e67e22"
    if aqi <= 300: return "#e74c3c"
    return "#8e44ad"


def ispu_label(aqi: float) -> str:
    if aqi <= 50: return "Baik"
    if aqi <= 100: return "Sedang"
    if aqi <= 200: return "Tidak Sehat"
    if aqi <= 300: return "Sangat Tidak Sehat"
    return "Berbahaya"


CSS = """
<style>
html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif; }
.stApp { background-color: #0d1117; color: #c9d1d9; }
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1c2128 0%, #161b22 100%);
    border: 1px solid #30363d; border-radius: 12px; padding: 14px;
}
[data-testid="stMetricValue"] { color: #e6edf3 !important; }
[data-testid="stMetricDelta"] { color: #8b949e !important; }
[data-testid="stMetricLabel"] { color: #8b949e !important; }
.human-box {
    background: linear-gradient(135deg, #161b22, #1c2128);
    border-left: 4px solid #e67e22; border-radius: 10px;
    padding: 14px 18px; margin-bottom: 10px; color: #e6edf3; font-size: 1.02rem;
    line-height: 1.55;
}
.legend-chip { display:inline-block; width: 12px; height: 12px; border-radius: 50%;
    margin: 0 4px 0 12px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv(PROC / "indonesia_hotspots.csv", parse_dates=["acq_date"])
    gjson = json.loads(BOUNDARIES.read_text())
    return df, gjson


@st.cache_data(show_spinner=False, ttl=1800)
def load_aqi():
    p = PROC / "aqi_summary.json"
    if not p.exists():
        return None
    return json.loads(p.read_text())


df, gjson = load_data()
aqi = load_aqi()

st.title("🔥 Peta Kebakaran Hutan & Lahan — Indonesia")
st.caption("Titik panas terdeteksi NASA (update tiap hari) + kualitas udara model CAMS. "
           "Pilih apa yang ingin dilihat, lalu pilih wilayahnya.")

HARI = {"Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
        "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"}
BULAN = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mei", 6: "Jun",
         7: "Jul", 8: "Agu", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Des"}
BULAN_PANJANG = {1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
                 7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"}


def tgl_id(d, panjang=False) -> str:
    h = HARI.get(d.strftime("%A"), d.strftime("%a"))
    b = BULAN_PANJANG[d.month] if panjang else BULAN[d.month]
    return f"{h}, {d.day} {b} {d.year}" if not panjang else f"{d.day} {b} {d.year}"

# ---------- pemilih sederhana ----------
c1, c2, c3 = st.columns([1, 1.2, 1.6])
with c1:
    layer = st.radio("Ingin melihat apa?", ["🔥 Titik api", "🌫️ Kualitas udara"], label_visibility="visible")
with c2:
    island = st.selectbox("Wilayah", ISLANDS)
with c3:
    tanggal = None
    if layer == "🔥 Titik api":
        opsi = sorted(df["acq_date"].dt.date.unique())
        tanggal = st.select_slider("Tanggal", opsi, value=opsi[-1],
                                   format_func=lambda d: tgl_id(d))

lat0, lon0, zoom0 = ISLAND_CENTER[island]
TILES = "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"
TILES_ATTR = "Tiles © Esri — Source: Esri, OpenStreetMap contributors"
sub = df if island == "Semua (Indonesia)" else df[df["pulau"] == island]

# ---------- ringkasan bahasa manusia ----------
if layer == "🔥 Titik api":
    day = sub[sub["acq_date"].dt.date == tanggal]
    n = len(day)
    if n:
        top = day.groupby("provinsi").size().sort_values(ascending=False)
        top_p = PROV_ID.get(top.index[0], top.index[0])
        strong = int((day["frp"] >= 100).sum())
        st.markdown(
            f"<div class='human-box'>📅 <b>{tgl_id(tanggal, True)} — {island}:</b> "
            f"ditemukan <b>{n:,} titik api</b>, paling banyak di <b>{top_p}</b> ({int(top.iloc[0]):,} titik). "
            f"<b>{strong} titik berukuran besar/panas tinggi</b> — potensi kebakaran nyata, "
            f"bukan hanya panas matahari."
            + (" 🔥" if strong > 200 else "") + "</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(f"<div class='human-box'>📅 {tgl_id(tanggal, True)} — {island}: "
                    f"tidak ada titik api terdeteksi. ✅</div>", unsafe_allow_html=True)
else:
    if aqi:
        cities = aqi["cities"]
        cs = [(c, v) for c, v in cities.items()
              if island == "Semua (Indonesia)" or v.get("pulau") == island]
        cs.sort(key=lambda kv: -kv[1]["us_aqi_now"])
        worst_c, worst_v = cs[0]
        ok = sum(1 for _, v in cs if v["us_aqi_now"] <= 50)
        bad = sum(1 for _, v in cs if v["us_aqi_now"] > 100)
        st.markdown(
            f"<div class='human-box'>🌫️ <b>Kualitas udara {island} sekarang:</b> "
            f"terburuk di <b>{worst_c}</b> — {worst_v['ispu_category']} "
            f"(PM2.5 24 jam rata-rata {worst_v['pm25_24h_mean']:.0f} µg/m³). "
            f"Dari {len(cs)} kota: {ok} kota udaranya Baik, {bad} kota Tidak Sehat atau lebih buruk. "
            f"Kalau kategori Tidak Sehat, kurangi aktivitas luar tanpa masker.</div>",
            unsafe_allow_html=True,
        )
    else:
        st.info("Data kualitas udara belum tersedia.")

# ---------- peta besar ----------
m = folium.Map(location=[lat0, lon0], zoom_start=zoom0, tiles=TILES, attr=TILES_ATTR)

# base: batas provinsi (tip: nama + jumlah)
counts = sub.groupby("provinsi").size().to_dict()
folium.GeoJson(
    gjson,
    name="provinsi",
    style_function=lambda f: {
        "fillColor": "#e67e22",
        "color": "#484f58", "weight": 1, "fillOpacity": 0.06,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["shapeName"], aliases=["Provinsi:"],
        labels=True, localize=True, sticky=True,
    ),
).add_to(m)

if layer == "🔥 Titik api":
    day = sub[sub["acq_date"].dt.date == tanggal]
    if len(day):
        # agregasi per grid ~3km supaya peta ringan (ratusan marker, bukan ribuan)
        g = (day.assign(rlat=(day["latitude"] / 0.03).round(),
                        rlon=(day["longitude"] / 0.03).round())
                .groupby(["rlat", "rlon"])
                .agg(lat=("latitude", "mean"), lon=("longitude", "mean"),
                     n=("frp", "size"), frp=("frp", "max"),
                     prov=("provinsi", "first"),
                     sensor=("sensor", "first"),
                     when=("acq_datetime", "first"))
                .reset_index())
        # warna berdasar kekuatan panas maksimum di sel
        def cell_color(frp):
            if frp >= 500: return "#ff2d2d"
            if frp >= 100: return "#e67e22"
            if frp >= 20: return "#f1c40f"
            return "#9acd32"
        for _, r in g.iterrows():
            folium.CircleMarker(
                location=[r["lat"], r["lon"]],
                radius=min(4 + 1.6 * r["n"], 16),
                color=None, fill=True, fill_color=cell_color(r["frp"]), fill_opacity=0.8,
                popup=(f"<b>{int(r['n'])} titik</b> di area ini (±3 km)<br>"
                       f"Kekuatan panas maks: {r['frp']:.0f} MW<br>"
                       f"{PROV_ID.get(r['prov'], r['prov'])}<br>"
                       f"Deteksi pertama: {r['when']} (satelit {str(r['sensor']).upper()})"),
            ).add_to(m)
        m.get_root().html.add_child(folium.Element(
            "<style>.pn-legend{position:absolute;bottom:30px;left:20px;z-index:999;"
            "background:#161b22e8;color:#e6edf3;padding:8px 12px;border-radius:8px;"
            "font-size:13px;line-height:1.6}</style>"
            "<div class='pn-legend'><b>Kekuatan panas</b><br>"
            "<span style='color:#9acd32'>●</span> kecil &nbsp;"
            "<span style='color:#f1c40f'>●</span> sedang<br>"
            "<span style='color:#e67e22'>●</span> besar &nbsp;"
            "<span style='color:#ff2d2d'>●</span> sangat besar</div>"))
    else:
        st.info("Tidak ada titik api pada tanggal ini di wilayah ini.")

else:  # kualitas udara
    if aqi:
        for c_name, v in aqi["cities"].items():
            if island != "Semua (Indonesia)" and v.get("pulau") != island:
                continue
            aqi_now = v["us_aqi_now"]
            col = v.get("ispu_color") or ispu_color_for(aqi_now)
            lat, lon = v.get("lat"), v.get("lon")
            if lat is None:
                continue
            folium.Marker(
                location=[lat, lon],
                icon=folium.DivIcon(
                    icon_size=(84, 40), icon_anchor=(42, 20),
                    html=(f"<div style='background:{col};color:#0d1117;font-weight:800;"
                          f"padding:3px 8px;border-radius:14px;font-size:13px;"
                          f"text-align:center;border:2px solid #0d111780;white-space:nowrap;"
                          f"box-shadow:0 2px 6px #0008'>{c_name}<br>{aqi_now:.0f}</div>"),
                ),
                popup=(f"{c_name} — {PROV_ID.get(v['provinsi'], v['provinsi'])}<br>"
                       f"Udara: <b>{v['ispu_category']}</b> (AQI {aqi_now:.0f})<br>"
                       f"PM2.5 rata-rata 24 jam: {v['pm25_24h_mean']:.0f} µg/m³<br>"
                       f"PM2.5 saat ini: {v['pm25_now']:.1f} µg/m³"),
            ).add_to(m)
        m.get_root().html.add_child(folium.Element(
            "<style>.pn-legend{position:absolute;bottom:30px;left:20px;z-index:999;"
            "background:#161b22e8;color:#e6edf3;padding:8px 12px;border-radius:8px;"
            "font-size:13px;line-height:1.6}</style>"
            "<div class='pn-legend'><b>Kategori udara (AQI)</b><br>"
            "<span style='color:#2ecc71'>●</span> 0–50 Baik &nbsp;"
            "<span style='color:#f1c40f'>●</span> 51–100 Sedang<br>"
            "<span style='color:#e67e22'>●</span> 101–200 Tidak Sehat &nbsp;"
            "<span style='color:#e74c3c'>●</span> 201–300 Sangat Buruk<br>"
            "<span style='color:#8e44ad'>●</span> &gt;300 Berbahaya</div>"))

st_folium(m, width="1180", height=620)

# ---------- angka pendukung (tetap sederhana) ----------
k1, k2, k3, k4 = st.columns(4)
if layer == "🔥 Titik api":
    day = sub[sub["acq_date"].dt.date == tanggal]
    k1.metric(f"Titik api {island}", f"{len(day):,}")
    k2.metric("Provinsi terdampak", f"{day['provinsi'].nunique()}")
    k3.metric("Titik panas tinggi", f"{int((day['frp'] >= 100).sum()):,}")
    k4.metric("7 hari terakhir", f"{len(sub):,}")
else:
    cities = aqi["cities"] if aqi else {}
    cs = [v for v in cities.values()
          if island == "Semua (Indonesia)" or v.get("pulau") == island]
    if cs:
        worst = max(cs, key=lambda v: v["us_aqi_now"])
        k1.metric("Kota dipantau", f"{len(cs)}")
        k2.metric("AQI terburuk sekarang", f"{worst['us_aqi_now']:.0f}", worst.get("provinsi"))
        k3.metric("Baik / Sedang", f"{sum(1 for v in cs if v['us_aqi_now'] <= 100)}")
        k4.metric("Tidak Sehat ke atas", f"{sum(1 for v in cs if v['us_aqi_now'] > 100)}")

# ---------- detail untuk yang mau ngulik ----------
with st.expander("📊 Lihat tren & data lengkap"):
    cc1, cc2 = st.columns(2)
    with cc1:
        st.markdown("**Titik api per hari, per pulau**")
        daily = (df.groupby([df["acq_date"].dt.date, "pulau"]).size()
                 .unstack(fill_value=0))
        st.line_chart(daily, height=280)
    with cc2:
        st.markdown(f"**Top 10 provinsi — 7 hari terakhir{' (' + island + ')' if island != 'Semua (Indonesia)' else ''}**")
        top10 = (sub.groupby("provinsi").size().sort_values(ascending=False).head(10))
        top10.index = [PROV_ID.get(i, i) for i in top10.index]
        st.bar_chart(top10, height=280)
    st.caption("Sumber: NASA FIRMS (satelit MODIS & VIIRS), Open-Meteo/CAMS untuk kualitas udara. "
               "PM2.5 = partikel halus hasil pembakaran; AQI = indeks 0–500, makin besar makin berbahaya.")

st.caption("Diperbarui otomatis setiap hari. Data hotspot = 7 hari terakhir.")
