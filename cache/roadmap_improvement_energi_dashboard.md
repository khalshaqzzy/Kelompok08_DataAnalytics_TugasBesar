# Roadmap Improvement Maksimal

## HKUST Energy Analytics + React Dashboard

| Komponen | Keterangan |
|---|---|
| Tujuan utama | Memaksimalkan kualitas tugas besar Data Analitik |
| Kerangka kerja | OSEMN: Obtain, Scrub, Explore, Model, iNterpret |
| Dataset utama | HKUST smart meter dataset |
| Dataset pendukung | Hong Kong Observatory Open Data |
| Scope data prioritas | T1440 harian + metadata TTL |
| Output akhir yang dituju | Dataset dashboard-ready, anomaly detection defensible, React dashboard interaktif, insight dan rekomendasi |
| Status dokumen | Roadmap implementasi lanjutan |
| Tanggal | 2026-06-15 |

---

# Scope Alignment Note - 2026-06-15

Roadmap ini dipertahankan sebagai cache planning artifact untuk repo pipeline dan dashboard readiness. Untuk scope kerja saat ini:

1. Perubahan implementasi dibatasi ke repo pipeline/dashboard dan cache planning files.
2. Final academic report/documentation, presentation, slide deck, video/demo, dan README berada di luar scope kecuali diminta eksplisit di task terpisah.
3. PRD tetap menjadi source-of-truth produk analitik; roadmap ini hanya menyusun prioritas improvement.
4. Notebook aktif harus formal seperti laporan analitis, tetapi hanya memuat bagian OSEMN yang sudah didukung output final.
5. Klaim analisis harus dibatasi pada selected T1440 meter-level subset, terutama `Cheng_Yu_Tung_Building`, bukan keseluruhan kampus HKUST.
6. Target visualisasi final terbaru adalah standalone React dashboard di `web/` yang dipublish ke Vercel. Power BI tetap boleh dipakai sebagai historical/manual alternative, tetapi bukan target utama implementasi berikutnya.

---

# 1. Ringkasan Eksekutif

Roadmap ini menyusun improvement dari awal pipeline sampai dashboard akhir untuk proyek **Analisis Konsumsi dan Efisiensi Energi Gedung/Kampus**. Fokus utama bukan membangun sistem produksi, tetapi menghasilkan tugas besar yang kuat secara akademik: sumber data jelas, preprocessing dapat dipertanggungjawabkan, eksplorasi tajam, model anomaly detection masuk akal, dan dashboard React yang bisa dipublish ke Vercel benar-benar membantu interpretasi.

Keputusan utama:

1. **T1440 tetap menjadi analytical table utama** karena selaras dengan data cuaca harian HKO.
2. **TTL harus mulai dimanfaatkan** agar analisis tidak berhenti di level agregat kampus atau ID meter tanpa konteks.
3. **Isolation Forest tetap menjadi model utama**, tetapi perlu diperbaiki menjadi scenario-based dan menghasilkan skor anomali.
4. **React dashboard harus membaca prebuilt JSON dari output Python**, bukan melatih model secara dinamis.
5. **Dashboard harus interaktif**, dengan filter skenario model, waktu, entity, kondisi cuaca, dan status anomali.

---

# 2. Kondisi Saat Ini

## 2.1 Artefak yang Sudah Ada

| Artefak | Status | Catatan |
|---|---|---|
| `memo_dataset_energi_hkust_hko.md` | Ada | Memo profiling, pipeline, dan EDA awal |
| `prd_energi_anomaly_powerbi.md` | Ada | PRD model Isolation Forest dan Power BI dashboard |
| `notebooks/eksplorasi_hkust_hko.ipynb` | Ada | Notebook eksplorasi awal |
| `scripts/download_hko_open_data.py` | Ada | Download HKO Open Data |
| `scripts/profile_datasets.py` | Ada | Profil HKUST dan HKO |
| `scripts/explore_energy_weather.py` | Ada | Dataset harian, EDA awal, baseline model |
| `dataset/processed/energy_weather_daily_sample.csv` | Ada | Dataset gabungan harian energi + cuaca |

## 2.2 Dataset Processed Saat Ini

