# Wildfire Guardian — Video Pitch Script (Max 5:00)

> Format: screen-recording demo + VO (atau langsung bicara). Timeline per segmen,
> total ≤ 5:00. VO jelas, jangan terburu-buru. Bahasa: **Inggris** (hackathon
> internasional; track di Devpost English). Bisa pakai subtitle.

---

## [00:00–00:25] HOOK — buka mata (25s)

> **Visual:** Slow zoom on `preview_peta_kalimantan.png` — Kalimantan penuh titik api.

"Every dry season, Indonesian Borneo burns. In a single 8-day window, **[tunjuk angka
61.575]** — over sixty-one thousand active fire detections lit up the island.
This haze doesn't stay in Indonesia. It crosses borders, sickens millions, and
releases carbon from peat that's been stored for thousands of years. But the
people responding on the ground are often the last to know."

---

## [00:25–01:15] PROBLEM (50s)

> **Visual:** B-roll satelelit / stock simmering haze (atau tetap di map, zoom ke
> Kalimantan Barat). Tampilkan 3 absis data.

"The problem isn't that we lack satellites. NASA tracks these fires every day.
The problem is that the information doesn't reach the people who need it, fast
enough. **Three things go wrong:**

1. **It's fragmented.** Fire data is scattered across science portals nobody
   outside research can easily use.
2. **It lags.** Official reporting trails the fires by days — by the time it's
   published, the plume has already moved.
3. **It's overwhelming.** 30,000+ points means nothing to a village fire crew
   without a way to see *today's* fires and *how* intense they are."

---

## [01:15–02:15] SOLUTION — demo (60s)

> **Visual:** Screen-record live Streamlit dashboard (`streamlit run
> dashboard/app.py`). Mulai dari KPI cards, lalu interact: scroll peta, gerakin
> date slider, hover table.

"Wildfire Guardian turns that raw NASA satellite data into a tool anyone can open
in a browser. Here's the live dashboard.

- **On top, the numbers that matter** — total hotspots, worst province, the peak
  fire day. **[klik wilayah]** Central Kalimantan — **46%** of the entire window's
  fires.
- **The map** shows every active fire dot, colored by intensity — Fire Radiative
  Power. Green is small, red is a blowtorch. **[gerakkan date slider]** Watch what
  happens as you scrub through the week — you can see the outbreak surge on
  August 29th — **13.568 detections in one day**.
- **The search feature** lets you find fires around any village. **[ketik:
  "Pangkalan Bun", lalu enter]** In seconds we see **108 hotspots within 10
  kilometers** of Pangkalan Bun. You can adjust the radius and see the circle
  extend on the map.
- **The intensity chart** tells the real story: most fires are small, but the few
  high-intensity ones — up to **1.167 megawatts** — are the ones that make the
  haze that blacks out cities across the region.

And the pipeline is fully reproducible — no API key, every step documented, and it
re-runs every day."

---

## [02:15–03:05] TECHNOLOGY (50s)

> **Visual:** Diagram alur 5-tahap (atau scrolling source code di GitHub).

"Under the hood it's a clean five-stage pipeline:

1. **Extract** — pull NASA FIRMS fire data (VIIRS + MODIS) without any API key,
   through a free humanitarian mirror, with retry-and-backoff.
2. **Transform** — geolocate every hotspot to its province using boundaries.
3. **Analyze** — aggregate daily and by province, classify intensity by FRP.
4. **Export** — push ready-to-use CSVs, including Tableau Public.
5. **Visualize** — the interactive Streamlit dashboard you just saw.

Because NASA only keeps ~7 days of near-real-time fire data, the pipeline runs
**daily via cron** — which means it's *accumulating history*. The longer it runs,
the richer the seasonal story. It's built to *watch*, not just analyze."

---

## [03:05–04:05] IMPACT — why it matters (60s)

> **Visual:** Kembali ke map, zoom-in West Kalimantan; teks overlay angka dampak.

"So why does this win? Impact first:

- **Speed to safety.** A village fire crew or district office opens a browser and
  sees today's fires — days before official reports. That's the window to act
  before the fire grows and the haze spreads.
- **Targeting the worst offenders.** The high-FRP detection points straight at the
  fires driving the transboundary haze — the biggest single lever for health
  impacts on millions.
- **Zero barriers.** No API key. No paid tool. Every line is public on GitHub, in
  Indonesian and English. Anyone can verify it, re-run it, or adapt it.
- **Built for the future.** [paparkan sebagai visi] This daily dataset is the
  foundation for an AI early-warning layer — agentic vision that combines satellite
  with ground CCTV smoke detection to escalate alerts, task drones, and route
  information to the right human at the right time."

---

## [04:05–04:50] CLOSE — CTA (45s)

> **Visual:** Final frame — logo + repo link + "Wildfire Guardian" + track.

"Wildfire Guardian is a small, open, reproducible tool that makes an enormous
crisis *visible* — in time to act. I'm submitting it to the **Environmental
Sustainability** track, because protecting Borneo's forests and its people isn't a
distant problem. It's happening right now — and it's visible right now.

**[soft slate]**
Check out the repo, the live dashboard, and the full analysis in the links below.
Thank you."

---

## ⏱ Timer & tips recording

| Segmen | Waktu | Durasi |
|---|---|---|
| Hook | 0:00–0:25 | 0:25 |
| Problem | 0:25–1:15 | 0:50 |
| Solution demo | 1:15–2:15 | 1:00 |
| Technology | 2:15–3:05 | 0:50 |
| Impact | 3:05–4:05 | 1:00 |
| Close | 4:05–4:50 | 0:45 |
| Buffer | 4:50–5:00 | 0:10 |
| **TOTAL** | | **5:00** |

**Tips:**
- Record screen at 1080p, 30fps; dashboard full-window.
- Rehearse 2×; the hook matters most — nail the opening 25s.
- Keep the demo under 60s so you don't blow the budget.
- Burn-in English subtitles (judges may watch muted).
- Export final, upload to YouTube as **unlisted**, link in Devpost.
- Add the YouTube thumbnail = `dashboard_heatmap.png`.
