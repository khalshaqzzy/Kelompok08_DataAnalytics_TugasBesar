# Session Handoff - Kelompok08 Data Analytics Tugas Besar

Last updated: 2026-06-13, Asia/Jakarta

Update 2026-06-14:

- Menambahkan script `scripts/select_t1440_subset.py` untuk profiling semua file HKUST T1440, parsing metadata TTL, pemberian quality flag, dan pemilihan subset objektif.
- Output baru:
  - `dataset/profile_hkust_hko/t1440_meter_inventory_with_decision.csv`
  - `dataset/profile_hkust_hko/t1440_subset_selection_justification.md`
  - `dataset/processed/dim_entity_t1440.csv`
  - `dataset/processed/selected_t1440_meters.csv`
  - `dataset/processed/fact_energy_t1440_selected_long.csv`
  - `outputs/subset_selection/t1440_total_consumption_by_meter.png`
  - `outputs/subset_selection/t1440_quality_flag_counts.png`
  - `outputs/subset_selection/t1440_meter_count_by_building.png`
  - `outputs/subset_selection/selected_meters_daily_consumption.png`
- Keputusan subset utama: fokus pada `Cheng_Yu_Tung_Building` dengan 12 meter aktif full-coverage: `D0849`, `D0848`, `D0854`, `D0853`, `D0862`, `D0857`, `D0851`, `D0861`, `D0852`, `D0860`, `D0850`, `D0865`.
- Meter zero constant (`D0821`, `D0823`, `D0844`, `D0847`), near-zero/low-signal (`D0863`, `D0864`, `D0846`), dan short coverage (`D0816`) dicatat untuk data quality, bukan model utama.
- Menambahkan script `scripts/build_energy_weather_master.py` untuk membangun tabel HKO harian dan join ke master energy berdasarkan `date`.
- HKO harian berhasil diunduh ke `dataset/hko_open_data/raw/` menggunakan `scripts/download_hko_open_data.py`.
- Output gabungan baru:
  - `dataset/processed/hko_weather_daily.csv`
  - `dataset/processed/master_energy_weather_t1440_selected_daily.csv`
- Catatan kualitas HKO periode proyek: `rainfall_mm` missing 5 hari dan `global_solar_radiation_mj_m2` missing 1 hari.

## 0. Instruksi Wajib untuk Sesi Berikutnya

File ini adalah sumber konteks utama untuk melanjutkan pekerjaan. **Setiap perubahan penting pada project harus memperbarui `sessionHandoff.md`**, terutama jika ada:

- dataset baru atau file dataset yang dipindah;
- script baru atau perubahan pipeline;
- notebook, laporan, slide, memo, atau output visual baru;
- keputusan modelling, preprocessing, feature engineering, atau evaluasi;
- perubahan scope berdasarkan panduan tugas besar;
- issue/blocker yang ditemukan.

Jika melanjutkan sesi, baca file ini dulu, lalu cek status aktual repo dengan:

```powershell
git status --short
Get-ChildItem -Force
```

## 1. Konteks Project

Repo:

`C:\Users\Khalfani Shaquille\Documents\GitHub\Kelompok08_DataAnalytics_TugasBesar`

Mata kuliah:

Data Analitik

Topik sesuai panduan:

**Energi dan Efisiensi Gedung/Kampus**

Fokus proyek:

Analisis konsumsi listrik kampus menggunakan dataset smart meter HKUST dan data cuaca Hong Kong Observatory. Tujuannya untuk menemukan pola konsumsi, membandingkan efisiensi relatif antar meter/gedung/zona, mendeteksi anomali beban, dan menyiapkan dashboard/rekomendasi efisiensi.

Kerangka kerja wajib:

**OSEMN**:

- O - Obtain
- S - Scrub
- E - Explore
- M - Model
- N - iNterpret

Panduan tugas besar yang dipakai:

`C:\Users\Khalfani Shaquille\Downloads\1779174569814_Panduan_Tugas_Besar_Data_Analitik.pdf`

Poin penting dari panduan:

- Minimal 2 sumber data: 1 dataset utama dan 1 dataset pendukung.
- Minimal 1 data memiliki dimensi wilayah atau waktu.
- Raw data harus disimpan terpisah dari data hasil preprocessing.
- Laporan akhir mengikuti struktur OSEMN.
- Presentasi akhir mengikuti alur OSEMN.
- Tahap Model wajib ada: metode, input-output, evaluasi, keterbatasan.
- Tahap Interpret wajib minimal 3 insight dan 3 rekomendasi.
- Peran kelompok 4 orang boleh menggabungkan Documentation and Insight Lead dengan Data Analyst/Modeler atau Visualization/Dashboard Developer.

