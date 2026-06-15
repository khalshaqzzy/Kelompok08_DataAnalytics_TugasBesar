# Product Requirements Document

## Energy Efficiency Analytics: HKUST Smart Meter Anomaly Detection and React Dashboard

| Komponen | Keterangan |
|---|---|
| Nama produk analitik | Energy Efficiency Analytics Dashboard |
| Topik tugas besar | Energi dan Efisiensi Gedung/Kampus |
| Kerangka kerja | OSEMN: Obtain, Scrub, Explore, Model, iNterpret |
| Dataset utama | HKUST campus-level smart meter database |
| Dataset pendukung | Hong Kong Observatory Open Data |
| Model utama | Isolation Forest anomaly detection |
| Media visualisasi akhir | Standalone React dashboard interaktif yang dipublish ke Vercel |
| Pengguna sasaran | Pengelola gedung, sarana prasarana, manajemen kampus, tim sustainability, dosen/penilai |
| Versi dokumen | 1.2 |
| Tanggal | 2026-06-15 |

---

# Revision Notes v1.2

Update v1.2 mengganti target visualisasi final dari Power BI menjadi standalone React dashboard yang siap dipublish ke Vercel.

1. Dataset CSV final tetap menjadi canonical analytical output.
2. React dashboard memakai prebuilt JSON di `web/public/data` sebagai delivery format.
3. Power BI `.pbix` dan manual build guide dipertahankan sebagai historical/manual alternative, bukan target utama.
4. Target deploy baru adalah Vercel static deployment dari Vite React app di `web/`.
5. Enam halaman dashboard tetap dipertahankan: Executive Overview, Consumption Trend, Anomaly Explorer, Weather Impact, Meter Ranking, dan Data Quality and Methodology.

Supersession rule:

Setiap referensi lama ke Power BI, `.pbix`, DAX, atau Power BI Service di bagian historis dokumen ini harus dibaca sebagai keputusan yang sudah superseded oleh React dashboard target, kecuali bagian tersebut eksplisit menyebut historical/manual alternative.

---

# Revision Notes v1.1

Update v1.1 menyinkronkan PRD dengan `roadmap_improvement_energi_dashboard.md`. Perubahan utama:

1. Scope final dikunci ke **T1440 harian + TTL metadata**.
2. TTL diprioritaskan untuk membangun `dim_entity`, bukan hanya enhancement umum.
3. Data quality flag wajib mencakup meter nol konstan, hampir nol, dan coverage pendek.
4. Output Power BI dikunci sebagai star schema: `fact_energy_weather_daily`, `fact_anomaly_scenarios`, `dim_date`, `dim_entity`, dan `dim_scenario`.
5. Isolation Forest harus memasukkan fitur konsumsi dan rolling deviation, bukan hanya fitur cuaca dan kalender.
6. Acceptance criteria diperluas dengan entity scorecard dan anomaly case review.

---

# 1. Ringkasan Produk

Produk analitik ini dirancang untuk membantu pengelola kampus memahami pola konsumsi listrik, menemukan pemakaian tidak wajar, dan menentukan prioritas efisiensi energi berbasis data. Dataset utama berasal dari smart meter kampus HKUST, sedangkan data cuaca Hong Kong Observatory digunakan sebagai konteks pendukung untuk membaca perubahan konsumsi listrik harian.

Output akhir yang diharapkan bukan hanya laporan statistik, tetapi pipeline analitik yang dapat menghasilkan dataset siap visualisasi, flag anomali berbasis Isolation Forest, dan dashboard React interaktif yang bisa dipublish ke Vercel. Dashboard akan memungkinkan pengguna melihat tren konsumsi, membandingkan meter/gedung/zona, memfilter skenario anomaly detection, serta menelusuri hari atau meter yang perlu ditinjau lebih lanjut.

---

# 2. Latar Belakang dan Masalah

Kampus modern memiliki pola konsumsi energi yang kompleks karena aktivitas akademik, laboratorium, perkantoran, fasilitas umum, server, pencahayaan, dan pendinginan ruangan berjalan pada jadwal yang berbeda. Konsumsi listrik dapat meningkat karena faktor operasional normal, kondisi cuaca, atau kondisi yang perlu diperiksa seperti beban tinggi di luar jam aktivitas, meter dengan pola tidak stabil, dan lonjakan konsumsi yang tidak sesuai tren historis.

Masalah utama yang ingin diselesaikan:

1. Pengelola kampus membutuhkan cara cepat untuk melihat pola konsumsi listrik dari banyak meter.
2. Konsumsi tinggi belum tentu anomali; perlu konteks waktu, cuaca, dan pola historis.
3. Tanpa dashboard interaktif, analisis sulit dipakai untuk pemantauan dan pengambilan keputusan.
4. Dataset besar perlu diringkas menjadi pipeline yang reproducible dan sesuai OSEMN.

---

# 3. Tujuan Produk

Tujuan utama:

1. Menghasilkan dataset analitik gabungan energi dan cuaca yang bersih, terdokumentasi, dan siap dipakai.
2. Mendeteksi anomali konsumsi listrik menggunakan baseline statistik dan Isolation Forest.
3. Menyediakan dashboard React interaktif untuk memantau konsumsi, anomali, dan konteks cuaca.
4. Mendukung interpretasi dan rekomendasi efisiensi energi untuk pengguna non-teknis.
5. Memenuhi kebutuhan tugas besar Data Analitik berbasis OSEMN, termasuk tahap Model dan iNterpret.

Definisi sukses:

| Area | Kriteria sukses |
|---|---|
| Data | Dataset utama dan pendukung terhubung berdasarkan tanggal/waktu dengan dokumentasi sumber yang jelas |
| Model | Isolation Forest menghasilkan flag dan skor anomali tanpa membutuhkan label manual |
| Evaluasi | Hasil model dibandingkan dengan IQR/Z-score, dicek secara visual, dan dijelaskan keterbatasannya |
| Dashboard | Pengguna dapat memfilter periode, meter/gedung/zona, skenario model, dan status anomali |
| Interpretasi | Minimal 3 insight dan 3 rekomendasi efisiensi dapat diturunkan dari dashboard/analisis |
| Reproducibility | Pipeline dapat dijalankan ulang dari raw/clean data hingga output dashboard React |

---

# 4. Pengguna Sasaran

| Pengguna | Kebutuhan utama | Cara produk membantu |
|---|---|---|
| Tim sarana dan prasarana | Mengetahui konsumsi tinggi dan potensi pemborosan | Melihat tren, ranking konsumsi, dan flag anomali |
| Pengelola gedung | Memahami pola energi gedung/zona yang dikelola | Filter per meter, gedung, zona, dan periode |
| Manajemen kampus | Membaca ringkasan performa energi | KPI, tren bulanan, dan prioritas audit |
| Tim sustainability | Mendukung program efisiensi dan green campus | Insight konsumsi, cuaca, dan rekomendasi aksi |
| Dosen/penilai | Menilai penerapan data analytics | Dokumentasi OSEMN, model, evaluasi, dan interpretasi |
| Mahasiswa/analis | Melanjutkan eksplorasi dan modelling | Dataset processed, notebook, dan pipeline reproducible |

---

# 5. Sumber Data dan Scope

## 5.1 Dataset Utama: HKUST Smart Meter

Nama dataset:

**A 2.5-year campus-level smart meter database with equipment data for energy analytics**

Sumber:

- Dryad dataset: <https://doi.org/10.5061/dryad.k3j9kd5h6>
- Artikel Scientific Data: <https://doi.org/10.1038/s41597-024-04106-1>

Karakteristik:

| Aspek | Detail |
|---|---|
| Lokasi | Hong Kong University of Science and Technology, Sai Kung District, Hong Kong |
| Skala | Kampus |
| Jumlah meter | Lebih dari 1.400 smart meter |
| Jumlah gedung | Lebih dari 20 gedung |
| Periode | 2022-01-01 sampai 2024-05-27 |
| Format | `.xlsx` untuk time-series, `.ttl` untuk metadata Brick Schema |
| Interval | 15 menit, 30 menit, 1 jam, dan 1 hari setelah resampling |
| Peran | Dataset utama untuk konsumsi listrik, pola beban, ranking, dan anomali |

Dataset lokal:

- Raw time-series: 1.394 file `.xlsx`
- Clean T15: 403 file
- Clean T30: 645 file
- Clean T60: 255 file
- Clean T1440: 26 file
- Metadata: `HKUST_Meter_Metadata.ttl`

Scope final v1.1:

- **T1440 harian** menjadi main analytical table karena selaras dengan HKO daily weather.
- **TTL metadata** menjadi prioritas untuk entity mapping, minimal sampai level meter dan relasi fisik yang dapat diparse.
- T60 dipakai sebagai opsi eksplorasi pola jam, bukan basis utama dashboard final.

## 5.2 Metadata TTL

File `.ttl` bukan data konsumsi listrik. File ini adalah metadata berbasis Turtle/Brick Schema yang dapat berisi entity meter, equipment, zone, room, building, dan relasi antar entity.

Peran TTL dalam produk:

1. Menghubungkan `meter_id` ke konteks fisik seperti gedung/zona/equipment.
2. Mengaktifkan drill-down dashboard dari kampus ke gedung/zona/meter.
3. Membantu interpretasi anomali agar tidak berhenti pada ID meter saja.

Jika parsing TTL belum stabil, versi pertama dashboard tetap berjalan pada level kampus dan meter. Mapping gedung/zona menjadi enhancement prioritas.

Requirement v1.1:

TTL harus diupayakan menjadi `dim_entity`, minimal berisi:

| Kolom | Keterangan |
|---|---|
| `meter_id` | ID meter, misalnya `D0849` |
| `meter_name` | Nama entity meter dari TTL, misalnya `Meter_D0849` |
| `entity_type` | `meter`, `building`, `floor`, `room`, `equipment`, atau fallback |
| `building` | Nama building jika berhasil dipetakan |
| `floor` | Nama floor jika berhasil dipetakan |
| `room_or_equipment` | Room/equipment terkait jika berhasil dipetakan |
| `usage_type` | Usage type dari TTL jika tersedia |
| `mapping_status` | `mapped`, `partial`, atau `unmapped` |

