# Kelompok08 Data Analytics Tugas Besar

Repository ini berisi proyek tugas besar Data Analytics untuk analisis konsumsi energi dan deteksi kandidat anomali berbasis data smart meter HKUST. Analisis menggunakan pendekatan OSEMN, yaitu Obtain, Scrub, Explore, Model, dan iNterpret. Output utama proyek ini berupa dataset analitis, visualisasi eksplorasi, laporan akhir, notebook analisis, serta dashboard React interaktif yang dapat diakses melalui Vercel.

Dashboard Vercel: [https://kelompok08-data-analytics-tugas-besar.vercel.app/](https://kelompok08-data-analytics-tugas-besar.vercel.app/)

## Deskripsi Proyek

Proyek ini menganalisis konsumsi energi harian dari smart meter HKUST pada interval T1440. Dataset utama berasal dari data smart meter HKUST, sedangkan dataset pendukung berasal dari Hong Kong Observatory untuk memberikan konteks cuaca harian. Analisis difokuskan pada subset 12 meter aktif yang dipilih berdasarkan cakupan dan kualitas data.

Tahapan utama yang dilakukan dalam repository ini meliputi:

1. Akuisisi dan seleksi data smart meter HKUST serta data cuaca HKO.
2. Pembersihan, validasi, dan integrasi data energi-cuaca.
3. Pembentukan dataset analitis dan star schema untuk kebutuhan dashboard.
4. Eksplorasi pola konsumsi energi harian, bulanan, weekday/weekend, kontribusi meter, dan kualitas data.
5. Deteksi kandidat anomali menggunakan Isolation Forest dengan skenario `strict`, `balanced`, dan `sensitive`.
6. Penyusunan insight, rekomendasi, laporan akhir, dan dashboard React.

Hasil deteksi anomali pada proyek ini diperlakukan sebagai kandidat investigasi, bukan sebagai bukti final adanya gangguan operasional. Hal ini karena dataset tidak menyediakan label anomali resmi.

## Struktur Repository

```text
.
|-- Data_Acquisition/
|   |-- dataset/
|   |   |-- hkust_raw_data/          # Data mentah smart meter HKUST dan metadata TTL
|   |   |-- weather_raw_data/        # Data cuaca mentah HKO
|   |   |-- processed/               # Dataset hasil pemrosesan dan output model
|   |   `-- profile_hkust_hko/       # Dokumentasi profil dan seleksi data
|   `-- *.png                        # Visual hasil profiling awal
|-- assets/                          # Gambar tampilan dashboard
|-- cache/                           # Dokumen pendukung, panduan, dan arsip proses
|-- notebooks/                       # Notebook analisis OSEMN
|-- outputs/                         # Output visual eksplorasi data
|-- scripts/                         # Pipeline Python untuk data processing, modelling, dan export
|-- web/                             # Aplikasi dashboard React/Vite
|-- laporan_akhir_energi_anomaly_powerbi.md
|-- package.json
|-- vercel.json
`-- README.md
```

## Sumber Data

| Dataset | Peran | Lokasi di Repository |
|---|---|---|
| HKUST smart meter T1440 | Dataset utama konsumsi energi harian | `Data_Acquisition/dataset/hkust_raw_data/T1440/` |
| Metadata HKUST TTL | Mapping meter ke konteks entity, building, floor, dan equipment | `Data_Acquisition/dataset/hkust_raw_data/HKUST_Meter_Metadata.ttl` |
| Hong Kong Observatory weather | Dataset pendukung untuk konteks cuaca harian | `Data_Acquisition/dataset/weather_raw_data/` |
| Dataset processed | Fact table, dimension table, summary, dan output model | `Data_Acquisition/dataset/processed/` |
| Data dashboard | JSON statis yang dibaca aplikasi React | `web/public/data/` |

## Output Utama

Beberapa output penting dari repository ini adalah:

| Output | Keterangan |
|---|---|
| `laporan_akhir_energi_anomaly_powerbi.md` | Laporan akhir analisis konsumsi energi dan deteksi anomali |
| `notebooks/energy_analytics_osemn.ipynb` | Notebook utama berbasis tahapan OSEMN |
| `Data_Acquisition/dataset/processed/fact_energy_weather_daily.csv` | Fact table utama hasil integrasi energi-cuaca |
| `Data_Acquisition/dataset/processed/fact_anomaly_scenarios.csv` | Output deteksi kandidat anomali untuk beberapa skenario |
| `Data_Acquisition/dataset/processed/dim_entity.csv` | Dimension table entity/meter |
| `Data_Acquisition/dataset/processed/dim_date.csv` | Dimension table tanggal |
| `Data_Acquisition/dataset/processed/dim_scenario.csv` | Dimension table skenario model |
| `outputs/eda/final/` | Visualisasi eksplorasi final |
| `web/` | Dashboard React/Vite |

## Prasyarat

Pastikan perangkat memiliki:

1. Python 3.10 atau versi yang kompatibel.
2. Node.js dan npm.
3. Git.

Paket Python yang digunakan oleh pipeline antara lain:

```bash
pip install pandas numpy matplotlib seaborn scikit-learn requests openpyxl
```

Dependency frontend dapat dipasang melalui:

```bash
npm install
```

## Cara Penggunaan

### 1. Clone Repository

```bash
git clone <url-repository>
cd Kelompok08_DataAnalytics_TugasBesar
```

Jika repository sudah tersedia secara lokal, perbarui terlebih dahulu:

```bash
git pull
```

### 2. Menjalankan Pipeline Data

Pipeline utama tersedia pada folder `scripts/`. Jalankan perintah berikut dari root repository sesuai kebutuhan:

```bash
python scripts/hko_weather.py
python scripts/hkust_t1440.py
python scripts/feature_engineering.py
python scripts/model_anomaly_scenarios.py
python scripts/build_powerbi_datamart.py
python scripts/build_final_eda.py
npm run build:web-data
```

Perintah tersebut akan membangun ulang data processed, output model, visual eksplorasi, dan data JSON untuk dashboard React.

### 3. Menjalankan Dashboard Secara Lokal

Pasang dependency frontend:

```bash
npm install
```

Jalankan dashboard dalam mode development:

```bash
npm run dev:web
```

Setelah server berjalan, buka alamat berikut pada browser:

```text
http://127.0.0.1:5173
```

### 4. Build Dashboard Produksi

Untuk memastikan dashboard dapat dibangun sebagai aplikasi produksi:

```bash
npm run build:web
```

Untuk menjalankan preview hasil build:

```bash
npm run preview:web
```

## Deployment

Dashboard dipublikasikan melalui Vercel dan dapat diakses pada:

[https://kelompok08-data-analytics-tugas-besar.vercel.app/](https://kelompok08-data-analytics-tugas-besar.vercel.app/)

Konfigurasi deployment tersedia pada `vercel.json` dengan pengaturan berikut:

| Pengaturan | Nilai |
|---|---|
| Framework | Vite |
| Install Command | `npm install` |
| Build Command | `npm run build:web` |
| Output Directory | `web/dist` |

## Halaman Dashboard

Dashboard React menyediakan beberapa halaman analisis:

1. Executive Overview.
2. Consumption Trend.
3. Anomaly Explorer.
4. Weather Impact.
5. Meter Ranking.
6. Data Quality.

Dashboard membaca data statis dari folder `web/public/data/`. Jika data processed diperbarui, jalankan kembali `npm run build:web-data` sebelum melakukan build atau deployment ulang.

## Catatan Batasan

1. Analisis difokuskan pada 12 meter aktif T1440, sehingga tidak mewakili seluruh smart meter HKUST.
2. Data cuaca digunakan sebagai konteks pendukung, bukan bukti kausal tunggal terhadap perubahan konsumsi energi.
3. Model Isolation Forest tidak menggunakan label ground truth karena label anomali resmi tidak tersedia.
4. Dashboard bersifat statis dan menggunakan file JSON yang sudah dibangun sebelumnya.
5. Kandidat anomali perlu divalidasi lebih lanjut dengan informasi operasional lapangan.