Dataset utama processed:

`dataset/processed/energy_weather_daily_sample.csv`

Karakteristik:

| Aspek | Nilai |
|---|---:|
| Baris | 878 |
| Kolom | 32 |
| Periode | 2022-01-01 sampai 2024-05-27 |
| Basis energi | HKUST T1440 |
| Basis cuaca | HKO daily weather |
| Jumlah meter T1440 | 26 |

## 2.3 Temuan Kualitas Data T1440

Meter yang perlu ditangani khusus:

| Kategori | Meter | Alasan |
|---|---|---|
| Nol konstan | `D0821`, `D0823`, `D0844`, `D0847` | Tidak memberi sinyal konsumsi aktif |
| Hampir nol | `D0846`, `D0864` | Kontribusi nyaris tidak bermakna pada total |
| Coverage pendek | `D0816` | Hanya sampai 2022-06-30 |

Temuan penting:

1. Top 5 meter menyumbang sekitar **66%** total konsumsi T1440.
2. Agregasi total kampus dapat bias jika meter nol, hampir nol, atau coverage pendek tidak diberi flag.
3. Analisis anomali perlu dipisahkan antara:
   - anomali konsumsi nyata;
   - anomali karena data quality;
   - hari dengan coverage meter berubah.

## 2.4 Potensi Metadata TTL

Metadata TTL berpotensi besar untuk meningkatkan kualitas interpretasi:

| Entity / relasi | Jumlah terdeteksi |
|---|---:|
| `brick:Electrical_Meter` | 1.432 |
| `brick:Building` | 34 |
| `brick:Floor` | 160 |
| `brick:Room` | 279 |
| `brick:isMeteredBy` | 1.581 |

Makna untuk proyek:

1. TTL dapat dipakai untuk membuat `dim_entity`.
2. Dashboard dapat naik dari level meter ke building/floor/equipment jika mapping cukup baik.
3. Insight menjadi lebih natural karena pengguna dapat membaca konteks fisik, bukan hanya kode meter.

---

# 3. Improvement Berdasarkan OSEMN

# 3.1 O - Obtain

## Kondisi Saat Ini

Obtain sudah cukup untuk proposal dan memo:

- HKUST dataset lokal tersedia.
- HKO Open Data sudah diunduh.
- Profil file HKUST dan HKO sudah dibuat.
- Raw dan processed data sudah dipisahkan.

## Gap

1. TTL baru diprofilkan secara kasar, belum dibuat menjadi tabel entity.
2. Manifest dataset belum disambungkan ke output final Power BI.
3. Belum ada daftar final file mana yang menjadi sumber resmi untuk dashboard.

## Improvement yang Direkomendasikan

| Prioritas | Improvement | Dampak |
|---|---|---|
| P0 | Tetapkan daftar canonical input untuk final analysis | Menghindari kebingungan antara raw, clean, processed, dan sample |
| P0 | Buat inventory final sumber Power BI | Memudahkan dokumentasi dan reproducibility |
| P1 | Parse TTL menjadi entity lookup | Membuat dashboard dan interpretasi jauh lebih kuat |
| P1 | Tambahkan data dictionary untuk semua dataset final | Membantu laporan dan presentasi |

## Output yang Ditargetkan

| Output | Isi |
|---|---|
| `dataset/processed/dim_entity.csv` | Mapping meter/entity dari TTL |
| `dataset/processed/data_dictionary_energy_dashboard.csv` | Definisi kolom final |
| `dataset/profile_hkust_hko/final_data_sources.md` | Sumber resmi dataset final |

## Acceptance Criteria

1. Semua dataset final punya sumber, periode, format, dan fungsi yang jelas.
2. TTL tidak lagi hanya disebut sebagai metadata, tetapi punya output tabel yang dapat digunakan.
3. Jika mapping TTL parsial, status mapping harus dicatat dengan `mapping_status`.

---

# 3.2 S - Scrub

## Kondisi Saat Ini

Scrub sudah melakukan:

- parse HKO CSV;
- parse HKUST T1440 Excel;
- normalisasi tanggal;
- hitung `daily_consumption` dengan differencing;
- join energi dan cuaca berdasarkan `date`;
- feature engineering awal.