## 5.3 Dataset Pendukung: HKO Weather

Sumber umum:

- Hong Kong Observatory Open Data: <https://www.weather.gov.hk/en/abouthko/opendata_intro.htm>

Dataset HKO yang digunakan:

| File lokal | Variabel | Stasiun | Peran |
|---|---|---|---|
| `skg_mean_temperature.csv` | `mean_temperature_c` | Sai Kung | Konteks suhu harian |
| `skg_max_temperature.csv` | `max_temperature_c` | Sai Kung | Kondisi panas maksimum |
| `skg_min_temperature.csv` | `min_temperature_c` | Sai Kung | Kondisi suhu minimum |
| `skg_relative_humidity.csv` | `relative_humidity_pct` | Sai Kung | Konteks kelembapan |
| `ksc_total_rainfall.csv` | `rainfall_mm` | Kau Sai Chau | Konteks hujan |
| `ksc_global_solar_radiation.csv` | `global_solar_radiation_mj_m2` | Kau Sai Chau | Konteks radiasi matahari |
| `skg_mean_wind_speed.csv` | `mean_wind_speed_kmh` | Sai Kung | Konteks angin |

HKO digunakan sebagai data pendukung, bukan dataset utama. Perannya adalah memperkaya interpretasi konsumsi listrik, terutama untuk melihat apakah anomali atau kenaikan beban mungkin berhubungan dengan cuaca.

---

# 6. Scope Produk

## 6.1 In Scope

1. Membuat dataset harian gabungan energi dan cuaca.
2. Membuat fitur waktu, fitur cuaca, dan indikator kualitas data.
3. Membuat baseline anomaly flag dengan IQR dan Z-score.
4. Membuat anomaly detection dengan Isolation Forest.
5. Membuat output model yang siap diload ke Power BI.
6. Mendesain dashboard Power BI interaktif.
7. Menyusun interpretasi, keterbatasan, dan rekomendasi efisiensi.
8. Menjaga struktur raw, processed, output, dan dokumentasi sesuai OSEMN.
9. Membuat data quality flag untuk meter nol konstan, hampir nol, coverage pendek, dan missing value.
10. Membuat entity scorecard untuk prioritas audit berbasis konsumsi, anomaly rate, dan kualitas data.

## 6.2 Out of Scope

1. Audit teknis HVAC secara langsung.
2. Integrasi live IoT atau streaming data real-time.
3. Perhitungan biaya listrik aktual jika tarif tidak tersedia.
4. Deployment dashboard ke Power BI Service sebagai sistem produksi.
5. Klaim kausal bahwa cuaca adalah penyebab tunggal kenaikan konsumsi.
6. Pelabelan manual anomali oleh ahli fasilitas sebagai ground truth.

---

# 7. Data Product Requirements

## 7.1 Dataset Processed Utama

Dataset processed minimum:

`dataset/processed/energy_weather_daily_sample.csv`

Shape saat ini:

- 878 baris
- 32 kolom
- Periode 2022-01-01 sampai 2024-05-27

Kolom utama:

| Kelompok | Kolom |
|---|---|
| Waktu | `date`, `weekday`, `is_weekend`, `month`, `year` |
| Energi | `meter_count`, `valid_daily_consumption_count`, `total_daily_consumption`, `mean_daily_consumption`, `median_daily_consumption`, `max_meter_daily_consumption`, `missing_daily_consumption_count` |
| Cuaca | `mean_temperature_c`, `max_temperature_c`, `min_temperature_c`, `relative_humidity_pct`, `rainfall_mm`, `global_solar_radiation_mj_m2`, `mean_wind_speed_kmh` |
| Kualitas | kolom `*_completeness` dari HKO |
| Feature engineering | `is_rainy_day`, `is_hot_day_28c`, `cooling_degree_day_24c` |
| Model awal | `zscore_total_daily_consumption`, `iqr_anomaly_flag`, `isolation_forest_anomaly` |

## 7.2 Output Model untuk Power BI

Dataset model final yang direkomendasikan:

`dataset/processed/energy_weather_anomaly_scenarios.csv`

Kolom minimum:

| Kolom | Tipe | Keterangan |
|---|---|---|
| `date` | date | Tanggal observasi |
| `entity_id` | string | ID analisis: kampus, meter, gedung, atau zona |
| `entity_type` | string | `campus`, `meter`, `building`, atau `zone` |
| `daily_consumption` | numeric | Konsumsi harian hasil differencing/agregasi |
| `meter_count` | numeric | Jumlah meter aktif pada agregasi |
| `valid_daily_consumption_count` | numeric | Jumlah konsumsi valid |
| `mean_temperature_c` | numeric | Suhu rata-rata harian |
| `relative_humidity_pct` | numeric | Kelembapan relatif harian |
| `rainfall_mm` | numeric | Curah hujan harian |
| `global_solar_radiation_mj_m2` | numeric | Radiasi matahari harian |
| `mean_wind_speed_kmh` | numeric | Kecepatan angin rata-rata |
| `weekday` | string | Nama hari |
| `is_weekend` | boolean/integer | Penanda akhir pekan |
| `is_rainy_day` | boolean/integer | Penanda hari hujan |
| `is_hot_day_28c` | boolean/integer | Penanda hari panas |
| `cooling_degree_day_24c` | numeric | Indikator kebutuhan pendinginan |
| `scenario` | string | `strict`, `balanced`, atau `sensitive` |
| `contamination` | numeric | Parameter proporsi anomali Isolation Forest |
| `anomaly_score` | numeric | Skor anomaly dari Isolation Forest |
| `anomaly_flag` | integer | 1 jika anomali, 0 jika normal |
| `iqr_anomaly_flag` | integer | Baseline IQR |
| `zscore_total_daily_consumption` | numeric | Baseline Z-score |
| `data_quality_flag` | string | Ringkasan kualitas data harian |

Catatan:

- Untuk versi awal, `entity_id` boleh bernilai `campus_total` jika mapping gedung/zona belum siap.
- Jika TTL berhasil dipakai, `entity_id` harus mendukung meter, building, dan zone.

## 7.3 Power BI Datamart Final

PRD v1.1 mengunci output final Power BI sebagai star schema sederhana.

| Tabel | Grain | Fungsi |
|---|---|---|
| `fact_energy_weather_daily` | Date x entity | Konsumsi harian, cuaca, fitur kalender, dan quality flag |
| `fact_anomaly_scenarios` | Date x entity x scenario | Skor dan flag Isolation Forest untuk strict, balanced, sensitive |
| `dim_date` | Date | Kalender, weekday/weekend, bulan, tahun, dan kuartal |
| `dim_entity` | Entity | Mapping meter/building/floor/room/equipment dari TTL atau fallback |
| `dim_scenario` | Scenario | Definisi scenario dan contamination |

Kolom quality flag minimum:

| Flag | Makna |
|---|---|
| `meter_quality_flag` | `active`, `zero_constant`, `near_zero`, `short_coverage`, `incomplete`, atau kombinasi ringkas |
| `data_quality_flag` | Status kualitas baris observasi untuk modelling dan dashboard |
| `is_model_eligible` | 1 jika boleh masuk model utama, 0 jika hanya untuk data quality/explanation |

Meter yang wajib diberi flag:

| Kategori | Meter |
|---|---|
| Nol konstan | `D0821`, `D0823`, `D0844`, `D0847` |
| Hampir nol | `D0846`, `D0864` |
| Coverage pendek | `D0816` |

---

# 8. Pipeline OSEMN

## 8.1 Obtain

Requirement:

1. Validasi keberadaan dataset HKUST lokal.
2. Validasi struktur folder raw, clean, T60, T1440, dan metadata TTL.
3. Download atau validasi 7 dataset HKO.
4. Simpan raw data terpisah dari processed data.
5. Dokumentasikan sumber, endpoint, periode, format, dan keterbatasan.

Output:

- Raw HKUST tetap di folder dataset Dryad.
- Raw HKO di `dataset/hko_open_data/raw/`.
- Manifest sumber HKO.
- Inventory dataset HKUST dan HKO.

## 8.2 Scrub

Requirement:

1. Parse file HKUST T1440 sebagai basis harian.
2. Normalisasi kolom `time` dan `number` menjadi tanggal dan meter reading.
3. Hitung `daily_consumption` dengan `diff()` per meter.
4. Tandai nilai negatif, nilai nol konstan, dan hari pertama per meter sebagai kasus khusus.
5. Parse HKO CSV menjadi `date`, variabel cuaca, dan completeness.
6. Filter semua dataset ke 2022-01-01 sampai 2024-05-27.
7. Join energi dan cuaca berdasarkan `date`.
8. Buat fitur kalender, cuaca, dan kualitas data.
9. Buat `meter_quality_flag`, `data_quality_flag`, dan `is_model_eligible`.
10. Exclude meter bermasalah dari model utama, tetapi tetap tampilkan pada halaman Data Quality.

Output:

- `dataset/processed/hkust_t1440_energy_long.csv`
- `dataset/processed/hko_weather_daily.csv`
- `dataset/processed/energy_weather_daily_sample.csv`
- `dataset/processed/fact_energy_weather_daily.csv`
- `dataset/processed/dim_entity.csv`
- `dataset/processed/dim_date.csv`

## 8.3 Explore

Requirement:

1. Statistik deskriptif energi dan cuaca.
2. Coverage dan missing value.
3. Tren konsumsi harian dan bulanan.
4. Perbandingan weekday vs weekend.
5. Korelasi energi dengan fitur cuaca.
6. Ranking meter/gedung/zona jika mapping tersedia.
7. Identifikasi kandidat meter bermasalah.
8. Contribution analysis untuk menunjukkan dominasi top meter.
9. Entity scorecard untuk prioritas audit.
10. Data quality visual untuk menjelaskan excluded/flagged meter.

Output visual minimum:

- Tren konsumsi harian.
- Scatter konsumsi vs suhu atau cooling degree day.
- Heatmap atau korelasi energi-cuaca.
- Ranking konsumsi per meter/gedung/zona.
- Visual data quality.

## 8.4 Model

Requirement:

1. Jalankan baseline IQR dan Z-score.
2. Jalankan Isolation Forest tanpa label.
3. Buat tiga skenario parameter: strict, balanced, sensitive.
4. Simpan skor dan flag model untuk Power BI.
5. Bandingkan hasil Isolation Forest dengan baseline statistik.
6. Dokumentasikan batasan evaluasi karena tidak ada ground truth.

Output:

- Dataset anomaly scenarios.
- Ringkasan jumlah anomali per skenario.
- Top anomaly days/entities.
- Evaluasi visual dan statistik.
- Entity scorecard.
- Anomaly case review.

## 8.5 iNterpret

Requirement:

1. Susun minimal 3 insight berbasis data.
2. Susun minimal 3 rekomendasi efisiensi yang bisa ditindaklanjuti.
3. Jelaskan keterbatasan data, model, dan dashboard.
4. Hubungkan insight ke pengguna sasaran.
5. Hindari klaim kausal berlebihan.

Output:

- Bagian interpretasi pada laporan akhir.
- Dashboard Power BI.
- Catatan rekomendasi prioritas audit.

---

# 9. Modelling Requirements

## 9.1 Problem Formulation

Tipe masalah:

**Unsupervised anomaly detection**

Target analitik:

Menandai hari, meter, gedung, atau zona yang memiliki pola konsumsi tidak biasa dibanding pola historisnya sendiri dan konteks waktu/cuaca.

Alasan tidak memakai supervised classification:

Dataset tidak menyediakan label resmi normal/anomali. Karena itu, model yang sesuai adalah unsupervised anomaly detection. Isolation Forest dapat bekerja tanpa label dengan mencari observasi yang lebih mudah diisolasi dari mayoritas data.

## 9.2 Feature Set

Fitur minimum:

| Kelompok | Fitur |
|---|---|
| Energi | `daily_consumption`, `mean_daily_consumption`, `median_daily_consumption`, `max_meter_daily_consumption`, rolling mean 7 hari, rolling std 7 hari, deviation from rolling mean |
| Coverage | `meter_count`, `valid_daily_consumption_count`, `missing_daily_consumption_count` |
| Kalender | `is_weekend`, `weekday`, `month`, `year` |
| Cuaca | `mean_temperature_c`, `relative_humidity_pct`, `rainfall_mm`, `global_solar_radiation_mj_m2`, `mean_wind_speed_kmh` |
| Engineered weather | `is_rainy_day`, `is_hot_day_28c`, `cooling_degree_day_24c` |

Fitur yang tidak boleh dipakai tanpa validasi:

- ID meter sebagai angka ordinal mentah.
- Kolom completeness sebagai angka tanpa encoding yang jelas.
- Nilai negatif hasil differencing yang belum diberi treatment.
- `data_quality_flag` sebagai fitur utama model; flag ini dipakai untuk filter dan interpretasi, bukan sinyal anomaly.

## 9.3 Baseline Model

Baseline diperlukan agar Isolation Forest tidak menjadi black box tunggal.

Baseline:

1. IQR outlier detection pada konsumsi harian.
2. Z-score pada konsumsi harian.

Output baseline:

- `iqr_anomaly_flag`
- `zscore_total_daily_consumption`

## 9.4 Isolation Forest Specification

Konfigurasi model:

| Scenario | `contamination` | Tujuan |
|---|---:|---|
| `strict` | 0.03 | Hanya menandai kasus paling ekstrem |
| `balanced` | 0.05 | Default untuk presentasi dan dashboard |
| `sensitive` | 0.10 | Eksplorasi lebih luas untuk mencari kandidat masalah |

Parameter default:

| Parameter | Nilai |
|---|---|
| `n_estimators` | 100 |
| `random_state` | 42 |
| `contamination` | sesuai scenario |
| `max_samples` | `auto` |

Output:

- `anomaly_score`
- `anomaly_flag`
- `scenario`
- `contamination`
- `is_model_eligible`

Catatan Power BI:

Power BI tidak digunakan untuk melatih Isolation Forest secara dinamis. Model dijalankan di Python, lalu output skenario diload ke Power BI. Pendekatan ini lebih stabil, reproducible, dan mudah dipresentasikan.

## 9.5 Evaluation Without Labels

Karena tidak ada label anomali resmi, evaluasi dilakukan dengan pendekatan berikut:

| Evaluasi | Tujuan |
|---|---|
| Agreement dengan IQR/Z-score | Melihat apakah anomali ekstrem juga tertangkap baseline |
| Visual inspection | Mengecek posisi anomaly flag pada grafik tren |
| Scenario stability | Membandingkan strict, balanced, sensitive |
| Volume sanity check | Memastikan jumlah flag tidak terlalu sedikit atau terlalu banyak |
| Domain interpretation | Menjelaskan apakah anomali masuk akal dari konsumsi, hari, dan cuaca |
| Case review | Mengambil beberapa tanggal anomali untuk dianalisis manual |