## 2. Keputusan Utama yang Sudah Diambil

Dataset utama:

**A 2.5-year campus-level smart meter database with equipment data for energy analytics**

Sumber:

- Dryad: <https://doi.org/10.5061/dryad.k3j9kd5h6>
- Artikel Scientific Data: <https://doi.org/10.1038/s41597-024-04106-1>

Dataset pendukung:

**Hong Kong Observatory Open Data**

Sumber umum:

- <https://www.weather.gov.hk/en/abouthko/opendata_intro.htm>

Dataset HKO yang digunakan:

- Daily mean temperature - Sai Kung
- Daily maximum temperature - Sai Kung
- Daily minimum temperature - Sai Kung
- Daily mean relative humidity - Sai Kung
- Daily total rainfall - Kau Sai Chau
- Daily global solar radiation - Kau Sai Chau
- Daily mean wind speed - Sai Kung

Alasan dataset pendukung:

HKUST berada di Sai Kung District, Hong Kong. Variabel cuaca seperti suhu, kelembapan, hujan, radiasi matahari, dan angin relevan untuk menjelaskan variasi konsumsi listrik, terutama beban pendinginan ruangan.

Strategi analisis awal:

- Gunakan HKUST **T1440** sebagai baseline harian karena cocok dengan HKO daily weather data.
- Gunakan HKUST **T60** hanya untuk eksplorasi pola jam pada sampel meter.
- Jangan langsung load seluruh raw Excel ke memory karena raw dataset besar.
- Tetap inventarisasi seluruh dataset, tetapi analisis awal memakai subset yang realistis.

## 3. Artefak Laporan dan Slide

File awal riset:

- `riset_energi_efisiensi_gedung_kampus.md`

Laporan awal Bab 1-2:

- `laporan_energi_efisiensi_gedung_kampus.md`
- `laporan_energi_efisiensi_gedung_kampus.pdf`

Laporan proposal terbaru:

- `laporan_proposal_energi_efisiensi_gedung_kampus.md`

Slide deck lengkap:

- `slides_energi_efisiensi_gedung_kampus.html`

Slide proposal maksimal 5 slide:

- `slides_proposal_energi_efisiensi_gedung_kampus.html`

Struktur slide proposal:

1. Pembuka
2. Pendahuluan lengkap
3. O - Obtain: sumber data
4. O - Obtain: strategi/pipeline dua dataset
5. Pembagian peran

Script presentasi 3 menit untuk slide 4:

- `script_presentasi_slide_4.md`
- Ada juga `script_presentasi_slide_4.pdf`

Memo dataset dan pipeline:

- `memo_dataset_energi_hkust_hko.md`

Notebook eksplorasi:

- `notebooks/eksplorasi_hkust_hko.ipynb`

PRD anomaly detection dan dashboard:

- `prd_energi_anomaly_powerbi.md`

Roadmap improvement:

- `roadmap_improvement_energi_dashboard.md`

## 4. Pembagian Peran Kelompok

Jumlah anggota: 4 orang.

Peran yang dipakai:

| Anggota | Peran | Tanggung jawab |
|---|---|---|
| Anggota 1 | Data Engineer | Mengambil data, struktur folder, raw data, dokumentasi sumber |
| Anggota 2 | Data Preprocessing Lead | Cleaning, missing value, resampling, integrasi data cuaca, feature engineering |
| Anggota 3 | Data Analyst / Modeler | EDA, perbandingan gedung/zona, anomaly detection, forecasting opsional, evaluasi |
| Anggota 4 | Visualization / Dashboard Developer + Documentation and Insight Lead | Dashboard, visualisasi, insight, rekomendasi, laporan, slide, README, deklarasi AI |

Keputusan penggabungan:

Documentation and Insight Lead digabung dengan Visualization / Dashboard Developer.

## 5. Dataset Lokal

Root dataset:

`dataset/`

### 5.1 HKUST Primary Dataset

Lokasi:

`dataset/doi_10_5061_dryad_k3j9kd5h6__v20240801/`

Struktur utama:

- `All_Data/All Data/Raw Dataset/Time-series data/`
- `All_Data/All Data/Raw Dataset/HKUST_Meter_Metadata.ttl`
- `All_Data/All Data/Clean Dataset/Resappled data/T15/`
- `All_Data/All Data/Clean Dataset/Resappled data/T30/`
- `All_Data/All Data/Clean Dataset/Resappled data/T60/`
- `All_Data/All Data/Clean Dataset/Resappled data/T1440/`

Inventory aktual dari profiling:

| Group | File count | Total size | Sample |
|---|---:|---:|---|
| raw_time_series | 1.394 | 773,253 MB | `GUI_NO.D0001.xlsx` |
| clean_T15 | 403 | 408,889 MB | `GUI_NO.D0001.xlsx` |
| clean_T30 | 645 | 349,720 MB | `GUI_NO.H0004.xlsx` |
| clean_T60 | 255 | 71,921 MB | `GUI_NO.D0601.xlsx` |
| clean_T1440 | 26 | 0,426 MB | `GUI_NO.D0816.xlsx` |

Format HKUST Excel:

- `.xlsx`
- dua kolom utama:
  - `time`
  - `number`

Normalisasi di script:

- `time` atau `date` / `timestamp`
- `meter_reading`
- `meter_id`
- `daily_consumption` atau `hourly_consumption` hasil differencing

Metadata TTL:

- File: `HKUST_Meter_Metadata.ttl`
- Format: Turtle / Brick Schema
- Fungsi: bukan data konsumsi, tetapi metadata lokasi/relasi.
- Dipakai untuk memahami meter berada di gedung/zona/equipment apa.
- Penting untuk naik dari level `meter_id` ke level gedung/zona/equipment.

Catatan tentang `.ttl`:

File `.ttl` sebagian besar berguna untuk relasi lokasi, tetapi bukan hanya lokasi. Isinya dapat mencakup meter, equipment, zone, building, room, dan hubungan antar entity berdasarkan Brick Schema. Tanpa `.ttl`, analisis masih bisa per meter, tetapi sulit menjelaskan konteks fisik meter.

### 5.2 HKO Open Data

Lokasi raw:

`dataset/hko_open_data/raw/`

File HKO:

| File | Variabel |
|---|---|
| `skg_mean_temperature.csv` | `mean_temperature_c` |
| `skg_max_temperature.csv` | `max_temperature_c` |
| `skg_min_temperature.csv` | `min_temperature_c` |
| `skg_relative_humidity.csv` | `relative_humidity_pct` |
| `ksc_total_rainfall.csv` | `rainfall_mm` |
| `ksc_global_solar_radiation.csv` | `global_solar_radiation_mj_m2` |
| `skg_mean_wind_speed.csv` | `mean_wind_speed_kmh` |

Format HKO:

- CSV
- dua baris awal berisi judul/metadata
- baris data memiliki pola:
  - Year
  - Month
  - Day
  - Value
  - Data Completeness

Normalisasi:

- `date`
- nilai numerik sesuai variabel
- kolom completeness: `*_completeness`

Coverage periode proyek:

Semua HKO dapat difilter ke 2022-01-01 sampai 2024-05-27, sesuai periode HKUST.

Missing pada periode proyek:

- temperature, humidity, wind: 0 missing
- rainfall: 5 missing
- global solar radiation: 1 missing

## 6. Script yang Sudah Dibuat

Folder:

`scripts/`

Script:

| Script | Fungsi |
|---|---|
| `download_hko_open_data.py` | Download 7 dataset HKO ke `dataset/hko_open_data/raw/` dan membuat manifest |
| `profile_datasets.py` | Profil file HKUST dan HKO: inventory, shape, periode, missing, sample rows |
| `explore_energy_weather.py` | Membuat dataset gabungan harian, EDA plots, anomaly baseline, baseline regression |
| `build_exploration_notebook.py` | Membuat dan mengeksekusi notebook eksplorasi `notebooks/eksplorasi_hkust_hko.ipynb` |

Cara menjalankan ulang workflow:

```powershell
python scripts\download_hko_open_data.py
python scripts\profile_datasets.py
python scripts\explore_energy_weather.py
python scripts\build_exploration_notebook.py
```

Dependency Python yang dipakai:

- pandas
- requests
- openpyxl
- matplotlib
- seaborn
- scikit-learn
- nbformat
- nbclient

Catatan:

`openpyxl` sudah pernah dipasang karena dibutuhkan untuk membaca Excel HKUST.

