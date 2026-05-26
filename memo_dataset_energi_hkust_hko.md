# Memo Dataset dan Pipeline

## Analisis Konsumsi dan Efisiensi Energi Gedung/Kampus

Memo ini merangkum hasil obtain, profiling, eksplorasi awal, interface data, dan rencana pipeline untuk topik **Energi dan Efisiensi Gedung/Kampus**. Arah analisis mengikuti panduan tugas besar Data Analitik berbasis OSEMN dan proposal `laporan_proposal_energi_efisiensi_gedung_kampus.md`.

---

## 1. Ringkasan Eksekusi

Proyek menggunakan dua kelompok data:

1. **Dataset utama: HKUST campus-level smart meter database**
   - Sumber: Dryad, DOI <https://doi.org/10.5061/dryad.k3j9kd5h6>
   - Artikel pendukung: Scientific Data, DOI <https://doi.org/10.1038/s41597-024-04106-1>
   - Peran: data inti untuk pola konsumsi listrik, perbandingan antar meter/gedung/zona, dan deteksi anomali beban.

2. **Dataset pendukung: Hong Kong Observatory Open Data**
   - Sumber umum: <https://www.weather.gov.hk/en/abouthko/opendata_intro.htm>
   - Peran: konteks cuaca untuk membantu membaca variasi konsumsi energi, terutama terkait suhu, kelembapan, hujan, radiasi matahari, dan angin.

Hasil implementasi awal:

- 7 dataset HKO berhasil diunduh ke `dataset/hko_open_data/raw/`.
- Profil HKUST dan HKO dibuat di `dataset/profile_hkust_hko/`.
- Dataset analitik harian gabungan dibuat di `dataset/processed/energy_weather_daily_sample.csv`.
- Visual eksploratif dibuat di `outputs/eda/`.
- Script reproducible tersedia di `scripts/`.

---

## 2. Inventaris Dataset HKUST

Lokasi lokal:

`dataset/doi_10_5061_dryad_k3j9kd5h6__v20240801/`

Struktur utama:

| Kelompok data | Jumlah file | Ukuran total | Contoh file |
|---|---:|---:|---|
| Raw time-series | 1.394 | 773,253 MB | `GUI_NO.D0001.xlsx` |
| Clean T15 | 403 | 408,889 MB | `GUI_NO.D0001.xlsx` |
| Clean T30 | 645 | 349,720 MB | `GUI_NO.H0004.xlsx` |
| Clean T60 | 255 | 71,921 MB | `GUI_NO.D0601.xlsx` |
| Clean T1440 | 26 | 0,426 MB | `GUI_NO.D0816.xlsx` |

Metadata:

| File | Format | Ukuran | Baris | Catatan |
|---|---|---:|---:|---|
| `HKUST_Meter_Metadata.ttl` | Turtle / Brick Schema | 2.352.640 bytes | 66.635 | Berisi relasi meter, lokasi, equipment, dan tipe entity berbasis Brick Schema |

Interface Excel HKUST:

| Kolom asli/normalisasi | Tipe hasil parsing | Makna |
|---|---|---|
| `time` | datetime | Timestamp pembacaan meter |
| `number` / `meter_reading` | numeric | Nilai pembacaan meter; pada analisis harian dipakai sebagai cumulative reading |

Catatan penting:

- File clean T1440 paling ringan dan cocok untuk integrasi dengan HKO karena HKO yang dipilih adalah data harian.
- File T60 tetap berguna untuk pola jam, tetapi tidak dipakai sebagai default karena dataset cuaca historis yang paling stabil tersedia di level harian.
- Dari 26 file T1440, 4 meter memiliki nilai konstan nol pada profil awal: `D0821`, `D0823`, `D0844`, dan `D0847`. Meter seperti ini perlu ditandai sebagai kandidat exclude atau ditangani khusus pada tahap Scrub.
- `D0816` hanya mencakup 2022-01-01 sampai 2022-06-30, sedangkan mayoritas T1440 lain mencakup 2022-01-01 sampai 2024-05-27.