## Gap

1. Meter nol konstan belum dikeluarkan atau diberi flag eksplisit pada dataset final.
2. Meter coverage pendek belum dipisahkan dari analisis utama.
3. Missing HKO masih dipertahankan, tetapi belum ada strategi final untuk modelling.
4. Nilai konsumsi hasil differencing belum diberi quality flag lengkap.
5. Dataset belum dibentuk sebagai star schema untuk Power BI.

## Improvement yang Direkomendasikan

| Prioritas | Improvement | Dampak |
|---|---|---|
| P0 | Tambahkan `meter_quality_flag` | Membedakan active, zero_constant, near_zero, short_coverage, incomplete |
| P0 | Tambahkan `data_quality_flag` pada fact table | Dashboard bisa membedakan anomaly model vs masalah data |
| P0 | Terapkan coverage threshold | Model tidak bias oleh meter yang tidak lengkap |
| P1 | Buat treatment missing HKO eksplisit | Model lebih stabil dan dapat dijelaskan |
| P1 | Buat table `dim_date` | Power BI lebih rapi untuk filter waktu |
| P1 | Buat normalized Power BI tables | Dashboard lebih mudah dikelola |

## Rule yang Direkomendasikan

| Kasus | Treatment |
|---|---|
| Hari pertama per meter | `daily_consumption = null`, flag `first_reading` |
| Differencing negatif | Set null, flag `negative_diff` |
| Meter nol konstan | Exclude dari model utama, tetap tampil pada data quality |
| Meter hampir nol | Exclude dari ranking konsumsi utama, tetap tampil pada data quality |
| Coverage pendek | Jangan dipakai untuk tren full-period tanpa flag |
| Missing rainfall/solar | Imputasi ringan untuk model atau drop pada model rows, tetapi tampilkan missing pada data quality |

## Output yang Ditargetkan

| Output | Isi |
|---|---|
| `fact_energy_weather_daily.csv` | Konsumsi harian + cuaca + quality flag |
| `dim_date.csv` | Kalender, weekday/weekend, bulan, kuartal |
| `dim_entity.csv` | Meter/entity metadata dari TTL dan fallback |
| `data_quality_summary.csv` | Ringkasan missing, excluded meter, coverage |

## Acceptance Criteria

1. Semua baris model dapat ditelusuri status kualitas datanya.
2. Meter bermasalah tidak diam-diam memengaruhi ranking dan model.
3. Treatment missing value dijelaskan di laporan.

---

# 3.3 E - Explore

## Kondisi Saat Ini

EDA sudah mencakup:

- tren konsumsi harian agregat;
- scatter konsumsi vs suhu;
- korelasi energi-cuaca;
- profil hourly T60 sample;
- statistik deskriptif dataset gabungan.

## Gap

1. EDA masih dominan agregat total, belum cukup per meter/entity.
2. Belum ada contribution analysis yang menunjukkan dominasi top meter.
3. Belum ada visual data quality yang menjelaskan meter nol, hampir nol, dan coverage pendek.
4. Belum ada case study hari anomali yang menggabungkan konsumsi, cuaca, dan quality flag.
5. Belum ada eksplorasi yang langsung mendukung desain dashboard Power BI.

## Improvement yang Direkomendasikan

| Prioritas | Improvement | Dampak |
|---|---|---|
| P0 | Contribution analysis per meter | Membuktikan top meter mendominasi konsumsi |
| P0 | EDA data quality | Membuat keterbatasan dataset transparan |
| P0 | Weekday/weekend dan monthly pattern | Mendukung insight operasional |
| P1 | Weather context per anomaly day | Membantu interpretasi, bukan sekadar korelasi |
| P1 | Entity scorecard | Menjadi dasar ranking dashboard |
| P2 | T60 hourly sample sebagai appendix | Menambah kedalaman tanpa mengubah main scope |

## Visual EDA yang Disarankan