## 7. Output Data dan EDA yang Sudah Dibuat

Profil dataset:

- `dataset/profile_hkust_hko/dataset_profile.json`
- `dataset/profile_hkust_hko/exploration_summary.json`
- `dataset/profile_hkust_hko/hko_profile_summary.csv`
- `dataset/profile_hkust_hko/hkust_file_inventory.csv`
- `dataset/profile_hkust_hko/hkust_t1440_profile.csv`

Processed data:

- `dataset/processed/hko_weather_daily.csv`
- `dataset/processed/hkust_t1440_energy_long.csv`
- `dataset/processed/energy_weather_daily_sample.csv`

Visual EDA:

- `outputs/eda/daily_consumption_trend.png`
- `outputs/eda/consumption_vs_temperature.png`
- `outputs/eda/energy_weather_correlation.png`
- `outputs/eda/t60_hourly_profile_sample.png`

Notebook:

- `notebooks/eksplorasi_hkust_hko.ipynb`

Notebook status:

- 18 cell
- 12 code cell
- 12 code cell executed
- 0 error output

## 8. Dataset Gabungan

File:

`dataset/processed/energy_weather_daily_sample.csv`

Shape:

878 baris x 32 kolom

Periode:

2022-01-01 sampai 2024-05-27

Sumber:

- HKUST T1440 daily meter reading
- HKO daily weather

Kolom utama:

| Kelompok | Kolom |
|---|---|
| Waktu | `date`, `weekday`, `is_weekend`, `month`, `year` |
| Energi | `meter_count`, `valid_daily_consumption_count`, `total_daily_consumption`, `mean_daily_consumption`, `median_daily_consumption`, `max_meter_daily_consumption`, `missing_daily_consumption_count` |
| Cuaca | `mean_temperature_c`, `max_temperature_c`, `min_temperature_c`, `relative_humidity_pct`, `rainfall_mm`, `global_solar_radiation_mj_m2`, `mean_wind_speed_kmh` |
| Kualitas HKO | `*_completeness` |
| Feature engineering | `is_rainy_day`, `is_hot_day_28c`, `cooling_degree_day_24c` |
| Anomali/model awal | `zscore_total_daily_consumption`, `iqr_anomaly_flag`, `isolation_forest_anomaly` |

Cara menghitung konsumsi:

- HKUST T1440 dibaca sebagai meter reading.
- `daily_consumption` dihitung dengan `diff()` per meter.
- Hari pertama per meter dianggap missing karena tidak punya reading hari sebelumnya.
- Nilai negatif hasil diff dianggap invalid/missing.

## 9. Hasil Eksplorasi Awal

Statistik gabungan:

- `total_daily_consumption` count: 877
- mean: 16.251,13
- min: 12.817,60
- median: 16.245,09
- max: 19.186,26

Cuaca:

- mean temperature rata-rata: 23,22 C
- relative humidity rata-rata: 79,18%
- rainfall rata-rata: 5,13 mm
- global solar radiation rata-rata: 14,13 MJ/m2
- wind speed rata-rata: 9,49 km/h

Korelasi awal terhadap `total_daily_consumption`:

- `mean_daily_consumption`: 0,887
- `meter_count`: 0,720
- `median_daily_consumption`: 0,638
- `valid_daily_consumption_count`: 0,289
- `relative_humidity_pct`: 0,209
- `rainfall_mm`: 0,131
- `is_rainy_day`: 0,106
- `mean_temperature_c`: 0,029
- `global_solar_radiation_mj_m2`: -0,030
- `cooling_degree_day_24c`: -0,037
- `is_weekend`: -0,074

Interpretasi:

- Hubungan cuaca terhadap total agregat 26 meter T1440 masih lemah.
- Ini tidak berarti cuaca tidak relevan. Kemungkinan sinyal cuaca lebih jelas jika analisis turun ke gedung/zona/equipment tertentu, misalnya HVAC atau area akademik besar.
- Coverage meter memengaruhi total konsumsi, sehingga valid meter count harus dikontrol.
- Weekend memiliki korelasi negatif kecil dengan konsumsi, sesuai dugaan aktivitas kampus berkurang.

## 10. Modelling yang Direkomendasikan

Berdasarkan panduan, tahap Model wajib ada. Untuk topik ini, modelling yang paling masuk akal:

### 10.1 Model utama: Anomaly Detection

Tujuan:

Mendeteksi hari/jam dengan konsumsi listrik tidak normal.

