# 🔥 Karhutla Kalimantan — Analisis Hotspot Kebakaran (NASA FIRMS)

> 📖 [English](README.md) · [Bahasa Indonesia](README.id.md)

Analisis data end-to-end **deteksi titik panas (hotspot) kebakaran hutan & lahan di
Kalimantan** dari NASA FIRMS (VIIRS 375m + MODIS C6.1), ditarik **tanpa kunci API**
lewat mirror Humanitarian Data Exchange (HDX). Dibangun sebagai proyek portofolio
data analyst: data asli, cerita yang kuat, pipeline yang bisa direproduksi.

**Jendela data:** 14–21 Agustus 2026 · **30.415 hotspot terdeteksi** · Puncak: 18 Agt
(5.905/hari) · Provinsi terparah: Kalimantan Barat (41% dari total)

![Dashboard atas](output/dashboard_top.png)

## Isi proyek

```
kalimantan-karhutla/
├── src/
│   ├── extract.py    # tarik CSV FIRMS VIIRS+MODIS 7 hari (retry + backoff)
│   ├── transform.py  # filter bbox → point-in-polygon → penentuan provinsi
│   ├── analyze.py    # agregat harian/provinsi, kelas intensitas FRP
│   └── pipeline.py   # extract → transform → analyze, ujung ke ujung
├── dashboard/
│   └── app.py        # Streamlit: peta folium interaktif + chart plotly
├── data/
│   ├── raw/          # CSV FIRMS asli (Asia Tenggara)
│   ├── processed/    # hotspot Kalimantan yang sudah bersih + agregat
│   └── boundaries/   # batas provinsi (geoBoundaries ADM1, CC BY)
├── output/
│   ├── LAPORAN.md    # temuan & rekomendasi (Bahasa Indonesia)
│   └── dashboard_*.png  # tangkapan layar dashboard
└── scripts/screenshot.py  # capture dashboard headless (Playwright)
```

## Temuan utama (jendela 8 hari)

1. **Kalimantan Barat episentrum** — 12.495 hotspot (41,1%), disusul Kalimantan
   Tengah (10.555; 34,7%).
2. **Lonjakan tajam 16→18 Agt** — jumlah harian naik 2× lipat menjadi 5.905 dan
   tetap tinggi (5.500+) sampai 21 Agt: pola "ledakan api", bukan yang mereda.
3. **Ada api berintensitas tinggi** — FRP hingga **817 MW** di Kaltim/Kalsel; titik
   FRP tinggi inilah sumber kabut asap lintas batas.

## Cara menjalankan

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1. Jalankan pipeline (unduh data 7 hari terbaru, ~30 MB)
python src/pipeline.py

# 2. Buka dashboard
streamlit run dashboard/app.py
# buka http://localhost:8501

# 3. (Opsional) ambil ulang screenshot
python scripts/screenshot.py   # butuh playwright + chromium
```

## Batasan yang jujur

- **Jendela NRT**: data near-real-time FIRMS hanya ~7 hari; makin lama proyek
  berjalan, makin kaya cerita musimannya. Cron harian (`python src/pipeline.py`)
  akan mengakumulasi riwayat ke `data/processed/`.
- **Hotspot ≠ luas terbakar**: deteksi adalah anomali termal; VIIRS mendeteksi lebih
  banyak titik daripada MODIS karena resolusinya lebih halus (375m vs 1km) — keduanya
  digabung untuk cakupan, bukan dihitung ganda sebagai luas.
- **FRP adalah proksi** intensitas api, bukan ukuran kobaran.
- Proyek ini untuk portofolio/edukasi, **bukan** alat peringatan dini resmi.

## Sumber data & lisensi

- **NASA FIRMS** (VIIRS S-NPP/NOAA-20/21 C2, MODIS C6.1) — publik, via mirror HDX:
  `nasa-firms-active-fire-southeast-asia-viirs` / `-modis` (CC BY).
- **Batas provinsi**: geoBoundaries `IDN_ADM1` (CC BY) via HDX.
- **Konteks ENSO** (untuk studi musiman): indeks NOAA ONI.
