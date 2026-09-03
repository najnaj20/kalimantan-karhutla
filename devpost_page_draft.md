# Wildfire Guardian — Devpost Project Page (Draft)

> **Branding:** "Wildfire Guardian" untuk GatewayHacks; repo publik pakai nama
> `najnaj20/kalimantan-karhutla` (submission boleh beda nama dari repo).
>
> **Batas fakta:** angka & waktu sesuai data asli (14–21 Aug 2026, 30.972 hotspot).
> JANGAN tambah klaim yang belum didukung pipeline. Bagian [CI-NEXT] menandai
> fitur OpenCV/AI yang belum dibangun — jangan ditampilkan sebagai sudah jadi.

---

## 📌 Judul & Tagline

**Wildfire Guardian — Real-time Active-Fire & Smoke Monitoring for Indonesian Borneo**

> Tagline: *Turning NASA satellite detection into actionable early warning for the
> communities most exposed to forest and peatland fires.*

> **Live data (29 Agustus – 2 September 2026, via cron):** **61.575 hotspot** ·
> window 26 Agt – 2 Sep · puncak **29 Agt (13.568)** · provinsi terparah
> **Central Kalimantan (28.254, 46%)** · FRP max **1.167 MW**. Angka otomatis
> ter-refresh harian; ganti angka di bawah ini yang basi kalau window berubah.

---

## 🌍 The Problem (Social Impact — 40% of score)

Kalimantan (Indonesian Borneo) experiences some of the most severe **forest and
peatland fires** in the world — the primary driver of the transboundary **haze**
crisis that blankets Southeast Asia each dry season. These fires are not a remote
tragedy: they destroy biodiversity, emit vast carbon stocks from peat, and cause
documented respiratory illness across millions of people.

Yet the frontline responders — local fire brigades, village officials, health
offices — largely lack a simple, up-to-the-hour way to see where fires are
*actually burning right now* and how *intense* they are. Official reporting lags
by days. The result is reactive, not preventive.

**The scale (live data, 8-day window — coin linking cron-refresh):**

- **61.575** thermal fire detections across Kalimantan in the latest 8-day window (26 Aug – 2 Sep 2026)
- **45.9%** concentrated in **Central Kalimantan** — now the worst-affected province (28.254 points)
- Peak surge of **13.568 detections in one day** (29 Aug) — a fire outbreak pattern, not a decline
- Fire Radiative Power up to **1.167 MW** — extreme-intensity sources that drive transboundary haze

> *Angka di atas adalah data live dari cron harian. Saat kamu submit, angka pasti bisa lain — cek dashboard kamu untuk angka terkini.*

---

## 💡 Our Solution (Technical Execution — 30%)

Wildfire Guardian is an open, reproducible end-to-end pipeline that turns raw
NASA FIRMS satellite fire detections into a **live, map-first monitoring
dashboard** anyone can use.

**How it works — 5 stages:**

1. **Extract** — pull NASA's FIRMS active-fire data (VIIRS 375m + MODIS C6.1)
   *without any API key*, via the Humanitarian Data Exchange (HDX) mirror. Built
   with retry + backoff for resilience.
2. **Transform** — filter the regional feed to a Kalimantan bounding box, run
   point-in-polygon against provincial boundaries, and classify each hotspot to a
   province.
3. **Analyze** — aggregate daily & by province, classify fire intensity by Fire
   Radiative Power (FRP), and accumulate a growing seasonal `history_daily.csv`.
4. **Export** — push ready-to-use CSVs for Tableau Public (publishable portfolio
   dashboard).
5. **Visualize** — an interactive **Streamlit** dashboard: live folium map with an
   FRP heat legend, date slider, per-province table, and intensity histogram.

**Live, not static:** NASA's near-real-time FIRMS window is only ~7 days. So the
pipeline runs **daily via cron**, continuously accumulating a long-run seasonal
dataset — meaning the tool gets *more* valuable the longer it runs. It's designed
as a monitoring system, not a one-off analysis.

---

## 🏆 Why It Wins — Dampak Nyata (Impact-first framing)

[CI-NEXT] = komponen AI/CCTV yang akan dibangun di fase berikutnya (belum ada di
build sekarang — jangan klaim sudah jadi di page ini).

- **Early warning for the most exposed:** village-level fire crews can open a
  browser and see where today's fires are and their intensity — before official
  reports catch up.
- **Peat-fire carbon & haze:** high-FRP detection (up to 817 MW) identifies the
  sources that drive the transboundary haze — the single most impactful lever for
  regional health impacts.
- **Reproducible & no-barrier:** no API key, no paid service; every step is
  documented, git-versioned, and re-runnable. Judges and users can verify the
  data end-to-end.
- **Open-source foundation for AI early warning:** the accumulated daily dataset is
  a training foundation for [CI-NEXT] an agentic vision layer that augments
  satellite detection with CCTV/ground smoke detection, alert escalation, and
  drone tasking.

---

## 🛠 Tech Stack

| Layer | Tool |
|---|---|
| Data extraction | NASA FIRMS (VIIRS 375m + MODIS C6.1) via HDX mirror — no API key |
| Geospatial | geoBoundaries ADM1, point-in-polygon (shapely) |
| Analysis | pandas, numpy |
| Dashboard | Streamlit + folium + plotly + streamlit_folium |
| Visualization export | Tableau Public (CSV ready) |
| Automation | Bash + cron (daily refresh) |
| Repo | Public GitHub, README (EN + ID) |

---

## 🖼 Screenshots

> Pilih 3, prefer `dashboard_heatmap.png` sebagai hero.

1. **`dashboard_heatmap.png`** (HERO) — live dashboard: FRP map + KPI cards +
   per-province table + intensity chart.
2. **`preview_peta_kalimantan.png`** — standalone interactive hotspot map of
   Southeast Asia, fires concentrated on Kalimantan.
3. **`dashboard_charts.png`** — KPI + map + intensity analysis.

*(Ganti path jadi URL GitHub raw saat submit.)*

---

## 🔗 Links

- **Repo:** https://github.com/najnaj20/kalimantan-karhutla
- **Video pitch:** *(link YouTube unlisted — dari script terpisah)*
- **Data source:** NASA FIRMS — nasa-firms-fire-southeast-asia-viirs / -modis (CC BY)

---

## 🤝 Team

**Najwati** *(handle: Nanaj)* — solo builder; full-stack data + geospatial
pipeline, dashboard, and narrative.

> *(Ubah sesuai tim final. Tidak menampilkan target pribadi/biaya pribadi.)*

---

## ✅ Submission checklist (jangan lupa saat submit)

- [ ] Semua angka di atas bisa diverifikasi dari `data/processed/` di repo
- [ ] Hero image: `dashboard_heatmap.png`
- [ ] Video pitch link (5 menit max) — unlisted YouTube
- [ ] Pilih track: **Track 3: Environmental Sustainability**
- [ ] Join Gateway Discord (wajib): https://discord.gg/XgsX3f7JV
- [ ] Klik **Join Hackathon** di Devpost