Input:

- konsumsi listrik historis;
- meter/gedung/zona;
- fitur waktu: hour, day, weekday/weekend, month;
- fitur cuaca: temperature, humidity, rainfall, solar radiation, wind speed;
- fitur engineering: cooling degree day, rainy day, hot day.

Metode:

- baseline IQR;
- Z-score;
- Isolation Forest.

Output:

- daftar tanggal/jam anomali;
- meter/gedung/zona terdampak;
- skor/flag anomali;
- konteks cuaca dan waktu pada saat anomali.

Evaluasi:

- jumlah flag tidak berlebihan;
- bandingkan IQR vs Isolation Forest;
- visual check terhadap tren;
- interpretasi domain: apakah masuk akal sebagai konsumsi tinggi di luar pola.

Kelebihan:

- paling sesuai dengan rumusan masalah tentang anomali beban;
- mudah dijelaskan ke pengelola gedung;
- tidak membutuhkan label anomali.

Keterbatasan:

- tanpa ground truth, evaluasi berbasis pola dan interpretasi.

### 10.2 Model pendukung: Forecasting / Regression

Tujuan:

Memprediksi konsumsi listrik harian untuk meter/gedung terpilih.

Input:

- lag konsumsi historis;
- weekday/weekend;
- bulan;
- suhu;
- kelembapan;
- hujan;
- solar radiation;
- cooling degree day.

Metode kandidat:

- Linear Regression sebagai baseline;
- Random Forest Regressor untuk non-linear pattern;
- SARIMA/Prophet jika ingin time-series lebih formal.

Output:

- prediksi konsumsi harian;
- error prediksi;
- fitur yang berpengaruh.

Evaluasi:

- MAE;
- RMSE;
- R2;
- plot aktual vs prediksi.

Catatan hasil awal:

Baseline Linear Regression pada agregat total memiliki R2 sekitar 0,035 dan MAE sekitar 911,65. Ini berarti model agregat masih lemah. Forecasting sebaiknya dilakukan per meter/gedung terpilih, bukan total 26 meter sekaligus.

### 10.3 Opsional: Clustering Pola Konsumsi

Tujuan:

Mengelompokkan meter/gedung berdasarkan pola konsumsi.

Metode:

- K-Means;
- Hierarchical Clustering.

Fitur:

- rata-rata konsumsi;
- peak load;
- base load;
- konsumsi malam;
- konsumsi weekend;
- variasi harian;
- rasio peak/base.

Evaluasi:

- silhouette score;
- interpretasi cluster.

Catatan:

Clustering akan lebih berguna jika metadata `.ttl` sudah dipakai untuk menghubungkan meter ke gedung/zona/equipment.

### 10.4 Keputusan PRD Model dan Dashboard

Dokumen PRD terbaru:

- `prd_energi_anomaly_powerbi.md`

Versi PRD terbaru: **v1.1**.

Keputusan utama PRD:

- Model utama tugas besar adalah **Isolation Forest anomaly detection** tanpa label.
- Baseline pembanding tetap menggunakan IQR dan Z-score agar hasil Isolation Forest tidak berdiri sendiri.
- Power BI tidak melatih model secara dinamis. Model dijalankan di Python, lalu output skenario diload ke Power BI.
- PRD v1.1 disinkronkan dengan roadmap improvement: scope final dikunci ke **T1440 harian + TTL metadata**.
- TTL diprioritaskan untuk `dim_entity`, bukan hanya enhancement umum.
- Data quality flag wajib mencakup meter nol konstan, hampir nol, dan coverage pendek.
- Isolation Forest final harus memasukkan fitur konsumsi dan rolling deviation, bukan hanya cuaca dan kalender.
- Entity scorecard dan anomaly case review menjadi acceptance criteria tambahan.
- Skenario Isolation Forest yang disepakati:
  - `strict`: `contamination=0.03`
  - `balanced`: `contamination=0.05`
  - `sensitive`: `contamination=0.10`
- Parameter default: `n_estimators=100`, `random_state=42`, `max_samples=auto`.
- Output model yang direkomendasikan untuk Power BI: `dataset/processed/energy_weather_anomaly_scenarios.csv`.
- Kolom kunci output model: `date`, `entity_id`, `entity_type`, `daily_consumption`, fitur cuaca, fitur waktu, `scenario`, `contamination`, `anomaly_score`, `anomaly_flag`, `iqr_anomaly_flag`, dan `zscore_total_daily_consumption`.
- Granularitas default tetap harian T1440 + HKO daily weather. Jika TTL berhasil diparse, dashboard dapat naik ke level building/zone; jika belum, gunakan fallback `campus_total` atau `meter`.