Model dianggap layak untuk tugas besar jika:

1. Output bisa dijelaskan secara naratif.
2. Hasil tidak hanya menandai semua peak biasa tanpa konteks.
3. Jumlah flag sesuai skenario.
4. Dashboard dapat memfilter dan menelusuri anomali.

---

# 10. React Dashboard Requirements

## 10.1 Tujuan Dashboard

Dashboard harus membantu pengguna menjawab:

1. Bagaimana tren konsumsi listrik kampus dari waktu ke waktu?
2. Kapan terjadi konsumsi tidak biasa?
3. Meter/gedung/zona mana yang paling sering atau paling besar anomali?
4. Apakah hari anomali berhubungan dengan cuaca, weekend, atau kualitas data?
5. Area mana yang perlu diprioritaskan untuk audit atau investigasi?

## 10.2 Data Tables and Delivery Format

Tabel minimum:

| Tabel | Isi | Sumber |
|---|---|---|
| `fact_energy_weather_daily` | Konsumsi harian + cuaca + fitur waktu | processed dataset |
| `fact_anomaly_scenarios` | Output Isolation Forest per scenario | Python model output |
| `dim_date` | Kalender, bulan, tahun, weekday/weekend | generated |
| `dim_entity` | Meter/building/zone metadata | TTL parsing atau fallback meter ID |
| `dim_scenario` | strict, balanced, sensitive | generated |

Delivery format untuk React:

| JSON | Isi | Sumber CSV |
|---|---|---|
| `manifest.json` | Metadata build, date range, limitation, selected entity count | generated |
| `daily_trend.json` | Aggregated daily trend | `fact_energy_weather_daily`, `fact_anomaly_scenarios` |
| `monthly_trend.json` | Aggregated monthly trend | `fact_energy_weather_daily` |
| `entity_daily.json` | Daily selected meter rows for filtering | `fact_energy_weather_daily` |
| `anomalies.json` | Scenario anomaly rows | `fact_anomaly_scenarios` |
| `dimensions.json` | Entity and scenario dimensions | `dim_entity`, `dim_scenario` |
| `entity_scorecard.json` | Ranking and priority score | `entity_scorecard` |
| `anomaly_case_review.json` | Top balanced anomaly cases | `anomaly_case_review` |
| `data_quality_summary.json` | Quality summary | `data_quality_summary` |
| `model_evaluation_summary.json` | Scenario model evaluation | `model_evaluation_summary` |
| `eda_summary.json` | EDA evidence summary | `eda_summary` |
| `insight_recommendation_matrix.json` | Insight/recommendation evidence | `insight_recommendation_matrix` |

Jika TTL belum berhasil diparse:

- `dim_entity` cukup berisi `entity_id`, `entity_type`, dan nama tampilan.
- Kolom building/zone boleh bernilai `Unknown` atau `Not mapped`.
- `mapping_status` wajib diisi agar keterbatasan entity mapping transparan.

## 10.3 Dashboard Pages

### Page 1: Executive Overview

Tujuan:

Memberi ringkasan cepat kondisi energi kampus.

Visual:

| Visual | Isi |
|---|---|
| KPI Card | Total consumption |
| KPI Card | Average daily consumption |
| KPI Card | Peak daily consumption |
| KPI Card | Anomaly count |
| KPI Card | Anomaly rate |
| Line chart | Tren konsumsi harian/bulanan |
| Bar chart | Top entities by consumption |
| Small summary table | Top anomaly days |

Slicer:

- Date range
- Entity type
- Scenario
- Anomaly flag

### Page 2: Consumption Trend

Tujuan:

Melihat perubahan konsumsi dan pola waktu.

Visual:

| Visual | Isi |
|---|---|
| Line chart | Daily consumption with anomaly marker |
| Column chart | Monthly consumption |
| Matrix/heatmap | Weekday vs month |
| Tooltip | Cuaca, anomaly score, data quality |

Slicer:

- Date range
- Meter/building/zone
- Weekday/weekend

### Page 3: Anomaly Explorer

Tujuan:

Menelusuri hasil Isolation Forest.

Visual:

| Visual | Isi |
|---|---|
| Scatter plot | Consumption vs anomaly score |
| Table | Date, entity, consumption, score, scenario, weather |
| Bar chart | Anomaly count by entity |
| Bar chart | Anomaly count by month |
| Line chart | Consumption with selected anomaly points |

Slicer:

- Scenario
- Contamination
- Anomaly flag
- Entity
- Date range

### Page 4: Weather Impact

Tujuan:

Melihat konteks cuaca pada konsumsi dan anomali.

Visual:

| Visual | Isi |
|---|---|
| Scatter plot | Consumption vs mean temperature |
| Scatter plot | Consumption vs rainfall |
| Line chart | Temperature and consumption over time |
| Correlation-style bar | Weather feature relation to consumption |
| Table | Hot/rainy anomaly days |

Slicer:

- Rainy day
- Hot day
- Date range
- Scenario

### Page 5: Meter / Building Ranking

Tujuan:

Menentukan prioritas audit energi.

Visual:

| Visual | Isi |
|---|---|
| Ranked bar chart | Highest total consumption |
| Ranked bar chart | Highest anomaly rate |
| Table | Entity scorecard |
| Conditional formatting matrix | Entity by month |

Slicer:

- Entity type
- Building/zone jika tersedia
- Date range
- Scenario

### Page 6: Data Quality and Methodology

Tujuan:

Menjelaskan kualitas data dan metode agar dashboard transparan.

Visual:

| Visual | Isi |
|---|---|
| KPI Card | Missing value count |
| KPI Card | Active meter count |
| Bar chart | Missing by variable |
| Table | Dataset sources |
| Text panel | OSEMN pipeline summary |

Slicer:

- Date range
- Dataset group

## 10.4 Required Frontend Metrics

React dashboard metrics minimum:

| Measure | Definisi |
|---|---|
| `Total Consumption` | Sum of daily consumption |
| `Average Daily Consumption` | Average daily consumption |
| `Peak Daily Consumption` | Max daily consumption |
| `Active Meter Count` | Distinct count or average valid meter count |
| `Anomaly Count` | Count rows where `anomaly_flag = 1` |
| `Anomaly Rate` | Anomaly count divided by total observations |
| `Average Anomaly Score` | Average anomaly score |
| `Rainy Day Count` | Count rainy days |
| `Hot Day Count` | Count hot days |
| `Missing Data Count` | Count missing or invalid values |
| `Model Eligible Count` | Count entity/date yang masuk model utama |
| `Excluded Meter Count` | Count meter dengan quality flag bermasalah |
| `Entity Priority Score` | Skor prioritas audit dari konsumsi, anomaly rate, dan quality status |

## 10.5 Interaction Requirements

Dashboard harus mendukung:

1. Global filtering by date, scenario, entity, anomaly flag, day type, weather context, and data quality flag.
2. Drill-down style comparison from selected building scope to meter-level detail.
3. Tooltip yang menampilkan cuaca dan anomaly score.
4. Scenario filter untuk membandingkan strict, balanced, sensitive.
5. Filter anomaly flag untuk melihat hanya hari/meter bermasalah.
6. Detail tables for top anomaly cases, scorecard, data quality, and model evaluation.
7. Responsive desktop and mobile layout.
8. Vercel static deployment from `web/dist`.

---

# 11. Non-Functional Requirements

| Area | Requirement |
|---|---|
| Reproducibility | Semua data dashboard berasal dari output script yang dapat dijalankan ulang |
| Traceability | Setiap dataset memiliki sumber dan periode yang jelas |
| Performance | React dashboard harus tetap responsif dengan data harian dan scenario model |
| Explainability | Model anomaly harus dijelaskan dengan baseline dan contoh kasus |
| Maintainability | Raw, processed, output, notebook, dan dokumen dipisahkan |
| Academic compliance | Struktur mengikuti OSEMN dan mencantumkan keterbatasan |

---

# 12. Acceptance Criteria

PRD dan implementasi akhir dianggap memenuhi kebutuhan jika:

1. Dataset utama adalah HKUST smart meter, sedangkan HKO hanya pendukung.
2. Dataset processed memiliki tanggal, konsumsi, cuaca, fitur waktu, dan indikator kualitas.
3. Isolation Forest dijalankan tanpa label, dengan tiga scenario parameter.
4. Output model memiliki `scenario`, `contamination`, `anomaly_score`, dan `anomaly_flag`.
5. Dashboard Power BI memiliki minimal 6 halaman sesuai spesifikasi.
6. Dashboard menyediakan slicer date range, scenario, anomaly flag, entity, weekend, rainy/hot day.
7. Dashboard dapat menunjukkan top anomaly days dan top entities.
8. Laporan akhir dapat menjelaskan evaluasi model tanpa ground truth.
9. Minimal 3 insight dan 3 rekomendasi dapat ditarik dari dashboard.
10. Keterbatasan data dan model dijelaskan secara eksplisit.
11. `dim_entity`, `dim_date`, `dim_scenario`, `fact_energy_weather_daily`, dan `fact_anomaly_scenarios` tersedia atau dijelaskan sebagai target final.
12. Meter nol konstan, hampir nol, dan coverage pendek diberi quality flag.
13. Dashboard memiliki entity scorecard untuk prioritas audit.
14. Minimal satu anomaly case review tersedia untuk menjelaskan hasil model secara naratif.

---

# 13. Risks and Mitigations

| Risiko | Dampak | Mitigasi |
|---|---|---|
| TTL sulit diparse | Dashboard belum bisa drill-down gedung/zona | Gunakan fallback per meter/kampus, jadikan TTL mapping sebagai enhancement |
| T1440 hanya 26 meter | Representasi kampus terbatas | Jelaskan sebagai subset harian, gunakan TTL dan quality flag; T60 hanya appendix/opsional |
| Tidak ada label anomali | Evaluasi supervised tidak bisa dilakukan | Gunakan baseline, visual inspection, scenario stability, dan case review |
| Cuaca berkorelasi lemah pada agregat | Insight cuaca terlihat kurang kuat | Analisis per meter/gedung/zona dan gunakan cuaca sebagai konteks, bukan penyebab tunggal |
| Power BI tidak melatih model real-time | Parameter tidak berubah langsung di dashboard | Precompute scenario strict/balanced/sensitive di Python |
| Meter nol konstan atau data tidak lengkap | Ranking dan model bisa bias | Tandai data quality flag dan exclude pada analisis final jika perlu |
| Top meter mendominasi konsumsi | Ranking dan insight terlalu dipengaruhi beberapa meter | Tambahkan contribution analysis dan entity scorecard |