| Visual | Tujuan |
|---|---|
| Daily total consumption with quality markers | Melihat tren sekaligus kualitas data |
| Top meter contribution bar | Menunjukkan konsentrasi konsumsi |
| Pareto chart contribution | Menjelaskan top 5 meter sekitar 66% |
| Weekday vs weekend boxplot | Membaca pola operasional |
| Monthly trend line | Membaca seasonal pattern |
| Weather vs consumption scatter | Memberi konteks cuaca |
| Data quality matrix | Menunjukkan meter aktif, nol, missing, coverage |
| Anomaly case table | Menjelaskan beberapa hari penting secara naratif |

## Output yang Ditargetkan

| Output | Isi |
|---|---|
| `outputs/eda/final_*` | Visual EDA final untuk laporan |
| `entity_scorecard.csv` | Ranking entity berdasarkan konsumsi, anomaly, dan quality |
| `anomaly_case_review.csv` | Tabel hari/entity anomali untuk interpretasi |

## Acceptance Criteria

1. EDA menjawab rumusan masalah, bukan hanya menampilkan grafik.
2. Setiap visual punya interpretasi singkat.
3. EDA menyiapkan bahan langsung untuk Bab Explore dan Power BI.

---

# 3.4 M - Model

## Kondisi Saat Ini

Model awal:

- IQR anomaly flag pada total konsumsi;
- Z-score konsumsi harian;
- Isolation Forest dengan `contamination=0.08`;
- baseline linear regression dengan R2 rendah pada agregat total.

## Gap

1. Isolation Forest belum menggunakan skenario `strict`, `balanced`, `sensitive`.
2. `anomaly_score` belum diekspor.
3. Feature set belum memasukkan konsumsi sebagai sinyal utama.
4. Model masih level agregat, belum siap untuk per meter/entity.
5. Evaluasi tanpa label belum distrukturkan.

## Improvement yang Direkomendasikan

| Prioritas | Improvement | Dampak |
|---|---|---|
| P0 | Scenario-based Isolation Forest | Dashboard dapat eksplorasi sensitivitas model |
| P0 | Export `anomaly_score` dan `anomaly_flag` | Power BI bisa menampilkan ranking anomali |
| P0 | Masukkan fitur konsumsi ke model | Model benar-benar mendeteksi pola konsumsi tidak biasa |
| P0 | Bandingkan dengan IQR/Z-score | Hasil lebih defensible untuk laporan |
| P1 | Model per meter aktif | Lebih fair dibanding total agregat |
| P1 | Stability check antar scenario | Menghindari interpretasi berlebihan |
| P2 | Forecasting optional | Hanya jika waktu cukup, sebagai model pendukung |

## Feature Set Final yang Disarankan

| Kelompok | Fitur |
|---|---|
| Konsumsi | `daily_consumption`, rolling mean 7 hari, rolling std 7 hari, deviation from rolling mean |
| Kalender | `is_weekend`, `weekday`, `month` |
| Cuaca | `mean_temperature_c`, `relative_humidity_pct`, `rainfall_mm`, `global_solar_radiation_mj_m2`, `mean_wind_speed_kmh` |
| Engineered weather | `cooling_degree_day_24c`, `is_rainy_day`, `is_hot_day_28c` |
| Data quality | jangan dipakai sebagai fitur utama; pakai untuk filter dan interpretasi |

## Isolation Forest Scenario

| Scenario | Contamination | Tujuan |
|---|---:|---|
| `strict` | 0.03 | Menangkap anomali paling ekstrem |
| `balanced` | 0.05 | Default untuk laporan dan dashboard |
| `sensitive` | 0.10 | Eksplorasi kandidat anomali lebih luas |

Parameter default:

| Parameter | Nilai |
|---|---|
| `n_estimators` | 100 |
| `random_state` | 42 |
| `max_samples` | `auto` |

## Evaluasi Tanpa Label

| Evaluasi | Tujuan |
|---|---|
| Volume sanity check | Apakah jumlah anomali sesuai contamination |
| Agreement IQR/Z-score | Apakah kasus ekstrem juga tertangkap baseline |
| Visual inspection | Apakah marker anomali masuk akal pada tren |
| Scenario stability | Apakah anomali penting tetap muncul lintas scenario |
| Case review | Apakah hari anomali bisa dijelaskan dengan data energi, cuaca, dan quality |