Rancangan halaman Power BI dalam PRD:

1. Executive Overview
2. Consumption Trend
3. Anomaly Explorer
4. Weather Impact
5. Meter / Building Ranking
6. Data Quality and Methodology

Slicer wajib:

- Date range
- Scenario
- Anomaly flag
- Meter/building/zone jika tersedia
- Weekday/weekend
- Rainy day/hot day
- Data completeness

### 10.5 Roadmap Improvement Maksimal

Dokumen roadmap terbaru:

- `roadmap_improvement_energi_dashboard.md`

Keputusan roadmap:

- Target utama improvement adalah memaksimalkan kualitas tugas besar, bukan membangun sistem produksi.
- Scope data lanjutan dikunci pada **T1440 harian + TTL metadata**.
- T1440 tetap menjadi analytical table utama karena selaras dengan HKO daily weather.
- TTL diprioritaskan untuk membangun `dim_entity`, minimal berisi `meter_id`, `meter_name`, `entity_type`, `building`, `floor`, `room_or_equipment`, `usage_type`, dan `mapping_status`.
- Meter bermasalah yang perlu diberi flag:
  - nol konstan: `D0821`, `D0823`, `D0844`, `D0847`;
  - hampir nol: `D0846`, `D0864`;
  - coverage pendek: `D0816`.
- Top 5 meter T1440 menyumbang sekitar 66% konsumsi subset, sehingga contribution analysis dan quality filtering wajib dilakukan sebelum ranking dan modelling final.
- Output Power BI yang direkomendasikan:
  - `fact_energy_weather_daily`;
  - `fact_anomaly_scenarios`;
  - `dim_date`;
  - `dim_entity`;
  - `dim_scenario`.
- Roadmap memprioritaskan data quality flag, entity mapping, scenario-based Isolation Forest, entity scorecard, final EDA, dan dashboard interaktif.

Prioritas implementasi roadmap:

1. Buat script datamart Power BI untuk menghasilkan fact dan dimension tables.
2. Tambahkan quality flag dan exclusion logic untuk meter bermasalah.
3. Jalankan Isolation Forest 3 scenario dan ekspor `anomaly_score`.
4. Buat final EDA yang selaras dengan halaman dashboard.
5. Bangun Power BI dashboard dari fact/dimension tables.
6. Update laporan akhir OSEMN dengan hasil model, dashboard, insight, dan rekomendasi.

## 11. Rencana Pipeline Lanjutan

Prioritas selanjutnya:

1. Query/parse `HKUST_Meter_Metadata.ttl` supaya `meter_id` dapat dikaitkan ke gedung/zona/equipment.
2. Pilih 3-5 gedung/zona dengan coverage data terbaik.
3. Exclude atau label meter T1440 yang nilai reading-nya konstan nol.
4. Buat dataset final per gedung/zona.
5. Buat Bab 3 Scrub:
   - missing value;
   - duplikasi;
   - tipe data;
   - outlier;
   - integrasi dataset;
   - feature engineering.
6. Buat Bab 4 Explore:
   - statistik deskriptif;
   - minimal 3 visualisasi eksploratif;
   - interpretasi tiap visualisasi;
   - hubungan temuan dengan pertanyaan analitik.
7. Buat Bab 5 Model:
   - anomaly detection sebagai model utama;
   - forecasting/regression sebagai model pendukung jika waktu cukup.
8. Buat Bab 6 Interpret:
   - minimal 3 insight berbasis data;
   - minimal 3 rekomendasi spesifik;
   - pihak sasaran dan prioritas rekomendasi.

## 12. Known Issues / Hal yang Perlu Hati-hati

- `dataset/` dan `outputs/` berisi banyak file, saat ini muncul sebagai untracked di `git status`.
- `scripts/__pycache__/` juga muncul sebagai untracked. Jika membersihkan repo, jangan hapus dataset penting; cukup pertimbangkan `.gitignore` untuk cache.
- HKUST raw sangat besar. Jangan load seluruh raw Excel tanpa strategi chunk/subset.
- T1440 hanya 26 meter, belum mewakili seluruh kampus.
- HKO data harian cocok untuk T1440, tetapi kurang granular untuk T60.
- `.ttl` belum sepenuhnya dipakai dalam pipeline; ini adalah peluang peningkatan paling penting.
- Beberapa meter T1440 konstan nol: `D0821`, `D0823`, `D0844`, `D0847`.
- `D0816` hanya sampai 2022-06-30.
- Data completeness HKO `#` harus dipertahankan atau dijelaskan; jangan diam-diam dibuang tanpa alasan.