---

# 14. Roadmap Implementasi

## Phase 1: Finalize Data Foundation

1. Validasi ulang processed dataset.
2. Buat dataset anomaly scenario untuk Power BI.
3. Tambahkan `entity_id` dan `entity_type`.
4. Buat data dictionary ringkas.
5. Buat `dim_entity`, `dim_date`, dan quality flags.
6. Buat `fact_energy_weather_daily`.

Deliverable:

- `energy_weather_anomaly_scenarios.csv`
- data dictionary
- `fact_energy_weather_daily.csv`
- `dim_entity.csv`
- `dim_date.csv`

## Phase 2: Modelling Final

1. Jalankan baseline IQR/Z-score.
2. Jalankan Isolation Forest strict, balanced, sensitive.
3. Simpan skor dan flag.
4. Buat ringkasan evaluasi.
5. Buat anomaly case review.
6. Buat entity scorecard.

Deliverable:

- model output CSV
- ringkasan model dan evaluasi
- `fact_anomaly_scenarios.csv`
- `anomaly_case_review.csv`
- `entity_scorecard.csv`

## Phase 3: Power BI Dashboard

1. Load fact dan dimension tables.
2. Buat measures.
3. Buat 6 halaman dashboard.
4. Uji slicer, tooltip, dan cross-filter.

Deliverable:

- file Power BI dashboard
- screenshot dashboard untuk laporan/presentasi

## Phase 4: Report and Presentation

1. Masukkan hasil modelling ke Bab Model.
2. Masukkan dashboard dan insight ke Bab iNterpret.
3. Susun rekomendasi akhir.
4. Siapkan narasi presentasi.

Deliverable:

- laporan akhir OSEMN
- slide akhir
- script presentasi

---

# 15. Rekomendasi Insight yang Ditargetkan

Insight akhir yang ditargetkan:

1. Pola konsumsi listrik kampus berubah menurut waktu, terutama weekday/weekend dan bulan tertentu.
2. Beberapa hari memiliki konsumsi tidak wajar yang tertangkap oleh Isolation Forest dan perlu ditinjau.
3. Coverage meter dan kualitas data memengaruhi interpretasi total konsumsi.
4. Cuaca memberi konteks tambahan, tetapi pengaruhnya perlu dibaca per meter/gedung, bukan hanya agregat kampus.
5. Prioritas efisiensi sebaiknya diarahkan ke entity dengan konsumsi tinggi, anomaly rate tinggi, dan data quality yang memadai.

Rekomendasi akhir yang ditargetkan:

1. Audit entity dengan anomaly rate tertinggi pada scenario balanced.
2. Review operasi beban malam atau weekend jika anomali muncul di luar pola aktivitas normal.
3. Pisahkan meter nol konstan atau incomplete dari analisis efisiensi final.
4. Gunakan dashboard sebagai alat monitoring berkala, bukan satu-satunya bukti teknis.
5. Lanjutkan parsing TTL agar rekomendasi bisa naik dari level meter ke gedung/zona/equipment.

---

# 16. Open Items

| Item | Status | Catatan |
|---|---|---|
| Parsing TTL ke building/zone | Belum final | Prioritas enhancement untuk dashboard lebih bermakna |
| Dataset anomaly scenarios | Perlu dibuat | Output utama untuk Power BI |
| Power BI `.pbix` | Belum dibuat | PRD ini menjadi spesifikasi dashboard |
| Model per gedung/zona | Bergantung TTL | Bisa fallback per meter/kampus |
| Validasi domain oleh fasilitas | Tidak tersedia | Gunakan evaluasi tanpa label |
| Datamart Power BI final | Perlu dibuat | Target: fact/dimension tables sesuai PRD v1.1 |
| Entity scorecard | Perlu dibuat | Target rekomendasi audit final |

---

# 17. Daftar Sumber

1. Li, M., Wang, Z., Qu, Y., Chui, K. M., & Leung-Shea, M. (2024). *A 2.5-year campus-level smart meter database with equipment data for energy analytics* [Dataset]. Dryad. <https://doi.org/10.5061/dryad.k3j9kd5h6>
2. Li, M., Wang, Z., Qu, Y., Chui, K. M., & Leung-Shea, M. (2024). *A multi-year campus-level smart meter database*. Scientific Data, 11, 1284. <https://doi.org/10.1038/s41597-024-04106-1>
3. Hong Kong Observatory. *Open Data*. <https://www.weather.gov.hk/en/abouthko/opendata_intro.htm>