---

## 3. Inventaris Dataset HKO

Folder raw:

`dataset/hko_open_data/raw/`

Dataset yang diunduh:

| File lokal | Dataset | Stasiun | Variabel normalisasi | Coverage total | Coverage periode proyek | Missing periode proyek |
|---|---|---|---|---|---|---:|
| `skg_mean_temperature.csv` | Daily Mean Temperature | Sai Kung | `mean_temperature_c` | 1993-04-01 s.d. 2026-04-30 | 2022-01-01 s.d. 2024-05-27 | 0 |
| `skg_max_temperature.csv` | Daily Maximum Temperature | Sai Kung | `max_temperature_c` | 1993-04-01 s.d. 2026-04-30 | 2022-01-01 s.d. 2024-05-27 | 0 |
| `skg_min_temperature.csv` | Daily Minimum Temperature | Sai Kung | `min_temperature_c` | 1993-04-01 s.d. 2026-04-30 | 2022-01-01 s.d. 2024-05-27 | 0 |
| `skg_relative_humidity.csv` | Daily Mean Relative Humidity | Sai Kung | `relative_humidity_pct` | 1993-04-01 s.d. 2026-04-30 | 2022-01-01 s.d. 2024-05-27 | 0 |
| `skg_mean_wind_speed.csv` | Daily Mean Wind Speed | Sai Kung | `mean_wind_speed_kmh` | 1993-04-01 s.d. 2026-04-30 | 2022-01-01 s.d. 2024-05-27 | 0 |
| `ksc_total_rainfall.csv` | Daily Total Rainfall | Kau Sai Chau | `rainfall_mm` | 2008-08-01 s.d. 2026-04-30 | 2022-01-01 s.d. 2024-05-27 | 5 |
| `ksc_global_solar_radiation.csv` | Daily Global Solar Radiation | Kau Sai Chau | `global_solar_radiation_mj_m2` | 2008-08-01 s.d. 2026-04-30 | 2022-01-01 s.d. 2024-05-27 | 1 |

Interface CSV HKO:

| Kolom hasil normalisasi | Tipe | Makna |
|---|---|---|
| `date` | datetime | Tanggal observasi |
| `value` atau nama variabel normalisasi | numeric | Nilai pengamatan cuaca |
| `data_completeness` | categorical | Kode kelengkapan data dari HKO, misalnya `C` atau `#` |

Alasan pemilihan stasiun:

- **Sai Kung** dipilih untuk suhu, kelembapan, dan angin karena lokasi HKUST berada di Sai Kung District.
- **Kau Sai Chau** dipilih untuk hujan dan radiasi matahari karena dataset historis harian yang tersedia relevan untuk kawasan Sai Kung dan lebih cocok dibanding data real-time yang sifatnya provisional.

---

## 4. Dataset Analitik Gabungan

File utama hasil integrasi:

`dataset/processed/energy_weather_daily_sample.csv`

Shape:

| Dataset | Shape | Periode |
|---|---:|---|
| `hkust_t1440_energy_long.csv` | 22.131 baris x 4 kolom | 2022-01-01 s.d. 2024-05-27 |
| `hko_weather_daily.csv` | 878 baris x 18 kolom | 2022-01-01 s.d. 2024-05-27 |
| `energy_weather_daily_sample.csv` | 878 baris x 32 kolom | 2022-01-01 s.d. 2024-05-27 |

Interface `energy_weather_daily_sample.csv`:

| Kelompok kolom | Kolom |
|---|---|
| Identitas waktu | `date`, `weekday`, `is_weekend`, `month`, `year` |
| Agregasi energi | `meter_count`, `valid_daily_consumption_count`, `total_daily_consumption`, `mean_daily_consumption`, `median_daily_consumption`, `max_meter_daily_consumption`, `missing_daily_consumption_count` |
| Cuaca | `mean_temperature_c`, `max_temperature_c`, `min_temperature_c`, `relative_humidity_pct`, `rainfall_mm`, `global_solar_radiation_mj_m2`, `mean_wind_speed_kmh` |
| Kualitas cuaca | Kolom `*_completeness` untuk setiap variabel HKO |
| Feature engineering | `is_rainy_day`, `is_hot_day_28c`, `cooling_degree_day_24c` |
| Anomali/model awal | `zscore_total_daily_consumption`, `iqr_anomaly_flag`, `isolation_forest_anomaly` |