## Output yang Ditargetkan

| Output | Isi |
|---|---|
| `fact_anomaly_scenarios.csv` | Output model untuk Power BI |
| `model_evaluation_summary.csv` | Ringkasan jumlah anomali, agreement, dan stability |
| `anomaly_case_review.csv` | Contoh kasus untuk laporan |

## Acceptance Criteria

1. Model tidak membutuhkan label anomaly.
2. Output model siap dipakai di Power BI.
3. Hasil model dapat dijelaskan dengan baseline dan contoh kasus.
4. Anomali data quality tidak dicampur dengan anomali konsumsi tanpa catatan.

---

# 3.5 N - iNterpret

## Kondisi Saat Ini

Interpretasi awal sudah ada, tetapi masih umum:

- integrasi HKO berhasil;
- kualitas data meter perlu dikontrol;
- hubungan cuaca agregat masih lemah;
- model baseline agregat belum kuat.

## Gap

1. Insight belum spesifik ke entity prioritas.
2. Rekomendasi belum dikaitkan dengan dashboard dan model final.
3. Belum ada prioritas tindakan berdasarkan konsumsi, anomaly rate, dan data quality.
4. Belum ada narasi yang membedakan hasil teknis dengan keputusan operasional.

## Improvement yang Direkomendasikan

| Prioritas | Improvement | Dampak |
|---|---|---|
| P0 | Buat insight template berbasis bukti | Laporan lebih mudah dinilai |
| P0 | Buat recommendation matrix | Rekomendasi tidak generik |
| P0 | Pisahkan insight data, model, dan dashboard | Struktur interpretasi lebih rapi |
| P1 | Buat priority score entity | Mengubah analisis menjadi daftar tindak lanjut |

## Template Insight Final

Setiap insight sebaiknya mengikuti pola:

1. **Temuan:** apa yang terlihat pada data.
2. **Bukti:** angka, visual, atau tabel pendukung.
3. **Makna:** kenapa temuan penting untuk efisiensi energi.
4. **Batasan:** apa yang belum bisa disimpulkan.
5. **Tindakan:** rekomendasi atau investigasi lanjutan.

## Rekomendasi yang Ditargetkan

| Rekomendasi | Dasar Data | Sasaran |
|---|---|---|
| Audit meter/entity dengan konsumsi dan anomaly rate tinggi | Entity scorecard | Pengelola gedung |
| Review operasi weekend atau hari anomali | Trend + anomaly explorer | Sarana prasarana |
| Pisahkan meter bermasalah dari evaluasi efisiensi | Data quality table | Tim data |
| Gunakan dashboard untuk monitoring berkala | Power BI dashboard | Manajemen fasilitas |
| Lanjutkan mapping TTL untuk interpretasi gedung/zona | dim_entity | Tim analitik |

## Acceptance Criteria

1. Minimal 3 insight kuat tersedia.
2. Minimal 3 rekomendasi spesifik tersedia.
3. Setiap rekomendasi punya dasar data dan pihak sasaran.
4. Keterbatasan model dan data disebutkan eksplisit.

---

# 4. Improvement React Dashboard

# 4.1 Data Model dan Delivery Format yang Disarankan

Gunakan star schema sederhana sebagai canonical processed CSV, lalu buat prebuilt JSON untuk React dashboard:

| Tabel | Grain | Isi |
|---|---|---|
| `fact_energy_weather_daily` | Date x entity | Konsumsi, cuaca, fitur kalender, quality flag |
| `fact_anomaly_scenarios` | Date x entity x scenario | Skor dan flag Isolation Forest |
| `dim_date` | Date | Kalender, bulan, tahun, weekday/weekend |
| `dim_entity` | Entity | Meter, building, floor, room/equipment, mapping status |
| `dim_scenario` | Scenario | strict, balanced, sensitive, contamination |

Relasi:

| From | To | Key |
|---|---|---|
| `fact_energy_weather_daily` | `dim_date` | `date` |
| `fact_energy_weather_daily` | `dim_entity` | `entity_id` |
| `fact_anomaly_scenarios` | `dim_date` | `date` |
| `fact_anomaly_scenarios` | `dim_entity` | `entity_id` |
| `fact_anomaly_scenarios` | `dim_scenario` | `scenario` |

