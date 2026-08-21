# 📊 Panduan Tableau — Dashboard Karhutla Kalimantan

Panduan langkah demi langkah untuk membuat dashboard Tableau dari data
`data/tableau/*.csv`. Dirancang untuk **Tableau Public (gratis)** — hasilnya bisa
di-publish online dan jadi link portofolio.

> 🎯 **Target visualisasi utama: peta Kalimantan + titik-titik api.**
> Preview target-nya ada di `output/preview_peta_kalimantan.png` (dibuat dari data
> asli pakai Folium). Buka gambar itu dulu — itulah look yang kita kejar di
> Tableau: peta Kalimantan dengan batas provinsi, di atasnya titik-titik api yang
> warna & ukurannya menggambarkan intensitas (FRP), plus legend.

---

## 0. Persiapan

1. Download & install **Tableau Public** (gratis): https://public.tableau.com
2. Buat akun Tableau Public (pakai email kamu) — akun ini = portofolio online.
3. File data yang dipakai (sudah disiapkan di `data/tableau/`):

| File | Isi | Untuk sheet |
|---|---|---|
| `tableau_hotspots.csv` | 30.415 titik hotspot (detail) | Peta, scatter, filter |
| `tableau_province.csv` | Agregat per provinsi | Bar chart ranking |
| `tableau_daily.csv` | Total per hari | Line chart tren |
| `tableau_province_daily.csv` | Provinsi × hari | Heatmap |

---

## 1. Konek Data

- **Connect → Text file** → pilih `tableau_hotspots.csv`
- Ulangi untuk 3 file lain (klik **New Data Source**).
- **Periksa tipe data** (klik ikon `#`/`Abc` di kolom):
  - `acq_datetime` → **Date & Time** ✓ (otomatis)
  - `acq_date` → **Date** ✓
  - `frp` → **Number (decimal)** ✓
  - `latitude` / `longitude` → **Number** ✓
  - Sisanya otomatis String ✓
- **Penting untuk peta**: klik kanan `latitude` → **Geographic Role → Latitude**;
  klik kanan `longitude` → **Geographic Role → Longitude**. `provinsi_id` → **Geographic Role → Province/State** (kalau muncul opsi, pilih "Indonesia - Province").

---

## 2. Buat 5 Sheet

### Sheet 1 — Peta Kalimantan + Titik Api (visualisasi UTAMA 🔥)
Ini sheet bintangnya — tiru persis preview `preview_peta_kalimantan.png`:
1. Data source: `tableau_hotspots.csv`
2. Dobel-klik **Latitude** dan **Longitude** → otomatis jadi peta. Zoom ke
   Kalimantan (semua 5 provinsi terlihat).
3. **Batas provinsi**: drag **provinsi_id** ke **Detail** (Marks) → garis batas
   provinsi muncul di peta.
4. Drag **FRP** ke **Color** — warna titik = intensitas api.
5. Drag **FRP** ke **Size** — titik api besar = api kuat (di preview: radius
   membesar seiring FRP).
6. Edit warna: Colors → **Edit Colors** → palette **"Orange-Red"** atau **"Temps"**.
7. **Legend FRP** otomatis muncul di kanan atas — sama seperti preview.
8. Filter: drag **acq_date** ke **Filters** → pilih **Range of Dates** (biar user
   bisa geser slider tanggal di dashboard).

> Alternatif bagus: ganti Marks ke **Density** — titik panas jadi "heat haze" yang
> sangat fotogenik. Coba keduanya, pilih yang lebih enak dilihat.

### Sheet 2 — Bar Chart Ranking Provinsi
1. Data source: `tableau_province.csv`
2. Drag **provinsi_id** ke **Columns**; drag **jumlah_hotspot** ke **Rows**.
3. Sort menurun (klik ikon sort).
4. Drag **jumlah_hotspot** ke **Label** (tampilkan angka).
5. Warna: drag **jumlah_hotspot** ke **Color** dengan palette merah-oranye.

### Sheet 3 — Line Chart Tren Harian
1. Data source: `tableau_daily.csv`
2. Drag **acq_date** ke **Columns**; drag **jumlah_hotspot** ke **Rows**.
3. Marks → **Line**.
4. Drag **jumlah_hotspot** ke **Label** (tampilkan nilai per titik).
5. Tandai puncak: Analysis → **Reference Line** → per baris jumlah → tambahkan
   garis rata-rata (avg) atau maks.

### Sheet 4 — Heatmap Provinsi × Hari
1. Data source: `tableau_province_daily.csv`
2. Drag **provinsi_id** ke **Rows**; drag **acq_date** ke **Columns**.
3. Marks → **Square**.
4. Drag **jumlah_hotspot** ke **Color** (palette YlOrRd) + ke **Label**.
5. Hasil: kotak warna yang menunjukkan "ledakan api" di hari tertentu.

### Sheet 5 — (Bonus) Scatter FRP per Waktu
1. Data source: `tableau_hotspots.csv`
2. Drag **acq_datetime** ke **Columns**; drag **FRP** ke **Rows**.
3. Marks → **Circle**; drag **provinsi_id** ke **Color**.
4. Menunjukkan titik ekstrem (FRP 800+ MW) — cerita "api besar" kamu.

---

## 3. Rakit Dashboard

1. Klik ikon **New Dashboard**.
2. Set ukuran **Automatic** atau **Desktop Browser**.
3. Susun (peta jadi pusat — sesuai target visualisasi):
   - **Kiri (besar, ~60% lebar): Sheet 1 — Peta Kalimantan + Titik Api**
   - Kanan atas: **Sheet 2 — Bar Ranking** (filter provinsi)
   - Kanan bawah: **Sheet 3 — Tren Harian**
4. **Hubungkan filter**: klik Sheet 1 → ikon **Use as Filter**. Sekarang klik titik
   atau geser tanggal di peta → semua chart ikut berubah. (Coba juga dari bar chart.)
5. Tambah **judul dashboard**: "Karhutla Kalimantan — Analisis Hotspot NASA FIRMS"
6. Tambah **text box** (di bawah): satu kalimat temuan utama, misalnya:
   > "Kalimantan Barat menyumbang 41% dari 30.415 hotspot (14–21 Agt 2026);
   > puncak terjadi 18 Agustus dengan 5.905 deteksi dalam sehari."

---

## 4. Publish ke Tableau Public (link portofolio!)

1. **File → Save to Tableau Public As...**
2. Login akun kamu, kasih nama: `Karhutla-Kalimantan-Hotspot-Analysis`
3. Setelah publish, **Share** → salin link: `https://public.tableau.com/views/Karhutla-...`
4. Link ini yang kamu taruh di GitHub README, LinkedIn, dan web portofolio.

> 💡 Tips: sebelum publish, buka dashboard di mode **Present** dan pastikan filter
> jalan. Kalau ada sheet kosong, cek lagi data source di sheet itu.

---

## 5. Checklist kualitas (biar recruiter "wow")

- [ ] Peta punya warna intensitas + ukuran titik
- [ ] Semua angka konsisten dengan README (30.415 total, Kalbar 41%)
- [ ] Filter tanggal berfungsi lintas sheet
- [ ] Judul + 1 kalimat temuan di dashboard
- [ ] Link Tableau Public ada di README.md / README.id.md