## 13. Validasi yang Pernah Dilakukan

Script:

```powershell
python -m py_compile scripts\download_hko_open_data.py scripts\profile_datasets.py scripts\explore_energy_weather.py
python -m py_compile scripts\build_exploration_notebook.py
```

Notebook:

- `notebooks/eksplorasi_hkust_hko.ipynb` berhasil dibuat dan dieksekusi.
- 0 error output.

EDA:

- Output visual PNG berhasil dibuat.

HTML slide:

- Slide proposal pernah dicek dengan browser local server untuk desktop dan mobile, tidak overflow.

## 14. Git / Workspace State Terakhir

Terakhir dicek pada 2026-06-13:

```text
?? dataset/
?? outputs/
?? scripts/__pycache__/
```

Catatan:

Beberapa file lain seperti laporan, memo, notebook, script, dan slide ada di workspace. Status git aktual perlu dicek ulang pada sesi berikutnya karena `.gitignore` atau tracking status mungkin berubah.

## 15. Artefak yang Perlu Dibaca Jika Melanjutkan

Urutan baca yang disarankan:

1. `sessionHandoff.md`
2. `laporan_proposal_energi_efisiensi_gedung_kampus.md`
3. `memo_dataset_energi_hkust_hko.md`
4. `notebooks/eksplorasi_hkust_hko.ipynb`
5. `scripts/explore_energy_weather.py`
6. `slides_proposal_energi_efisiensi_gedung_kampus.html`

## 16. Sumber Dataset

HKUST:

- Dryad dataset: <https://doi.org/10.5061/dryad.k3j9kd5h6>
- Scientific Data article: <https://doi.org/10.1038/s41597-024-04106-1>

HKO:

- Open Data intro: <https://www.weather.gov.hk/en/abouthko/opendata_intro.htm>
- Mean temperature Sai Kung: <https://data.weather.gov.hk/weatherAPI/opendata/opendata.php?dataType=CLMTEMP&rformat=csv&station=SKG>
- Maximum temperature Sai Kung: <https://data.weather.gov.hk/weatherAPI/opendata/opendata.php?dataType=CLMMAXT&rformat=csv&station=SKG>
- Minimum temperature Sai Kung: <https://data.weather.gov.hk/weatherAPI/opendata/opendata.php?dataType=CLMMINT&rformat=csv&station=SKG>
- Relative humidity Sai Kung: <https://data.weather.gov.hk/weatherAPI/cis/csvfile/SKG/ALL/daily_SKG_RH_ALL.csv>
- Rainfall Kau Sai Chau: <https://data.weather.gov.hk/weatherAPI/cis/csvfile/KSC/ALL/daily_KSC_RF_ALL.csv>
- Global solar radiation Kau Sai Chau: <https://data.weather.gov.hk/weatherAPI/cis/csvfile/KSC/ALL/daily_KSC_GSR_ALL.csv>
- Mean wind speed Sai Kung: <https://data.weather.gov.hk/cis/csvfile/SKG/ALL/daily_SKG_WSPD_ALL.csv>

## 17. Update Log

- 2026-06-13: Created handoff file with full project context, dataset state, pipeline, modelling plan, artifact inventory, and update rule.
- 2026-06-13: Added `prd_energi_anomaly_powerbi.md` with complete PRD for Isolation Forest anomaly detection and interactive Power BI dashboard. Updated handoff with model scenario decisions, dashboard page requirements, and expected Power BI model output.
- 2026-06-13: Added `roadmap_improvement_energi_dashboard.md` as the maximum-quality improvement roadmap from Obtain through Power BI dashboard. Updated handoff with T1440+TTL scope, data quality priorities, Power BI datamart targets, and recommended implementation sequence.
- 2026-06-13: Updated `prd_energi_anomaly_powerbi.md` to v1.1 so it matches the roadmap: T1440+TTL scope, required `dim_entity`, Power BI star schema outputs, quality flags for problematic meters, consumption/rolling features for Isolation Forest, entity scorecard, and anomaly case review.