Delivery React:

| JSON | Isi |
|---|---|
| `manifest.json` | Metadata build, date range, selected entities, limitation |
| `daily_trend.json` | Daily consumption trend and anomaly markers |
| `monthly_trend.json` | Monthly trend |
| `entity_daily.json` | Daily meter-level rows for filters |
| `anomalies.json` | Scenario-level anomaly rows |
| `dimensions.json` | Entity and scenario dimensions |
| `entity_scorecard.json` | Meter ranking and priority score |
| `anomaly_case_review.json` | Top anomaly case review |
| `data_quality_summary.json` | Quality summary |
| `model_evaluation_summary.json` | Scenario evaluation |
| `eda_summary.json` | EDA evidence |
| `insight_recommendation_matrix.json` | Evidence-backed insights and recommendations |

# 4.2 Halaman Dashboard Final

## Page 1 - Executive Overview

Tujuan:

Memberi ringkasan cepat kondisi energi dan anomali.

Visual:

- KPI total consumption
- KPI average daily consumption
- KPI peak consumption
- KPI anomaly count
- KPI anomaly rate
- line chart trend konsumsi
- bar chart top entity by consumption
- table top anomaly cases

## Page 2 - Consumption Trend

Tujuan:

Membaca pola konsumsi dari waktu ke waktu.

Visual:

- daily trend dengan marker anomali
- monthly trend
- weekday/weekend comparison
- matrix month x weekday
- tooltip cuaca dan data quality

## Page 3 - Anomaly Explorer

Tujuan:

Menelusuri hasil Isolation Forest.

Visual:

- scatter consumption vs anomaly score
- table anomaly detail
- anomaly count by entity
- anomaly count by month
- comparison strict vs balanced vs sensitive

## Page 4 - Weather Impact

Tujuan:

Menjelaskan konteks cuaca tanpa klaim kausal berlebihan.

Visual:

- consumption vs temperature
- consumption vs rainfall
- consumption and temperature over time
- hot/rainy anomaly days table
- weather feature summary

## Page 5 - Meter / Building Ranking

Tujuan:

Menentukan prioritas audit.

Visual:

- ranked bar total consumption
- ranked bar anomaly rate
- entity scorecard table
- conditional formatting by month/entity
- quality flag by entity

## Page 6 - Data Quality and Methodology

Tujuan:

Menjelaskan keandalan data dan metode.

Visual:

- missing value KPI
- active meter count
- excluded meter list
- data completeness chart
- OSEMN pipeline summary
- source table

# 4.3 Filter Wajib

| Filter | Kegunaan |
|---|---|
| Date range | Filter periode |
| Scenario | Pilih strict, balanced, sensitive |
| Anomaly flag | Tampilkan normal/anomali |
| Entity | Filter meter/building/floor jika tersedia |
| Entity type | Kampus, meter, building, floor/equipment |
| Weekday/weekend | Pisahkan hari kerja dan akhir pekan |
| Rainy day/hot day | Konteks cuaca |
| Data quality flag | Pisahkan data valid dan bermasalah |

# 4.4 Frontend Metrics Minimum

| Metric | Definisi |
|---|---|
| `Total Consumption` | Sum daily consumption |
| `Average Daily Consumption` | Average daily consumption |
| `Peak Daily Consumption` | Max daily consumption |
| `Active Entity Count` | Distinct count entity valid |
| `Anomaly Count` | Count anomaly flag = 1 |
| `Anomaly Rate` | Anomaly count / total observation |
| `Average Anomaly Score` | Average anomaly score |
| `Data Quality Issue Count` | Count row dengan quality issue |
| `Rainy Day Count` | Count rainy days |
| `Hot Day Count` | Count hot days |

# 4.5 React Dashboard Design Principle

1. Fokus pada decision support, bukan dekorasi.
2. KPI di atas, tren dan ranking di tengah, detail tabel di bawah.
3. Warna anomali harus konsisten di semua halaman.
4. Gunakan tooltip untuk konteks cuaca dan quality flag.
5. Jangan menyembunyikan data quality issue.
6. Default scenario dashboard adalah `balanced`.
7. Dashboard harus responsif untuk desktop dan mobile.
8. Dashboard harus deployable ke Vercel dari `web/dist`.