Cara membentuk konsumsi harian:

- Nilai HKUST T1440 dibaca sebagai meter reading.
- `daily_consumption` dihitung sebagai selisih antar hari per meter.
- Hari pertama per meter tidak memiliki konsumsi turunan karena belum ada nilai hari sebelumnya, sehingga diperlakukan sebagai missing, bukan nol.
- Agregasi harian dilakukan dengan menjumlahkan `daily_consumption` valid dari meter T1440.

Missing value pada dataset gabungan:

| Kolom | Missing |
|---|---:|
| `total_daily_consumption` | 1 |
| `mean_daily_consumption` | 1 |
| `median_daily_consumption` | 1 |
| `max_meter_daily_consumption` | 1 |
| `rainfall_mm` | 5 |
| `global_solar_radiation_mj_m2` | 1 |
| `isolation_forest_anomaly` | 7 |

---

## 5. Eksplorasi Awal

Statistik ringkas dataset gabungan:

| Variabel | Count | Mean | Min | Median | Max |
|---|---:|---:|---:|---:|---:|
| `total_daily_consumption` | 877 | 16.251,13 | 12.817,60 | 16.245,09 | 19.186,26 |
| `mean_temperature_c` | 878 | 23,22 | 6,80 | 23,90 | 32,20 |
| `relative_humidity_pct` | 878 | 79,18 | 29,00 | 81,00 | 98,00 |
| `rainfall_mm` | 873 | 5,13 | 0,00 | 0,00 | 256,00 |
| `global_solar_radiation_mj_m2` | 877 | 14,13 | 0,99 | 14,55 | 28,10 |
| `mean_wind_speed_kmh` | 878 | 9,49 | 1,70 | 8,00 | 37,60 |

Korelasi awal terhadap `total_daily_consumption`:

| Variabel | Korelasi |
|---|---:|
| `mean_daily_consumption` | 0,887 |
| `meter_count` | 0,720 |
| `median_daily_consumption` | 0,638 |
| `valid_daily_consumption_count` | 0,289 |
| `relative_humidity_pct` | 0,209 |
| `rainfall_mm` | 0,131 |
| `is_rainy_day` | 0,106 |
| `mean_temperature_c` | 0,029 |
| `global_solar_radiation_mj_m2` | -0,030 |
| `cooling_degree_day_24c` | -0,037 |
| `is_weekend` | -0,074 |

Interpretasi awal:

1. Korelasi cuaca terhadap agregasi 26 meter T1440 masih lemah. Ini tidak berarti cuaca tidak relevan; kemungkinan sinyal cuaca lebih terlihat pada subset gedung tertentu seperti HVAC, area akademik besar, atau meter yang benar-benar mewakili cooling load.
2. `meter_count` dan `valid_daily_consumption_count` masih berpengaruh pada total konsumsi harian, sehingga kualitas coverage meter harus dikontrol sebelum membuat kesimpulan efisiensi.
3. Hujan dan kelembapan memiliki korelasi positif kecil terhadap konsumsi, tetapi perlu dianalisis lebih lanjut per gedung/zona.
4. Weekend cenderung berkorelasi negatif kecil dengan konsumsi, sesuai dugaan bahwa aktivitas kampus turun pada akhir pekan.
5. Baseline linear regression dengan fitur cuaca + waktu memiliki R2 0,035 dan MAE 911,65 pada dataset agregat. Ini menunjukkan baseline sederhana belum cukup menjelaskan variasi konsumsi total dan model perlu diarahkan ke level meter/gedung atau menambah fitur operasi kampus.

Deteksi anomali awal:

| Metode | Jumlah flag |
|---|---:|
| IQR pada `total_daily_consumption` | 17 hari |
| Isolation Forest pada fitur cuaca + waktu | 70 hari |

Contoh hari dengan flag IQR awal:

- 2022-01-05: `total_daily_consumption` 18.815,41; suhu rata-rata 19,0 C; hujan 0,5 mm.
- 2022-01-07: `total_daily_consumption` 18.886,70; suhu rata-rata 17,8 C; hujan 0,0 mm.
- 2022-05-13: `total_daily_consumption` 19.186,26; suhu rata-rata 25,6 C; hujan 68,5 mm.

Visual eksploratif:

| File | Isi |
|---|---|
| `outputs/eda/daily_consumption_trend.png` | Tren konsumsi harian T1440 |
| `outputs/eda/consumption_vs_temperature.png` | Scatter konsumsi harian vs suhu rata-rata |
| `outputs/eda/energy_weather_correlation.png` | Korelasi energi dan cuaca |
| `outputs/eda/t60_hourly_profile_sample.png` | Profil median konsumsi per jam dari sampel T60 |

---

## 6. Pipeline Lengkap OSEMN

### O - Obtain

Tujuan:

- Mengambil dataset HKUST dan HKO.
- Menyimpan raw data terpisah.
- Mendokumentasikan sumber, periode, format, ukuran, interface, dan keterbatasan awal.

Implementasi:

- `scripts/download_hko_open_data.py`
- Output raw HKO: `dataset/hko_open_data/raw/`
- Output manifest: `dataset/hko_open_data/profile/hko_download_manifest.csv`

### S - Scrub

Langkah:

1. Baca HKUST T1440 untuk analisis harian.
2. Hitung `daily_consumption` dari selisih meter reading per meter.
3. Tandai meter konstan nol dan hari dengan missing reading.
4. Normalisasi HKO ke format `date`, `value`, `data_completeness`.
5. Filter semua data ke periode 2022-01-01 sampai 2024-05-27.
6. Join energi dan cuaca berdasarkan `date`.
7. Buat fitur:
   - `is_rainy_day`
   - `is_hot_day_28c`
   - `cooling_degree_day_24c`
   - `is_weekend`
   - `month`, `year`, `weekday`

Output:

- `dataset/processed/hkust_t1440_energy_long.csv`
- `dataset/processed/hko_weather_daily.csv`
- `dataset/processed/energy_weather_daily_sample.csv`

### E - Explore

Eksplorasi yang sudah dibuat:

- Coverage dan shape semua data.
- Missing value energi dan cuaca.
- Statistik deskriptif energi dan cuaca.
- Tren konsumsi harian.
- Hubungan konsumsi dan suhu.
- Korelasi energi dan cuaca.
- Profil jam dari sampel T60.

Script:

- `scripts/profile_datasets.py`
- `scripts/explore_energy_weather.py`

### M - Model

Baseline awal:

- IQR anomaly flag pada total konsumsi harian.
- Z-score konsumsi harian.
- Isolation Forest pada fitur cuaca + waktu.
- Linear regression baseline untuk memprediksi `total_daily_consumption` dari cuaca + fitur waktu.

Catatan:

- Model baseline agregat belum cukup kuat karena R2 masih rendah.
- Untuk laporan akhir, model sebaiknya diarahkan ke level meter/gedung tertentu, bukan total agregat semua T1440.

### N - iNterpret

Insight awal yang dapat dibawa ke laporan:

1. Integrasi HKO berhasil dan coverage hariannya sesuai periode HKUST, sehingga data cuaca layak menjadi dataset pendukung.
2. Kualitas data energi harus dikontrol karena beberapa meter T1440 bernilai nol konstan atau memiliki coverage lebih pendek.
3. Hubungan cuaca terhadap total konsumsi agregat lemah, sehingga analisis lanjutan perlu dilakukan pada subset gedung/zona yang lebih relevan.

Rekomendasi awal:

1. Gunakan T1440 untuk pipeline utama dan T60 untuk eksplorasi pola jam pada meter terpilih.
2. Exclude atau beri label khusus pada meter nol konstan sebelum analisis efisiensi.
3. Pilih subset meter/gedung dengan coverage lengkap untuk model forecasting atau anomaly detection.
4. Simpan semua raw, clean, dan processed dataset secara terpisah agar sesuai panduan tugas besar.

---

## 7. Struktur File yang Dibuat

Script:

- `scripts/download_hko_open_data.py`
- `scripts/profile_datasets.py`
- `scripts/explore_energy_weather.py`

Data baru:

- `dataset/hko_open_data/raw/*.csv`
- `dataset/hko_open_data/profile/hko_download_manifest.csv`
- `dataset/hko_open_data/profile/hko_download_manifest.json`
- `dataset/profile_hkust_hko/dataset_profile.json`
- `dataset/profile_hkust_hko/hko_profile_summary.csv`
- `dataset/profile_hkust_hko/hkust_file_inventory.csv`
- `dataset/profile_hkust_hko/hkust_t1440_profile.csv`
- `dataset/profile_hkust_hko/exploration_summary.json`
- `dataset/processed/hkust_t1440_energy_long.csv`
- `dataset/processed/hko_weather_daily.csv`
- `dataset/processed/energy_weather_daily_sample.csv`

Visual:

- `outputs/eda/consumption_vs_temperature.png`
- `outputs/eda/daily_consumption_trend.png`
- `outputs/eda/energy_weather_correlation.png`
- `outputs/eda/t60_hourly_profile_sample.png`

---

## 8. Reproducibility

Urutan menjalankan ulang:

```bash
python scripts/download_hko_open_data.py
python scripts/profile_datasets.py
python scripts/explore_energy_weather.py
```

Dependensi Python:

- `pandas`
- `requests`
- `openpyxl`
- `matplotlib`
- `seaborn`
- `scikit-learn`

`openpyxl` diperlukan untuk membaca file `.xlsx` HKUST.

---

## 9. Keterbatasan

- Analisis awal memakai T1440 yang hanya mencakup 26 meter, sehingga belum mewakili seluruh 1.394 file raw atau seluruh kampus HKUST.
- Nilai HKUST diperlakukan sebagai meter reading kumulatif, lalu konsumsi harian dihitung dengan differencing. Asumsi ini perlu diverifikasi lebih lanjut dengan metadata atau dokumentasi teknis meter.
- Metadata Brick Schema belum dipetakan penuh ke gedung/zona pada memo ini; tahap berikutnya perlu query metadata untuk menghubungkan meter ke lokasi dan equipment.
- Data HKO harian cocok untuk T1440, tetapi kurang granular untuk menjelaskan pola jam T60. Jika ingin analisis jam, perlu sumber cuaca hourly atau strategi penempelan daily context.
- Kode `#` pada data completeness HKO menunjukkan data tidak sepenuhnya lengkap; baris tersebut belum dihapus, tetapi sudah dipertahankan sebagai kolom kualitas data.
- Hasil model baseline belum dimaksudkan sebagai model final, hanya validasi bahwa pipeline dapat menghasilkan fitur untuk tahap Model.

---

## 10. Arah Lanjutan untuk Tugas Besar

Prioritas berikutnya:

1. Query metadata `.ttl` agar setiap `meter_id` dapat dikaitkan ke gedung, zona, dan equipment.
2. Pilih 3-5 gedung/zona dengan coverage data terbaik.
3. Jalankan EDA per gedung/zona, bukan hanya agregat 26 meter T1440.
4. Buat minimal 3 visualisasi eksploratif untuk Bab 4:
   - Tren konsumsi harian per gedung/zona.
   - Heatmap weekday/month atau hour/day untuk T60.
   - Scatter konsumsi vs suhu atau cooling degree day.
5. Bangun model final:
   - Forecasting sederhana konsumsi harian, atau
   - Anomaly detection berbasis pola historis per meter/gedung.
6. Susun minimal 3 insight dan 3 rekomendasi spesifik untuk tim sarana prasarana atau pengelola gedung.
