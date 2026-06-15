# Laporan Analisis Konsumsi Energi dan Deteksi Anomali Berbasis Smart Meter HKUST

## Daftar Isi

1. [Pendahuluan](#1-pendahuluan)  
   1.1 [Latar Belakang](#11-latar-belakang)  
   1.2 [Rumusan Masalah](#12-rumusan-masalah)  
   1.3 [Tujuan Analisis](#13-tujuan-analisis)  
   1.4 [Ruang Lingkup dan Batasan](#14-ruang-lingkup-dan-batasan)  
   1.5 [Pembagian Peran](#15-pembagian-peran)  
2. [O - Obtain: Akuisisi dan Seleksi Data](#2-o---obtain-akuisisi-dan-seleksi-data)  
   2.1 [Tujuan Tahap Obtain](#21-tujuan-tahap-obtain)  
   2.2 [Sumber Data](#22-sumber-data)  
   2.3 [Struktur Folder Data](#23-struktur-folder-data)  
   2.4 [Pemilihan Interval T1440](#24-pemilihan-interval-t1440)  
   2.5 [Pemilihan Subset Meter](#25-pemilihan-subset-meter)  
   2.6 [Akuisisi Data Cuaca HKO](#26-akuisisi-data-cuaca-hko)  
   2.7 [Integrasi Awal Energi dan Cuaca](#27-integrasi-awal-energi-dan-cuaca)  
   2.8 [Output Tahap Obtain](#28-output-tahap-obtain)  
   2.9 [Keterbatasan Tahap Obtain](#29-keterbatasan-tahap-obtain)  
3. [S - Scrub: Pembersihan, Validasi, dan Pembentukan Data Siap Analisis](#3-s---scrub-pembersihan-validasi-dan-pembentukan-data-siap-analisis)  
   3.1 [Tujuan Tahap Scrub](#31-tujuan-tahap-scrub)  
   3.2 [Status Tahap Scrub pada Dataset Analitis](#32-status-tahap-scrub-pada-dataset-analitis)  
   3.3 [Transformasi Data Energi](#33-transformasi-data-energi)  
   3.4 [Transformasi Data Cuaca](#34-transformasi-data-cuaca)  
   3.5 [Pembentukan Star Schema untuk Analisis](#35-pembentukan-star-schema-untuk-analisis)  
   3.6 [Validasi Kualitas Data](#36-validasi-kualitas-data)  
   3.7 [Feature Engineering Awal](#37-feature-engineering-awal)  
   3.8 [Output Tahap Scrub](#38-output-tahap-scrub)  
   3.9 [Catatan Kritis dan Batasan](#39-catatan-kritis-dan-batasan)  
4. [E - Explore](#4-e---explore)  
5. [M - Model](#5-m---model)  
6. [N - iNterpret](#6-n---interpret)  
7. [Kesimpulan dan Rekomendasi](#7-kesimpulan-dan-rekomendasi)  
8. [Lampiran](#8-lampiran)
   8.1 [Daftar Output Data Utama](#81-daftar-output-data-utama)  
   8.2 [Daftar Output Visual](#82-daftar-output-visual)  
   8.3 [Daftar Placeholder Gambar Manual](#83-daftar-placeholder-gambar-manual)  
   8.4 [Ringkasan Sumber](#84-ringkasan-sumber)  
   8.5 [Catatan Penggunaan Laporan](#85-catatan-penggunaan-laporan)

## 1. Pendahuluan

### 1.1 Latar Belakang

Konsumsi energi pada lingkungan kampus dipengaruhi oleh aktivitas akademik, operasional gedung, sistem pendingin, pencahayaan, laboratorium, lift, dan peralatan pendukung lainnya. Dalam lingkungan yang memiliki banyak titik pengukuran, data smart meter menjadi sumber penting untuk memahami pola konsumsi listrik dan menemukan kejadian yang tidak biasa.

Analisis ini menggunakan data smart meter kampus Hong Kong University of Science and Technology (HKUST) sebagai dataset utama dan data cuaca harian Hong Kong Observatory (HKO) sebagai dataset pendukung. Data energi digunakan untuk melihat pola konsumsi, kontribusi meter, dan kandidat anomali. Data cuaca digunakan sebagai konteks pembacaan, terutama suhu, kelembapan, curah hujan, radiasi matahari, dan kecepatan angin.

Fokus analisis diarahkan pada data harian T1440 karena granularitas tersebut sesuai dengan data cuaca harian. Hasil akhir analisis bukan hanya ringkasan statistik, tetapi juga dataset analitis yang siap digunakan untuk dashboard Vite React dan deteksi anomali berbasis Isolation Forest.

![Placeholder alur analisis OSEMN energi dan anomali](assets/laporan/gambar_01_alur_osemn_energi_anomali.png)

*Gambar 1. Placeholder alur analisis OSEMN dari akuisisi data, pembersihan, eksplorasi, pemodelan, interpretasi, hingga rancangan dashboard.*

### 1.2 Rumusan Masalah

Rumusan masalah dalam analisis ini adalah sebagai berikut:

1. Bagaimana memperoleh dan menyeleksi data smart meter HKUST serta data cuaca HKO agar dapat dianalisis secara konsisten?
2. Bagaimana membersihkan data energi dan cuaca sehingga terbentuk dataset harian yang valid, terdokumentasi, dan siap digunakan?
3. Bagaimana pola konsumsi listrik harian pada subset meter terpilih, termasuk tren waktu, perbedaan weekday dan weekend, kontribusi meter, serta konteks cuaca?
4. Bagaimana mendeteksi kandidat anomali konsumsi energi tanpa label ground truth?
5. Bagaimana hasil analisis dapat diterjemahkan menjadi insight, rekomendasi, dan dashboard Vite React interaktif?

### 1.3 Tujuan Analisis

Tujuan analisis ini adalah:

1. Menyusun dataset gabungan energi dan cuaca pada granularitas harian.
2. Menentukan subset meter yang layak digunakan sebagai fokus analisis utama.
3. Melakukan pembersihan, validasi, dan feature engineering untuk mendukung eksplorasi serta pemodelan.
4. Menjalankan deteksi anomali konsumsi listrik dengan baseline statistik dan Isolation Forest.
5. Menyusun insight dan rekomendasi berbasis bukti data.
6. Menyiapkan struktur data, data JSON statis, dan dashboard Vite React untuk visualisasi interaktif.

### 1.4 Ruang Lingkup dan Batasan

Analisis ini merupakan studi kasus selected daily meter-level, bukan klaim cakupan seluruh kampus HKUST. Cakupan utama adalah 12 meter aktif yang terpilih dari inventory T1440 dan terutama terhubung dengan `Cheng_Yu_Tung_Building`.

| Area | Ruang Lingkup |
|---|---|
| Dataset utama | Smart meter HKUST interval T1440 harian |
| Dataset pendukung | Data cuaca harian HKO |
| Periode analisis | 2022-01-02 sampai 2024-05-27 untuk fact energi-cuaca setelah differencing |
| Unit analisis utama | Date x entity_id, dengan entity_id berupa meter |
| Model utama | Isolation Forest anomaly detection tanpa label |
| Dashboard | Vite React dashboard di `web/` dengan data statis dari `web/public/data/*.json` |

Batasan utama:

1. Data T1440 hanya mencakup 26 meter harian, sehingga tidak mewakili seluruh meter HKUST.
2. Subset model utama memakai 12 meter aktif dari satu konteks gedung utama.
3. Data cuaca bersifat kontekstual, bukan bukti kausal tunggal terhadap konsumsi energi.
4. Tidak tersedia label anomali resmi, sehingga evaluasi model dilakukan dengan pendekatan tanpa ground truth.
5. Dashboard bersifat statis dan membaca prebuilt JSON; deployment produksi ke Vercel belum dilakukan dari CLI karena autentikasi Vercel lokal tidak valid.

### 1.5 Pembagian Peran

| Anggota | Peran | Tanggung Jawab Utama |
|---|---|---|
| Anggota 1 | Data Engineer | Akuisisi dataset, struktur folder data, validasi sumber, dan pengelolaan raw data |
| Anggota 2 | Data Preprocessing Lead | Pembersihan data, integrasi energi-cuaca, feature engineering, dan validasi kualitas data |
| Anggota 3 | Data Analyst / Modeler | Eksplorasi data, deteksi anomali, evaluasi model, dan interpretasi hasil model |
| Anggota 4 | Visualization / Dashboard Developer dan Documentation Lead | Rancangan dashboard, penyusunan insight, rekomendasi, dan laporan akhir |

## 2. O - Obtain: Akuisisi dan Seleksi Data

### 2.1 Tujuan Tahap Obtain

Tahap Obtain bertujuan memperoleh dataset yang relevan, memahami struktur sumber data, memilih granularitas analisis, dan memastikan data mentah tetap terpisah dari data hasil pemrosesan. Pada analisis ini, tahap Obtain juga mencakup seleksi meter karena dataset smart meter memiliki variasi kualitas dan cakupan.

### 2.2 Sumber Data

| Dataset | Sumber | Format | Peran dalam Analisis |
|---|---|---|---|
| HKUST smart meter | Dryad dataset: *A 2.5-year campus-level smart meter database with equipment data for energy analytics* | `.xlsx` untuk time-series, `.ttl` untuk metadata | Dataset utama konsumsi energi |
| Metadata HKUST | File Turtle berbasis Brick Schema | `.ttl` | Menghubungkan meter dengan gedung, lantai, ruang, atau equipment |
| HKO weather | Hong Kong Observatory Open Data | `.csv` | Dataset pendukung untuk konteks cuaca harian |

Dataset HKUST menyediakan data meter dengan beberapa granularitas waktu, sedangkan HKO menyediakan variabel cuaca harian. Kombinasi kedua sumber data memenuhi kebutuhan minimal dua sumber data dan memiliki dimensi waktu yang jelas.

![Placeholder ringkasan sumber data HKUST dan HKO](assets/laporan/gambar_02_sumber_data_hkust_hko.png)

*Gambar 2. Placeholder ringkasan dua sumber data utama, yaitu smart meter HKUST dan data cuaca HKO.*

### 2.3 Struktur Folder Data

Struktur data analitis dipisahkan menjadi data mentah, data hasil profil, data processed, dan output visual.

| Kelompok Folder | Isi | Fungsi |
|---|---|---|
| `Data_Acquisition/dataset/hkust_raw_data` | Data smart meter HKUST dan metadata TTL | Penyimpanan data energi mentah/awal |
| `Data_Acquisition/dataset/weather_raw_data` | CSV cuaca HKO | Penyimpanan data cuaca mentah |
| `Data_Acquisition/dataset/profile_hkust_hko` | Ringkasan sumber dan profil dataset | Dokumentasi sumber dan hasil profiling |
| `Data_Acquisition/dataset/processed` | Fact table, dimension table, output model, dan evidence table | Data siap analisis dan siap dashboard |
| `outputs/eda/final` | Visual eksplorasi final | Bukti visual untuk laporan dan rancangan dashboard |

Pemisahan ini penting agar alur analisis dapat ditelusuri dari sumber data ke output akhir tanpa mencampur data mentah dan hasil transformasi.

![Placeholder struktur folder dan alur file data](assets/laporan/gambar_03_struktur_folder_data.png)

*Gambar 3. Placeholder struktur folder data, mulai dari raw data, processed data, hingga output visual.*

### 2.4 Pemilihan Interval T1440

Interval T1440 dipilih sebagai basis utama karena merepresentasikan data harian. Pemilihan ini memiliki beberapa alasan:

1. Data cuaca HKO tersedia pada granularitas harian, sehingga T1440 dapat diintegrasikan langsung berdasarkan tanggal.
2. Analisis tugas besar berfokus pada pola konsumsi, anomali, dan dashboard, sehingga granularitas harian sudah memadai untuk ringkasan manajerial.
3. Data T1440 lebih ringan untuk diproses dibandingkan interval yang lebih kecil.
4. Deteksi anomali harian lebih mudah dijelaskan kepada pengguna non-teknis.

Konsekuensi dari keputusan ini adalah analisis tidak menangkap pola intraday seperti jam puncak, beban malam, atau variasi jam operasional. Pola tersebut dapat menjadi pengembangan lanjutan jika menggunakan data T60 atau interval yang lebih kecil.

### 2.5 Pemilihan Subset Meter

Inventory T1440 terdiri dari 26 meter. Dari jumlah tersebut, 12 meter dipilih sebagai subset utama karena aktif, memiliki coverage penuh, dan terhubung dengan konteks `Cheng_Yu_Tung_Building`.

| Kategori | Jumlah Meter | Keterangan |
|---|---:|---|
| Active | 18 | Meter aktif berdasarkan quality flag |
| Near-zero / low signal | 3 | Meter dengan sinyal konsumsi sangat rendah |
| Short coverage | 1 | Meter dengan cakupan waktu pendek |
| Zero constant | 4 | Meter dengan nilai konstan nol |
| Selected main subset | 12 | Meter yang digunakan sebagai fokus model utama |
| Comparison or secondary | 4 | Meter aktif tetapi tidak masuk subset model utama |
| Excluded from main model | 10 | Meter dikeluarkan dari model utama karena kualitas atau cakupan |

Meter selected main subset:

| Meter | Gedung | Peran Analitis |
|---|---|---|
| D0849 | Cheng_Yu_Tung_Building | Subset utama, kontribusi konsumsi tertinggi |
| D0848 | Cheng_Yu_Tung_Building | Subset utama |
| D0854 | Cheng_Yu_Tung_Building | Subset utama |
| D0853 | Cheng_Yu_Tung_Building | Subset utama |
| D0862 | Cheng_Yu_Tung_Building | Subset utama |
| D0857 | Cheng_Yu_Tung_Building | Subset utama |
| D0851 | Cheng_Yu_Tung_Building | Subset utama |
| D0861 | Cheng_Yu_Tung_Building | Subset utama |
| D0852 | Cheng_Yu_Tung_Building | Subset utama |
| D0860 | Cheng_Yu_Tung_Building | Subset utama |
| D0850 | Cheng_Yu_Tung_Building | Subset utama |
| D0865 | Cheng_Yu_Tung_Building | Subset utama |

Pemilihan subset ini menjaga kualitas analisis karena model tidak dilatih pada meter yang konstan nol, hampir nol, atau memiliki coverage pendek.

![Placeholder seleksi subset meter T1440](assets/laporan/gambar_04_seleksi_subset_meter_t1440.png)

*Gambar 4. Placeholder proses seleksi 26 meter T1440 menjadi 12 selected main subset.*

### 2.6 Akuisisi Data Cuaca HKO

Data cuaca HKO digunakan untuk melengkapi pembacaan konsumsi energi. Variabel yang digunakan adalah:

| Variabel | Stasiun | Kegunaan |
|---|---|---|
| Mean temperature | Sai Kung | Konteks suhu rata-rata harian |
| Maximum temperature | Sai Kung | Konteks panas maksimum |
| Minimum temperature | Sai Kung | Konteks suhu minimum |
| Relative humidity | Sai Kung | Konteks kelembapan |
| Total rainfall | Kau Sai Chau | Konteks hujan |
| Global solar radiation | Kau Sai Chau | Konteks radiasi matahari |
| Mean wind speed | Sai Kung | Konteks kecepatan angin |

Data HKO diproses menjadi satu tabel harian `hko_weather_daily.csv`. Missing value yang ditemukan pada periode proyek adalah 5 hari untuk rainfall dan 1 hari untuk global solar radiation.

### 2.7 Integrasi Awal Energi dan Cuaca

Integrasi awal dilakukan dengan menyamakan kolom tanggal. Data energi T1440 dinormalisasi menjadi konsumsi harian per meter, lalu digabungkan dengan data cuaca harian berdasarkan `date`.

Tahapan integrasi:

1. Membaca data meter harian.
2. Menormalisasi timestamp menjadi tanggal.
3. Menghitung konsumsi harian dari selisih meter reading.
4. Membaca data cuaca harian dan menormalisasi nama variabel.
5. Menggabungkan energi dan cuaca berdasarkan tanggal.
6. Menambahkan fitur kalender dan indikator cuaca.

### 2.8 Output Tahap Obtain

| Output | Isi |
|---|---|
| Inventory meter T1440 | Daftar 26 meter, quality flag, dan keputusan seleksi |
| Justifikasi subset | Alasan pemilihan 12 meter utama |
| Data cuaca harian | Tabel cuaca HKO harian terintegrasi |
| Data sumber final | Dokumentasi sumber, periode, dan batasan |

### 2.9 Keterbatasan Tahap Obtain

Keterbatasan utama pada tahap Obtain adalah cakupan T1440 yang terbatas pada 26 meter. Selain itu, data cuaca berasal dari stasiun HKO terdekat dan tidak mengukur kondisi mikro di dalam gedung. Oleh karena itu, hasil analisis harus dibaca sebagai studi kasus meter-level dengan konteks cuaca harian, bukan pengukuran lengkap seluruh kampus.

## 3. S - Scrub: Pembersihan, Validasi, dan Pembentukan Data Siap Analisis

### 3.1 Tujuan Tahap Scrub

Tahap Scrub bertujuan membersihkan data, mengubah format menjadi konsisten, menangani missing value, menandai kualitas data, dan membentuk tabel analitis yang siap digunakan untuk eksplorasi, model, dan rancangan dashboard.

### 3.2 Status Tahap Scrub pada Dataset Analitis

Tahap Scrub telah menghasilkan dataset analitis utama dengan grain `date x entity_id`. Dataset utama `fact_energy_weather_daily.csv` berisi 10.524 baris dan 62 kolom. Setiap baris merepresentasikan satu tanggal dan satu meter terpilih.

| Komponen | Status |
|---|---|
| Normalisasi data energi | Selesai |
| Normalisasi data cuaca | Selesai |
| Join energi-cuaca harian | Selesai |
| Pembuatan quality flag | Selesai |
| Feature engineering untuk model | Selesai |
| Star schema dashboard | Selesai sebagai CSV siap impor |

### 3.3 Transformasi Data Energi

Data energi awal berupa meter reading. Agar dapat dianalisis sebagai konsumsi harian, nilai konsumsi dihitung dengan differencing per meter.

Langkah transformasi:

1. Membaca file T1440 per meter.
2. Menormalisasi kolom waktu menjadi `date`.
3. Menormalisasi nilai pembacaan menjadi `meter_reading`.
4. Menghitung `daily_consumption` dari selisih pembacaan meter harian.
5. Menghapus atau menandai baris yang tidak layak, seperti pembacaan pertama yang belum memiliki nilai pembanding.
6. Menambahkan metadata meter dari hasil pemetaan entity.

Hasil akhir menunjukkan periode fact energi-cuaca dimulai pada 2022-01-02 karena tanggal pertama per meter tidak memiliki konsumsi hasil differencing.

![Placeholder transformasi meter reading menjadi konsumsi harian](assets/laporan/gambar_05_transformasi_konsumsi_harian.png)

*Gambar 5. Placeholder transformasi data energi dari meter reading menjadi daily consumption.*

### 3.4 Transformasi Data Cuaca

Data cuaca HKO memiliki struktur CSV yang perlu dinormalisasi. Setiap variabel cuaca diproses menjadi kolom numerik dan kolom completeness bila tersedia.

Transformasi utama:

1. Mengubah kolom tahun, bulan, dan hari menjadi `date`.
2. Mengubah nilai cuaca menjadi numerik.
3. Mempertahankan informasi completeness.
4. Membuat fitur cuaca:
   - `is_rainy_day`
   - `is_hot_day_28c`
   - `cooling_degree_day_24c`
5. Membuat field model-safe:
   - `rainfall_mm_model`
   - `global_solar_radiation_mj_m2_model`
6. Menambahkan indikator imputasi:
   - `rainfall_mm_was_imputed`
   - `global_solar_radiation_mj_m2_was_imputed`

Nilai rainfall yang hilang diisi dengan 0 pada field model-safe, sedangkan solar radiation yang hilang diisi menggunakan median bulanan. Nilai asli tetap dipertahankan untuk transparansi.

### 3.5 Pembentukan Star Schema untuk Analisis

Dataset disiapkan dalam struktur star schema sederhana sebagai output analitis utama. Struktur CSV ini menjadi sumber kanonik yang kemudian dikemas menjadi JSON statis untuk dashboard Vite React.

| Tabel | Grain | Jumlah Baris | Fungsi |
|---|---:|---:|---|
| `fact_energy_weather_daily.csv` | Date x entity | 10.524 | Konsumsi harian, cuaca, fitur kalender, dan quality flag |
| `fact_anomaly_scenarios.csv` | Date x entity x scenario | 31.260 | Skor dan flag anomali untuk tiga skenario |
| `dim_date.csv` | Date | 878 | Dimensi kalender |
| `dim_entity.csv` | Entity/meter | 26 | Metadata meter, quality flag, dan keputusan seleksi |
| `dim_scenario.csv` | Scenario | 3 | Definisi strict, balanced, dan sensitive |
| `entity_scorecard.csv` | Entity | 12 | Ranking prioritas audit |

Relasi yang dirancang:

| Tabel Fakta | Kolom | Tabel Dimensi | Kolom | Kardinalitas |
|---|---|---|---|---|
| fact_energy_weather_daily | date | dim_date | date | Many-to-one |
| fact_energy_weather_daily | entity_id | dim_entity | entity_id | Many-to-one |
| fact_anomaly_scenarios | date | dim_date | date | Many-to-one |
| fact_anomaly_scenarios | entity_id | dim_entity | entity_id | Many-to-one |
| fact_anomaly_scenarios | scenario | dim_scenario | scenario | Many-to-one |

![Placeholder star schema analitis](assets/laporan/gambar_06_star_schema_dashboard.png)

*Gambar 6. Placeholder rancangan star schema analitis, dengan fact table energi-cuaca dan fact table anomali sebagai sumber data dashboard.*

### 3.6 Validasi Kualitas Data

Validasi kualitas data dilakukan pada level meter, baris fact, dan output model. Ringkasan kualitas data adalah sebagai berikut:

| Area | Metrik | Nilai |
|---|---|---:|
| Meter quality | Active | 18 |
| Meter quality | Near-zero / low signal | 3 |
| Meter quality | Short coverage | 1 |
| Meter quality | Zero constant | 4 |
| Selection decision | Selected main subset | 12 |
| Selection decision | Comparison or secondary | 4 |
| Selection decision | Excluded from main model | 10 |
| Weather missing | Rainfall | 5 hari |
| Weather missing | Global solar radiation | 1 hari |
| Fact rows | fact_energy_weather_daily | 10.524 |
| Model eligible rows sebelum fitur rolling/lag lengkap | fact_energy_weather_daily | 10.524 |

Walaupun seluruh baris fact utama memenuhi syarat awal model, feature rolling dan lag menyebabkan jumlah baris feature-complete untuk model menjadi 10.420.

### 3.7 Feature Engineering Awal

Feature engineering digunakan untuk mendukung EDA, model, dan dashboard. Fitur yang dibuat dikelompokkan sebagai berikut:

| Kelompok Fitur | Contoh Kolom | Tujuan |
|---|---|---|
| Transformasi konsumsi | `log_daily_consumption`, percentile/rank konsumsi | Membantu pembacaan distribusi konsumsi |
| Rolling consumption | `rolling_mean_7d`, `rolling_std_7d`, `deviation_from_rolling_mean_7d` | Menilai penyimpangan dari pola terbaru |
| Lag consumption | `lag_1d_consumption`, `lag_7d_consumption`, `diff_from_lag_1d`, `diff_from_lag_7d` | Menangkap perubahan dari periode sebelumnya |
| Kalender | `is_weekend`, `month`, `day_of_week_num`, `is_month_start`, `is_month_end` | Menangkap pola waktu |
| Cuaca | `mean_temperature_c`, `rainfall_mm_model`, `temperature_band`, `rainfall_band` | Memberi konteks lingkungan |
| Readiness model | `feature_complete_flag`, `model_feature_set_version` | Menandai baris siap model |

Fitur rolling dan lag dihitung per `entity_id` dengan urutan waktu, sehingga tidak memakai informasi masa depan.

![Placeholder feature engineering energi cuaca](assets/laporan/gambar_07_feature_engineering_energi_cuaca.png)

*Gambar 7. Placeholder ringkasan feature engineering konsumsi, rolling, lag, kalender, dan cuaca.*

### 3.8 Output Tahap Scrub

Output utama tahap Scrub:

| Output | Keterangan |
|---|---|
| `fact_energy_weather_daily.csv` | Tabel utama konsumsi, cuaca, kalender, quality flag, dan fitur |
| `hko_weather_daily.csv` | Data cuaca harian hasil normalisasi |
| `dim_date.csv` | Dimensi tanggal |
| `dim_entity.csv` | Dimensi meter/entity |
| `dim_scenario.csv` | Dimensi skenario model |
| `data_quality_summary.csv` | Ringkasan kualitas data |
| `data_dictionary_energy_dashboard.csv` | Kamus data untuk output analitis |
| `feature_engineering_summary.csv` | Ringkasan fitur dan kelengkapan fitur |

### 3.9 Catatan Kritis dan Batasan

Catatan kritis tahap Scrub:

1. Meter dengan kualitas bermasalah tidak dihapus dari dimensi, tetapi tidak digunakan dalam model utama.
2. Missing value cuaca tidak dibuang; nilai asli dipertahankan dan field model-safe dibuat terpisah.
3. Data harian tidak dapat menjelaskan variasi konsumsi dalam satu hari.
4. Entity mapping cukup untuk meter-level dan gedung utama, tetapi interpretasi detail ruang/equipment tetap perlu kehati-hatian.

## 4. E - Explore

### 4.1 Tujuan Tahap Explore

Tahap Explore bertujuan memahami pola konsumsi energi, variasi waktu, kontribusi meter, kualitas data, dan konteks cuaca sebelum hasil model diinterpretasikan. Eksplorasi juga dipakai untuk menentukan visual yang relevan bagi dashboard Vite React.

### 4.2 Statistik Deskriptif Utama

Dataset utama berisi 10.524 baris observasi harian meter-level. Setelah fitur rolling dan lag diterapkan, 10.420 baris memiliki fitur lengkap untuk model. Pada level total harian selected meters, rata-rata konsumsi harian adalah 15.606,259 dengan nilai minimum 12.640 dan maksimum 17.400.

| Metrik | Nilai |
|---|---:|
| Baris fact energi-cuaca | 10.524 |
| Entity selected main subset | 12 |
| Hari analisis per selected meter | 877 |
| Rata-rata total konsumsi harian selected meters | 15.606,259 |
| Minimum total konsumsi harian selected meters | 12.640 |
| Maksimum total konsumsi harian selected meters | 17.400 |

### 4.3 Tren Konsumsi Harian

Tren harian menunjukkan bahwa konsumsi selected meters relatif stabil, tetapi tetap memiliki periode tinggi dan rendah yang layak ditinjau. Pada visual ini, tanggal dengan kandidat anomali pada skenario balanced diberi marker agar pola model dapat dibaca bersama tren konsumsi. Placeholder berikut dapat diisi menggunakan visual sumber `outputs/eda/final/daily_consumption_trend.png`.

![Placeholder tren konsumsi harian](assets/laporan/gambar_08_tren_konsumsi_harian.png)

Interpretasi: anomali tidak selalu identik dengan konsumsi paling tinggi secara absolut. Beberapa observasi dapat menjadi anomali karena menyimpang dari pola historis meter terkait, bukan hanya karena berada di puncak total konsumsi.

### 4.4 Tren Konsumsi Bulanan

Tren bulanan digunakan untuk melihat variasi konsumsi pada horizon yang lebih panjang. Nilai total bulanan tertinggi terjadi pada 2022-05, sedangkan nilai terendah terjadi pada 2024-05. Nilai 2024-05 perlu dibaca hati-hati karena periode data berakhir pada 2024-05-27, sehingga bulan tersebut tidak penuh. Placeholder berikut dapat diisi menggunakan visual sumber `outputs/eda/final/monthly_consumption_trend.png`.

![Placeholder tren konsumsi bulanan](assets/laporan/gambar_09_tren_konsumsi_bulanan.png)

Interpretasi: perbandingan bulanan perlu memperhatikan bulan parsial pada awal atau akhir periode. Visual bulanan tetap berguna untuk dashboard karena membantu manajemen melihat perubahan jangka menengah.

### 4.5 Perbandingan Weekday dan Weekend

Rata-rata total konsumsi harian weekday adalah 15.654,906, sedangkan weekend adalah 15.484,932. Selisih rata-rata weekday terhadap weekend adalah 169,973. Placeholder berikut dapat diisi menggunakan visual sumber `outputs/eda/final/weekday_weekend_consumption.png`.

![Placeholder perbandingan weekday dan weekend](assets/laporan/gambar_10_perbandingan_weekday_weekend.png)

Interpretasi: konsumsi weekday lebih tinggi dibanding weekend, konsisten dengan dugaan bahwa aktivitas operasional kampus lebih padat pada hari kerja. Namun, selisih ini bersifat deskriptif dan belum memasukkan jadwal operasional aktual.

### 4.6 Kontribusi Meter dan Pola Pareto

Analisis kontribusi menunjukkan bahwa konsumsi selected meters terkonsentrasi pada sejumlah kecil meter. Top 5 entity menyumbang sekitar 68,79% dari total konsumsi selected meters. Meter D0849 menjadi kontributor terbesar dengan kontribusi sekitar 20,62%. Placeholder berikut dapat diisi menggunakan visual sumber `outputs/eda/final/top_meter_contribution_pareto.png`.

![Placeholder kontribusi meter dan Pareto](assets/laporan/gambar_11_kontribusi_meter_pareto.png)

| Peringkat | Entity | Total Konsumsi | Kontribusi | Balanced Anomaly Count | Priority Score |
|---:|---|---:|---:|---:|---:|
| 1 | D0849 | 2.822.400 | 20,62% | 396 | 100,00 |
| 2 | D0848 | 2.053.420 | 15,00% | 59 | 52,57 |
| 3 | D0854 | 1.866.900 | 13,64% | 12 | 46,15 |
| 4 | D0853 | 1.774.050 | 12,96% | 8 | 43,07 |
| 5 | D0862 | 898.620 | 6,57% | 2 | 17,75 |

Interpretasi: meter dengan kontribusi tinggi perlu menjadi prioritas monitoring, tetapi kontribusi tinggi tidak otomatis berarti tidak efisien. Kontribusi harus dibaca bersama anomaly rate, peak consumption, fungsi equipment, dan kualitas data.

### 4.7 Konteks Cuaca terhadap Konsumsi

Korelasi sederhana antara total konsumsi harian dan mean temperature adalah 0,236087. Korelasi dengan rainfall adalah 0,138492. Nilai ini menunjukkan hubungan yang lemah sampai sedang, sehingga cuaca lebih tepat digunakan sebagai konteks daripada bukti kausal tunggal. Placeholder berikut dapat diisi menggunakan visual sumber `outputs/eda/final/weather_consumption_context.png`.

![Placeholder konteks cuaca terhadap konsumsi](assets/laporan/gambar_12_konteks_cuaca_konsumsi.png)

Interpretasi: suhu dan hujan dapat membantu membaca kondisi hari tertentu, terutama ketika suatu tanggal terdeteksi sebagai kandidat anomali. Namun, konsumsi gedung juga dipengaruhi jadwal penggunaan ruang, peralatan, dan operasi internal yang tidak tersedia dalam dataset.

### 4.8 Eksplorasi Kualitas Data

Visual kualitas data memperlihatkan quality flag pada level meter dan baris fact. Meter yang tidak dipakai dalam model utama tetap dicatat agar batas analisis transparan. Placeholder berikut dapat diisi menggunakan visual sumber `outputs/eda/final/data_quality_flags.png`.

![Placeholder kualitas data](assets/laporan/gambar_13_kualitas_data.png)

| Quality Flag | Jumlah Meter | Perlakuan |
|---|---:|---|
| active | 18 | Dapat dipertimbangkan untuk analisis |
| near_zero_low_signal | 3 | Tidak digunakan dalam model utama |
| short_coverage | 1 | Tidak digunakan dalam model utama |
| zero_constant | 4 | Tidak digunakan dalam model utama |

Pada baris fact utama terdapat 72 baris dengan isu kualitas karena imputasi cuaca. Baris tersebut tetap dapat digunakan dengan field model-safe, tetapi perlu ditampilkan pada halaman metodologi dashboard.

### 4.9 Ringkasan Temuan Eksploratif

| Area | Temuan | Implikasi |
|---|---|---|
| Tren harian | Konsumsi relatif stabil tetapi memiliki hari tinggi/rendah | Perlu visual trend dan marker anomali |
| Tren bulanan | Ada variasi antar bulan | Dashboard perlu filter bulan dan tahun |
| Weekday/weekend | Weekday rata-rata lebih tinggi 169,973 | Perlu slicer weekday/weekend |
| Kontribusi meter | Top 5 menyumbang sekitar 68,79% | Audit perlu memperhatikan bias kontribusi |
| Cuaca | Korelasi sederhana lemah sampai sedang | Cuaca digunakan sebagai konteks |
| Kualitas data | Meter bermasalah sudah ditandai | Dashboard perlu halaman metodologi |

### 4.10 Kesiapan Visual untuk Dashboard

Visual EDA yang sudah tersedia dapat dipetakan langsung ke halaman dashboard Vite React:

| Visual | Halaman Dashboard yang Didukung |
|---|---|
| `daily_consumption_trend.png` | Consumption Trend |
| `monthly_consumption_trend.png` | Consumption Trend |
| `weekday_weekend_consumption.png` | Consumption Trend |
| `top_meter_contribution_pareto.png` | Meter Ranking |
| `weather_consumption_context.png` | Weather Impact |
| `data_quality_flags.png` | Data Quality and Methodology |
| `anomaly_case_review.png` | Anomaly Explorer |

## 5. M - Model

### 5.1 Tujuan Tahap Model

Tahap Model bertujuan mendeteksi kandidat anomali konsumsi energi harian pada selected meters. Karena dataset tidak menyediakan label anomali resmi, pendekatan yang digunakan adalah unsupervised anomaly detection.

### 5.2 Formulasi Masalah

Masalah dimodelkan sebagai deteksi observasi yang tidak biasa pada kombinasi tanggal dan entity. Satu observasi dianggap kandidat anomali jika pola konsumsi dan fitur pendukungnya berbeda dari pola mayoritas observasi.

| Elemen | Definisi |
|---|---|
| Unit model | Date x entity_id |
| Target | Kandidat anomali konsumsi energi |
| Label ground truth | Tidak tersedia |
| Output model | `anomaly_score`, `anomaly_flag`, dan ranking anomali |
| Skenario utama dashboard | balanced |

### 5.3 Alasan Menggunakan Unsupervised Anomaly Detection

Supervised classification tidak digunakan karena tidak ada label historis yang menyatakan suatu observasi benar-benar normal atau anomali. Isolation Forest dipilih karena dapat mendeteksi observasi yang relatif mudah diisolasi dari mayoritas data tanpa label.

Model ini cocok untuk tujuan screening awal, yaitu menghasilkan daftar kandidat yang perlu ditinjau oleh pengelola gedung atau analis, bukan untuk membuat diagnosis teknis final.

### 5.4 Baseline Statistik: IQR dan Z-score

Baseline statistik digunakan agar hasil Isolation Forest tidak berdiri sendiri. Dua baseline yang digunakan adalah:

1. IQR anomaly flag, yaitu observasi di luar batas bawah atau atas berdasarkan kuartil per entity.
2. Z-score anomaly flag, yaitu observasi dengan nilai absolut Z-score minimal 3 pada konsumsi harian per entity.

Baseline ini membantu mengukur apakah kandidat model juga ekstrem secara statistik. Namun, baseline sederhana tidak selalu menangkap anomali multivariat karena hanya berfokus pada konsumsi.

### 5.5 Feature Set Model

Feature set model menggabungkan konsumsi, rolling pattern, lag, kalender, dan cuaca.

| Kelompok | Fitur |
|---|---|
| Konsumsi | `daily_consumption` |
| Rolling | `rolling_mean_7d`, `rolling_std_7d`, `deviation_from_rolling_mean_7d`, `pct_deviation_from_rolling_mean_7d` |
| Lag | `lag_1d_consumption`, `lag_7d_consumption`, `diff_from_lag_1d`, `diff_from_lag_7d` |
| Kalender | `is_weekend`, `month`, `day_of_week_num` |
| Cuaca | `mean_temperature_c`, `relative_humidity_pct`, `rainfall_mm_model`, `global_solar_radiation_mj_m2_model`, `mean_wind_speed_kmh` |
| Cuaca turunan | `cooling_degree_day_24c`, `is_rainy_day`, `is_hot_day_28c` |

Jumlah baris yang feature-complete untuk pemodelan adalah 10.420.

### 5.6 Isolation Forest

Isolation Forest dijalankan pada fitur numerik yang telah distandarkan. Model menggunakan parameter dasar:

| Parameter | Nilai |
|---|---|
| Model | Isolation Forest |
| n_estimators | 100 |
| max_samples | auto |
| random_state | 42 |
| contamination | Bergantung skenario |

Skor anomali diorientasikan agar nilai yang lebih tinggi berarti lebih anomali. Output disimpan dalam `fact_anomaly_scenarios.csv`.

![Placeholder alur pemodelan Isolation Forest](assets/laporan/gambar_14_alur_model_isolation_forest.png)

*Gambar 14. Placeholder alur pemodelan dari feature set, standardisasi, Isolation Forest, hingga anomaly score dan anomaly flag.*

### 5.7 Skenario Model

Tiga skenario digunakan agar pengguna dapat membandingkan sensitivitas model.

| Scenario | Contamination | Tujuan | Anomaly Count | Anomaly Rate |
|---|---:|---|---:|---:|
| strict | 0,03 | Menandai kasus paling ekstrem | 313 | 0,030038 |
| balanced | 0,05 | Default untuk dashboard dan presentasi | 521 | 0,050000 |
| sensitive | 0,10 | Menandai kandidat lebih luas | 1.042 | 0,100000 |

Skenario balanced dipakai sebagai default karena menghasilkan kandidat anomali yang cukup representatif tanpa terlalu banyak menandai observasi.

### 5.8 Evaluasi Tanpa Label Ground Truth

Karena tidak tersedia label anomali resmi, evaluasi dilakukan melalui beberapa pendekatan:

1. Sanity check jumlah anomali terhadap nilai contamination.
2. Perbandingan dengan baseline IQR dan Z-score.
3. Stabilitas kandidat antar skenario.
4. Case review pada kandidat anomali teratas.
5. Interpretasi domain berdasarkan konsumsi, pola rolling, kalender, cuaca, dan quality flag.

| Scenario | Eligible Rows | Anomaly Count | IQR Agreement | Z-score Agreement | Stable with Strict |
|---|---:|---:|---:|---:|---:|
| strict | 10.420 | 313 | 4 | 4 | 313 |
| balanced | 10.420 | 521 | 10 | 6 | 313 |
| sensitive | 10.420 | 1.042 | 24 | 12 | 313 |

Nilai agreement dengan baseline relatif kecil. Hal ini wajar karena Isolation Forest menggunakan fitur multivariat, sedangkan IQR dan Z-score hanya membaca ekstremitas konsumsi per entity. Dengan demikian, kandidat anomali dapat muncul karena kombinasi pola konsumsi, rolling deviation, kalender, dan cuaca, bukan hanya nilai konsumsi absolut.

![Placeholder evaluasi skenario model](assets/laporan/gambar_15_evaluasi_skenario_model.png)

*Gambar 15. Placeholder ringkasan evaluasi strict, balanced, dan sensitive, termasuk anomaly count dan baseline agreement.*

### 5.9 Anomaly Case Review

Anomaly case review berisi 20 kandidat teratas dari skenario balanced. Visual berikut menunjukkan deviasi kandidat anomali terhadap rolling mean terbaru. Placeholder berikut dapat diisi menggunakan visual sumber `outputs/eda/final/anomaly_case_review.png`.

![Placeholder anomaly case review](assets/laporan/gambar_16_anomaly_case_review.png)

Interpretasi utama: kandidat anomali yang kuat perlu dibaca berdasarkan deviasi dari pola terbaru, stabilitas lintas skenario, dan konteks cuaca. Kandidat yang muncul pada strict, balanced, dan sensitive lebih layak diprioritaskan dibanding kandidat yang hanya muncul pada sensitive.

### 5.10 Entity Scorecard

Entity scorecard menggabungkan total konsumsi, anomaly rate, peak load, dan kualitas data untuk menghasilkan prioritas audit. Entity D0849 menjadi prioritas tertinggi dengan `entity_priority_score` 100,00.

| Entity | Total Konsumsi | Balanced Anomaly Count | Balanced Anomaly Rate | Priority Rank |
|---|---:|---:|---:|---:|
| D0849 | 2.822.400 | 396 | 0,451539 | 1 |
| D0848 | 2.053.420 | 59 | 0,067275 | 2 |
| D0854 | 1.866.900 | 12 | 0,013683 | 3 |
| D0853 | 1.774.050 | 8 | 0,009122 | 4 |
| D0862 | 898.620 | 2 | 0,002281 | 5 |

Scorecard ini bukan diagnosis teknis, melainkan daftar prioritas screening awal untuk membantu pengguna memilih entity yang perlu ditinjau lebih dulu.

![Placeholder entity scorecard](assets/laporan/gambar_17_entity_scorecard_prioritas_audit.png)

*Gambar 17. Placeholder visual ranking entity scorecard untuk prioritas audit energi.*

### 5.11 Keterbatasan Model

Keterbatasan model:

1. Tidak ada ground truth, sehingga akurasi supervised tidak dapat dihitung.
2. Model menghasilkan kandidat anomali, bukan bukti final gangguan operasional.
3. Hasil model bergantung pada subset T1440 selected meters.
4. Fitur cuaca harian tidak menangkap kondisi ruang, jadwal kuliah, atau jam operasional.
5. Nilai contamination menentukan proporsi kandidat, sehingga interpretasi harus membandingkan skenario.

## 6. N - iNterpret

### 6.1 Tujuan Tahap iNterpret

Tahap iNterpret bertujuan menerjemahkan hasil eksplorasi dan model menjadi insight, rekomendasi, dan rancangan dashboard yang dapat dipahami pengguna non-teknis. Interpretasi harus tetap berbasis bukti dan tidak membuat klaim kausal berlebihan.

### 6.2 Prinsip Interpretasi

Prinsip interpretasi yang digunakan:

1. Menjelaskan hasil sebagai screening kandidat, bukan keputusan final.
2. Memisahkan konsumsi tinggi, anomali, dan efisiensi.
3. Membaca hasil model bersama konteks waktu, cuaca, dan kualitas data.
4. Menyatakan batasan subset selected meters secara eksplisit.
5. Mengarahkan rekomendasi kepada pengguna yang tepat.

### 6.3 Insight Utama

| No | Insight | Bukti | Implikasi |
|---:|---|---|---|
| 1 | Konsumsi selected meters terkonsentrasi pada sedikit entity | Top 5 entity menyumbang 68,79% konsumsi | Prioritas audit sebaiknya dimulai dari entity kontribusi tinggi |
| 2 | Weekday memiliki konsumsi rata-rata lebih tinggi daripada weekend | Selisih weekday-weekend sebesar 169,973 | Perlu filter kalender untuk membaca pola operasional |
| 3 | Skenario balanced menghasilkan kandidat anomali sesuai parameter 5% | 521 anomali dari 10.420 eligible rows | Balanced layak menjadi skenario default dashboard |
| 4 | Cuaca berguna sebagai konteks, tetapi korelasi sederhana tidak cukup untuk klaim kausal | Korelasi suhu 0,236087 dan rainfall 0,138492 | Cuaca ditampilkan sebagai filter dan tooltip pendukung |

### 6.4 Rekomendasi Prioritas

| No | Rekomendasi | Sasaran | Prioritas | Dasar |
|---:|---|---|---|---|
| 1 | Mulai audit dari entity prioritas tertinggi, terutama D0849 | Pengelola gedung | P0 | D0849 memiliki kontribusi dan anomaly count tertinggi |
| 2 | Gunakan skenario balanced sebagai default dashboard | Data analyst dan pengelola dashboard | P0 | Balanced menghasilkan anomaly rate 5% sesuai desain |
| 3 | Pertahankan halaman data quality agar batasan data transparan | Tim data | P0 | Meter excluded dan weather-imputed rows sudah dipisahkan |
| 4 | Prioritaskan kandidat yang stabil lintas skenario atau didukung baseline | Manajemen kampus | P1 | Stabilitas skenario meningkatkan keyakinan screening |
| 5 | Gunakan cuaca sebagai konteks pembacaan, bukan penyebab tunggal | Tim sustainability | P1 | Korelasi cuaca sederhana masih terbatas |

### 6.5 Arsitektur Dashboard Vite React

Target visualisasi final terbaru adalah dashboard Vite React di folder `web/`. Dashboard ini tidak membaca CSV secara langsung di browser, tetapi menggunakan JSON statis yang dibangun dari output CSV final.

| Komponen | Peran |
|---|---|
| `Data_Acquisition/dataset/processed/*.csv` | Sumber analitis kanonik hasil pipeline OSEMN |
| `scripts/build_react_dashboard_data.py` | Script packaging yang mengubah CSV final menjadi JSON ringkas |
| `web/public/data/*.json` | Data delivery statis untuk dashboard React |
| `web/src/main.tsx` | Implementasi enam halaman dashboard dan logika filter |
| `web/src/styles.css` | Styling dashboard responsif |
| `vercel.json` | Konfigurasi build dan output directory untuk Vercel |

JSON yang digunakan dashboard adalah:

| File JSON | Fungsi |
|---|---|
| `manifest.json` | Metadata dashboard, default scenario, dan ringkasan entity |
| `daily_trend.json` | Tren konsumsi harian dan marker anomali |
| `monthly_trend.json` | Agregasi konsumsi bulanan |
| `entity_daily.json` | Observasi harian per entity untuk drill-down |
| `anomalies.json` | Kandidat anomali per skenario |
| `dimensions.json` | Dimensi tanggal, entity, dan scenario |
| `entity_scorecard.json` | Ranking prioritas audit entity |
| `anomaly_case_review.json` | Kandidat anomali utama untuk review naratif |
| `data_quality_summary.json` | Ringkasan kualitas data |
| `model_evaluation_summary.json` | Ringkasan evaluasi model |
| `eda_summary.json` | Ringkasan hasil eksplorasi |
| `insight_recommendation_matrix.json` | Insight dan rekomendasi |

![Placeholder arsitektur dashboard Vite React](assets/laporan/gambar_18_arsitektur_dashboard_vite_react.png)

*Gambar 18. Placeholder alur CSV processed, packaging JSON, Vite React dashboard, dan deployment Vercel.*

### 6.6 Halaman Dashboard Vite React

| Halaman | Tujuan | Visual Utama |
|---|---|---|
| Executive Overview | Menampilkan ringkasan konsumsi dan anomali | KPI total consumption, average daily consumption, anomaly count, trend, top entity |
| Consumption Trend | Membaca pola waktu | Line chart harian, bar bulanan, weekday/weekend, dan filter waktu |
| Anomaly Explorer | Menelusuri kandidat anomali | Score view, tabel kandidat, anomaly count by entity, scenario comparison |
| Weather Impact | Membaca konteks cuaca | Konsumsi vs suhu/hujan, hot/rainy filter, tabel hari anomali bercuaca tertentu |
| Meter Ranking | Menentukan prioritas audit | Ranking konsumsi, anomaly rate, entity scorecard |
| Data Quality and Methodology | Menjelaskan batasan data dan metode | Quality flag counts, excluded meter list, source summary, method summary |

Global filter yang disediakan dashboard:

1. Date start.
2. Date end.
3. Scenario.
4. Entity.
5. Anomaly flag.
6. Day type.
7. Weather.
8. Data quality flag.

![Placeholder dashboard executive overview](assets/laporan/gambar_19_dashboard_executive_overview.png)

*Gambar 19. Placeholder screenshot halaman Executive Overview pada dashboard Vite React.*

![Placeholder dashboard anomaly explorer](assets/laporan/gambar_20_dashboard_anomaly_explorer.png)

*Gambar 20. Placeholder screenshot halaman Anomaly Explorer pada dashboard Vite React.*

![Placeholder dashboard data quality methodology](assets/laporan/gambar_21_dashboard_data_quality_methodology.png)

*Gambar 21. Placeholder screenshot halaman Data Quality and Methodology pada dashboard Vite React.*

### 6.7 Runbook dan Validasi Dashboard

Perintah lokal dari root repo:

```powershell
npm install
npm run build:web-data
npm run dev:web
```

Dashboard lokal dibuka melalui:

```text
http://127.0.0.1:5173
```

Validasi produksi:

```powershell
npm run build:web
npm run preview:web
```

Konfigurasi Vercel:

| Setting | Nilai |
|---|---|
| Framework Preset | Vite |
| Install Command | `npm install` |
| Build Command | `npm run build:web` |
| Output Directory | `web/dist` |
| Root Directory | repo root |

Validasi yang sudah dicatat pada cache proyek:

1. `python -m py_compile scripts\build_react_dashboard_data.py`.
2. `python scripts\build_react_dashboard_data.py`.
3. `npm install`.
4. `npm audit --omit=dev` menghasilkan 0 vulnerabilities setelah upgrade Vite.
5. `npm run build:web` berhasil.
6. Browser verification pada desktop dan mobile viewport.
7. Enam halaman dashboard dapat dinavigasi tanpa console warning/error.

### 6.8 Batasan Interpretasi

Batasan interpretasi:

1. D0849 menjadi prioritas utama karena scorecard, tetapi penyebab teknisnya perlu validasi lapangan.
2. Kandidat anomali adalah hasil model tanpa label, sehingga tidak boleh langsung disebut fault.
3. Konsumsi tinggi dapat mencerminkan fungsi equipment yang memang intensif energi.
4. Weather context tidak menggantikan data aktivitas gedung.
5. Dashboard bersifat statis dan memakai prebuilt JSON; model tidak dilatih ulang di browser.
6. Production deploy ke Vercel belum dilakukan dari CLI karena token lokal tidak valid.

### 6.9 Tindak Lanjut

Tindak lanjut yang direkomendasikan:

1. Publish dashboard Vite React ke Vercel menggunakan `cache/react_dashboard_vercel_guide.md`.
2. Validasi URL produksi untuk desktop/mobile layout, data load, filter, dan seluruh enam halaman.
3. Ambil screenshot setiap halaman dashboard Vite React untuk laporan presentasi.
4. Lakukan review manual terhadap kandidat anomali utama, terutama D0849.
5. Perluas analisis ke interval lebih kecil atau lebih banyak meter jika ingin membuat klaim kampus yang lebih luas.

## 7. Kesimpulan dan Rekomendasi

### 7.1 Kesimpulan

Analisis ini berhasil membentuk pipeline OSEMN untuk studi konsumsi energi berbasis smart meter HKUST dan data cuaca HKO. Data harian T1440 dipilih karena sesuai dengan granularitas data cuaca harian. Dari 26 meter inventory, 12 meter aktif pada konteks `Cheng_Yu_Tung_Building` digunakan sebagai subset utama.

Tahap Scrub menghasilkan fact table `date x entity_id` sebanyak 10.524 baris. Feature engineering menghasilkan 10.420 baris lengkap untuk model. Tahap Explore menunjukkan konsumsi yang relatif stabil, weekday lebih tinggi daripada weekend, top 5 meter menyumbang sekitar 68,79% konsumsi, dan cuaca lebih tepat dibaca sebagai konteks.

Tahap Model menggunakan Isolation Forest dengan tiga skenario. Skenario balanced menghasilkan 521 kandidat anomali atau 5% dari 10.420 baris eligible. Entity D0849 menjadi prioritas utama berdasarkan kontribusi konsumsi, anomaly count, peak load, dan priority score.

Tahap iNterpret menghasilkan insight dan rekomendasi yang digunakan pada dashboard Vite React. Dashboard membaca JSON statis dari `web/public/data`, sementara CSV processed tetap menjadi sumber analitis kanonik.

### 7.2 Rekomendasi Akhir

1. Gunakan D0849 sebagai titik awal investigasi karena memiliki kontribusi konsumsi dan kandidat anomali tertinggi.
2. Gunakan skenario balanced sebagai default analisis dashboard, dengan strict dan sensitive sebagai pembanding.
3. Jangan menghapus meter bermasalah dari dokumentasi; tampilkan pada halaman Data Quality agar batasan analisis transparan.
4. Baca anomali bersama rolling deviation, baseline agreement, cuaca, dan konteks weekday/weekend.
5. Publish dashboard Vite React ke Vercel, lalu lakukan validasi visual desktop/mobile sebelum digunakan untuk presentasi final.

## 8. Lampiran

### 8.1 Daftar Output Data Utama

| File | Fungsi |
|---|---|
| `Data_Acquisition/dataset/processed/fact_energy_weather_daily.csv` | Fact utama konsumsi, cuaca, kalender, quality flag, dan fitur |
| `Data_Acquisition/dataset/processed/fact_anomaly_scenarios.csv` | Output model Isolation Forest per skenario |
| `Data_Acquisition/dataset/processed/dim_date.csv` | Dimensi tanggal |
| `Data_Acquisition/dataset/processed/dim_entity.csv` | Dimensi meter/entity |
| `Data_Acquisition/dataset/processed/dim_scenario.csv` | Dimensi skenario model |
| `Data_Acquisition/dataset/processed/entity_scorecard.csv` | Ranking prioritas audit |
| `Data_Acquisition/dataset/processed/model_evaluation_summary.csv` | Ringkasan evaluasi model |
| `Data_Acquisition/dataset/processed/anomaly_case_review.csv` | Review kandidat anomali |
| `Data_Acquisition/dataset/processed/eda_summary.csv` | Ringkasan eksplorasi |
| `Data_Acquisition/dataset/processed/insight_recommendation_matrix.csv` | Insight dan rekomendasi |
| `Data_Acquisition/dataset/processed/dashboard_validation_checklist.csv` | Checklist validasi dashboard |
| `scripts/build_react_dashboard_data.py` | Script packaging CSV processed menjadi JSON dashboard |
| `web/public/data/*.json` | Data statis yang dibaca dashboard Vite React |
| `web/src/main.tsx` | Implementasi halaman dan interaksi dashboard React |
| `web/src/styles.css` | Styling responsif dashboard |
| `vercel.json` | Konfigurasi deployment Vercel |

### 8.2 Daftar Output Visual

| File | Keterangan |
|---|---|
| `outputs/eda/final/daily_consumption_trend.png` | Tren konsumsi harian dan marker anomali balanced |
| `outputs/eda/final/monthly_consumption_trend.png` | Tren konsumsi bulanan |
| `outputs/eda/final/weekday_weekend_consumption.png` | Distribusi konsumsi weekday dan weekend |
| `outputs/eda/final/top_meter_contribution_pareto.png` | Kontribusi meter dan pola Pareto |
| `outputs/eda/final/weather_consumption_context.png` | Konteks suhu dan hujan terhadap konsumsi |
| `outputs/eda/final/data_quality_flags.png` | Ringkasan quality flag |
| `outputs/eda/final/anomaly_case_review.png` | Review kandidat anomali utama |

### 8.3 Daftar Placeholder Gambar Manual

| Placeholder | Isi yang Disarankan |
|---|---|
| `assets/laporan/gambar_01_alur_osemn_energi_anomali.png` | Diagram alur OSEMN proyek |
| `assets/laporan/gambar_02_sumber_data_hkust_hko.png` | Ringkasan sumber data HKUST dan HKO |
| `assets/laporan/gambar_03_struktur_folder_data.png` | Struktur folder raw, processed, dan output |
| `assets/laporan/gambar_04_seleksi_subset_meter_t1440.png` | Alur seleksi 26 meter menjadi 12 meter utama |
| `assets/laporan/gambar_05_transformasi_konsumsi_harian.png` | Ilustrasi differencing meter reading menjadi konsumsi harian |
| `assets/laporan/gambar_06_star_schema_dashboard.png` | Star schema analitis untuk dashboard |
| `assets/laporan/gambar_07_feature_engineering_energi_cuaca.png` | Ringkasan feature engineering |
| `assets/laporan/gambar_08_tren_konsumsi_harian.png` | Salinan/versi final `outputs/eda/final/daily_consumption_trend.png` |
| `assets/laporan/gambar_09_tren_konsumsi_bulanan.png` | Salinan/versi final `outputs/eda/final/monthly_consumption_trend.png` |
| `assets/laporan/gambar_10_perbandingan_weekday_weekend.png` | Salinan/versi final `outputs/eda/final/weekday_weekend_consumption.png` |
| `assets/laporan/gambar_11_kontribusi_meter_pareto.png` | Salinan/versi final `outputs/eda/final/top_meter_contribution_pareto.png` |
| `assets/laporan/gambar_12_konteks_cuaca_konsumsi.png` | Salinan/versi final `outputs/eda/final/weather_consumption_context.png` |
| `assets/laporan/gambar_13_kualitas_data.png` | Salinan/versi final `outputs/eda/final/data_quality_flags.png` |
| `assets/laporan/gambar_14_alur_model_isolation_forest.png` | Diagram alur pemodelan Isolation Forest |
| `assets/laporan/gambar_15_evaluasi_skenario_model.png` | Grafik jumlah anomali dan baseline agreement per skenario |
| `assets/laporan/gambar_16_anomaly_case_review.png` | Salinan/versi final `outputs/eda/final/anomaly_case_review.png` |
| `assets/laporan/gambar_17_entity_scorecard_prioritas_audit.png` | Visual ranking prioritas audit dari entity scorecard |
| `assets/laporan/gambar_18_arsitektur_dashboard_vite_react.png` | Arsitektur CSV processed, JSON delivery, Vite React, dan Vercel |
| `assets/laporan/gambar_19_dashboard_executive_overview.png` | Screenshot halaman Executive Overview dashboard Vite React |
| `assets/laporan/gambar_20_dashboard_anomaly_explorer.png` | Screenshot halaman Anomaly Explorer dashboard Vite React |
| `assets/laporan/gambar_21_dashboard_data_quality_methodology.png` | Screenshot halaman Data Quality and Methodology dashboard Vite React |

### 8.4 Ringkasan Sumber

| Sumber | Keterangan |
|---|---|
| HKUST smart meter dataset | Dataset utama konsumsi energi kampus |
| HKUST metadata TTL | Metadata relasi meter, gedung, lantai, ruang, dan equipment |
| Hong Kong Observatory Open Data | Dataset pendukung cuaca harian |

### 8.5 Catatan Penggunaan Laporan

Laporan ini dapat digunakan sebagai dasar narasi tugas besar, bahan presentasi, dan panduan menjalankan dashboard Vite React. Bagian dashboard harus diperlakukan sebagai dashboard statis berbasis prebuilt JSON sampai URL produksi Vercel dipublish dan divalidasi.