---

# 5. Prioritas Implementasi

## P0 - Wajib untuk Nilai Maksimal

| No | Improvement | Alasan |
|---|---|---|
| 1 | Buat data quality flag per meter dan per hari | Mengontrol bias dari meter nol/coverage pendek |
| 2 | Buat `dim_entity` dari TTL atau fallback | Membuat analisis punya konteks fisik |
| 3 | Buat `fact_anomaly_scenarios` | Output utama untuk anomaly dashboard |
| 4 | Jalankan Isolation Forest 3 scenario | Model lebih defensible dan interaktif |
| 5 | Buat entity scorecard | Menghasilkan rekomendasi audit yang konkret |
| 6 | Buat React dashboard dengan filters dan metrics | Memastikan dashboard bukan sekadar grafik statis |

## P1 - Sangat Disarankan

| No | Improvement | Alasan |
|---|---|---|
| 1 | Parse relasi `brick:isMeteredBy` lebih dalam | Menghubungkan meter ke equipment |
| 2 | Tambahkan rolling features | Model menangkap deviasi historis |
| 3 | Buat anomaly case review | Memperkuat interpretasi |
| 4 | Tambahkan visual data quality | Membuat keterbatasan transparan |
| 5 | Buat data dictionary | Memperkuat dokumentasi |

## P2 - Opsional Jika Waktu Cukup

| No | Improvement | Alasan |
|---|---|---|
| 1 | T60 hourly sample analysis | Memberi kedalaman pola jam |
| 2 | Forecasting baseline | Menambah variasi modelling |
| 3 | Clustering entity | Menemukan kelompok pola konsumsi |
| 4 | React dashboard visual polish | Meningkatkan presentasi visual |

---

# 6. Roadmap Eksekusi Bertahap

## Milestone 1 - Data Foundation

Tujuan:

Membuat dataset final lebih bersih dan siap dashboard.

Task:

1. Buat `dim_entity` dari TTL dan fallback meter.
2. Buat `dim_date`.
3. Buat quality flag untuk meter dan tanggal.
4. Buat `fact_energy_weather_daily`.
5. Buat data dictionary.

Deliverable:

- `dim_entity.csv`
- `dim_date.csv`
- `fact_energy_weather_daily.csv`
- `data_quality_summary.csv`
- data dictionary

## Milestone 2 - Final EDA

Tujuan:

Menyediakan visual dan tabel eksplorasi yang langsung mendukung laporan.

Task:

1. Buat contribution analysis.
2. Buat weekday/weekend analysis.
3. Buat monthly trend.
4. Buat data quality visual.
5. Buat preliminary entity scorecard.

Deliverable:

- final EDA plots
- `entity_scorecard.csv`
- ringkasan insight awal

## Milestone 3 - Final Model

Tujuan:

Membuat anomaly detection yang kuat dan siap dashboard.

Task:

1. Buat feature set final.
2. Jalankan IQR dan Z-score baseline.
3. Jalankan Isolation Forest strict/balanced/sensitive.
4. Export anomaly score dan flag.
5. Buat evaluasi tanpa label.
6. Buat anomaly case review.

Deliverable:

- `fact_anomaly_scenarios.csv`
- `model_evaluation_summary.csv`
- `anomaly_case_review.csv`

## Milestone 4 - React Dashboard and Vercel Readiness

Tujuan:

Membangun dashboard React interaktif berdasarkan dataset final dan menyiapkannya untuk publish ke Vercel.

Task:

1. Buat script packaging CSV final menjadi JSON statis.
2. Buat Vite React app di `web/`.
3. Buat global filters untuk date, scenario, entity, anomaly flag, day type, weather, dan quality flag.
4. Buat 6 halaman dashboard.
5. Uji charts, tables, responsive layout, dan browser console.
6. Tambahkan Vercel config dan deployment guide.

Deliverable:

- React dashboard app
- `web/public/data/*.json`
- `vercel.json`
- Vercel deployment guide

## Milestone 5 - External Final Deliverables

Tujuan:

Mengunci hasil akhir untuk penilaian jika scope laporan, presentasi, atau demo diminta pada task terpisah. Bagian ini bukan scope implementasi repo pipeline/dashboard saat ini.

Task:

1. Update Bab Scrub dengan quality treatment.
2. Update Bab Explore dengan final visuals.
3. Update Bab Model dengan Isolation Forest scenario.
4. Update Bab Interpret dengan insight dan rekomendasi.
5. Buat narasi dashboard untuk presentasi.

Deliverable:

- laporan akhir OSEMN
- slide akhir
- script presentasi

Scope status:

- Out of scope untuk current cache-only alignment task.
- Out of scope untuk repo pipeline/dashboard implementation kecuali user meminta eksplisit.
- Tidak boleh menghalangi prioritas teknis: EDA final, model anomaly scenario, interpretation matrix, dan dashboard validation.

---

# 7. Risiko dan Mitigasi

| Risiko | Dampak | Mitigasi |
|---|---|---|
| T1440 hanya 26 meter | Representasi kampus terbatas | Jelaskan sebagai subset harian, gunakan TTL dan quality flag |
| Meter nol/hampir nol | Ranking dan model bias | Exclude dari model utama, tampilkan di data quality |
| `D0816` coverage pendek | Tren full-period bias | Flag short coverage dan jangan pakai untuk full-period comparison |
| TTL parsing tidak sempurna | Building/floor mapping parsial | Gunakan `mapping_status` dan fallback meter-level |
| Tidak ada label anomali | Evaluasi supervised tidak tersedia | Gunakan baseline, scenario stability, visual inspection, case review |
| Korelasi cuaca lemah pada agregat | Insight cuaca kurang kuat | Gunakan cuaca sebagai konteks, bukan klaim penyebab |
| Dashboard terlalu ramai | Sulit dipresentasikan | Prioritaskan 6 halaman dengan KPI, tren, anomali, cuaca, ranking, quality |

---

# 8. Acceptance Criteria Roadmap

Roadmap ini dianggap berhasil jika implementasi berikutnya memenuhi:

1. Semua tahap OSEMN punya improvement yang jelas.
2. Setiap improvement punya alasan, dampak, prioritas, dan output.
3. Dataset utama tetap HKUST, HKO tetap pendukung.
4. T1440 dan TTL menjadi scope utama yang konsisten.
5. Model anomaly tidak membutuhkan label.
6. Output model dapat dipakai langsung oleh Power BI.
7. Dashboard final dirancang sebagai alat eksplorasi interaktif.
8. Risiko utama dataset dan model tidak disembunyikan.
9. Hasil akhir mendukung minimal 3 insight dan 3 rekomendasi.

---

# 9. Ringkasan Keputusan Final

| Area | Keputusan |
|---|---|
| Target | Maksimal untuk nilai tugas besar |
| Scope data | T1440 harian + TTL metadata |
| Model utama | Isolation Forest anomaly detection |
| Baseline | IQR dan Z-score |
| Scenario model | strict 0.03, balanced 0.05, sensitive 0.10 |
| Dashboard | Power BI interaktif |
| Default dashboard scenario | balanced |
| TTL fallback | Jika mapping parsial, gunakan meter-level dan `mapping_status` |
| Output roadmap | Panduan implementasi, bukan perubahan pipeline langsung |

---

# 10. Next Action yang Paling Direkomendasikan

Urutan implementasi setelah roadmap ini:

1. Buat script `build_powerbi_datamart.py` untuk menghasilkan `dim_date`, `dim_entity`, `fact_energy_weather_daily`, dan `fact_anomaly_scenarios`.
2. Tambahkan quality flag dan exclusion logic untuk meter bermasalah.
3. Jalankan Isolation Forest 3 scenario dan ekspor `anomaly_score`.
4. Buat EDA final yang selaras dengan halaman dashboard.
5. Bangun Power BI dashboard dari fact/dimension tables.
6. Update laporan akhir OSEMN dengan hasil model, dashboard, insight, dan rekomendasi.
