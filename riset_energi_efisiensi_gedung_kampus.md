# Riset Topik: Energi dan Efisiensi Gedung/Kampus Organisasi

## 1. Ringkasan Rekomendasi

Topik yang dipilih:

> Analisis konsumsi dan efisiensi energi gedung/kampus organisasi untuk menemukan pola konsumsi, membandingkan efisiensi antar area/gedung, serta mendeteksi anomali beban listrik.

Rekomendasi dataset utama:

> **A 2.5-year campus-level smart meter database with equipment data for energy analytics** dari Hong Kong University of Science and Technology (HKUST), tersedia di Dryad.

Alasan utama:

- Paling sesuai dengan skala tugas: **kampus dan gedung**.
- Data berasal dari kampus nyata, bukan simulasi.
- Memiliki lebih dari **1.400 smart meter**, lebih dari **20 gedung**, dan periode sekitar **2,5 tahun**.
- Mendukung fokus analitik yang diminta: pola konsumsi, efisiensi, anomali beban, dan prediksi.
- Format data cukup umum untuk analitik: Excel `.xlsx` dan metadata `.ttl`.
- Ada publikasi ilmiah pendukung di Scientific Data, sehingga sumbernya kredibel.

Dataset cadangan yang juga kuat:

1. **Building Data Genome Project 2 / ASHRAE Great Energy Predictor III**
2. **I-BLEND: Indian Buildings Energy Consumption Dataset**
3. **UCI Energy Efficiency Dataset** sebagai opsi kecil/sederhana jika ingin model regresi cepat, tetapi kurang cocok untuk konteks kampus.

Kesimpulan:

> Untuk tugas besar ini, gunakan dataset HKUST sebagai dataset utama. Jika ukuran file terlalu besar, gunakan subset gedung, subset meter, atau subset periode, misalnya 3-6 bulan data dari beberapa gedung/zone.

---

## 2. Latar Belakang Topik

Kampus dan organisasi modern menggunakan banyak energi untuk menunjang aktivitas harian, seperti perkuliahan, laboratorium, kantor administrasi, asrama, perpustakaan, sistem pendingin ruangan, pencahayaan, server, dan fasilitas umum. Konsumsi energi ini tidak selalu merata. Ada jam-jam puncak, area yang boros, serta kemungkinan penggunaan listrik yang tidak wajar di luar jam operasional.

Efisiensi energi menjadi penting karena konsumsi listrik berdampak pada biaya operasional, keberlanjutan lingkungan, dan target green campus. Namun, penghematan energi tidak cukup dilakukan hanya dengan imbauan umum seperti "matikan lampu" atau "hemat AC". Pengelola kampus membutuhkan bukti berbasis data untuk mengetahui:

- Gedung atau area mana yang paling boros.
- Kapan beban listrik mencapai puncak.
- Apakah ada konsumsi energi yang tidak normal.
- Faktor apa yang memengaruhi konsumsi energi.
- Bagaimana strategi efisiensi dapat diprioritaskan.

Dengan pendekatan data analytics, data smart meter dapat diolah untuk menemukan pola pemakaian energi, membandingkan efisiensi antar gedung, mendeteksi anomali beban, dan memberi rekomendasi pengelolaan energi yang lebih tepat sasaran.

---

## 3. Rumusan Masalah

Rumusan masalah yang disarankan:

1. Bagaimana pola konsumsi energi pada gedung/kampus berdasarkan waktu, jenis gedung, dan area penggunaan?
2. Gedung atau area mana yang menunjukkan konsumsi energi paling tinggi dan paling tidak efisien?
3. Apakah terdapat anomali beban listrik, seperti lonjakan mendadak atau konsumsi tinggi di luar jam operasional?
4. Bagaimana data smart meter dapat membantu mendukung keputusan efisiensi energi di lingkungan kampus?
5. Visualisasi atau dashboard seperti apa yang dapat membantu pengelola kampus memantau konsumsi dan potensi pemborosan energi?

---

## 4. Tujuan

Tujuan analitik:

1. Mengidentifikasi pola konsumsi energi berdasarkan jam, hari, bulan, dan jenis area/gedung.
2. Membandingkan konsumsi energi antar gedung atau zona kampus.
3. Menemukan anomali beban listrik yang berpotensi menunjukkan pemborosan atau gangguan operasional.
4. Menghasilkan insight yang dapat digunakan untuk rekomendasi efisiensi energi.
5. Merancang visualisasi/dashboard untuk memudahkan pemantauan konsumsi energi.

---

## 5. Pengguna Sasaran

Pengguna sasaran dari hasil analitik:

- Tim sarana dan prasarana kampus.
- Manajemen kampus atau organisasi.
- Pengelola gedung.
- Tim sustainability/green campus.
- Dosen dan peneliti bidang energi, lingkungan, atau data analytics.
- Mahasiswa yang ingin memahami pola konsumsi energi di lingkungan kampus.

---

## 6. Ruang Lingkup

Ruang lingkup yang disarankan:

- Objek analisis: gedung, zona, atau meter listrik pada lingkungan kampus.
- Fokus analisis: konsumsi listrik, pola beban, efisiensi relatif, dan anomali.
- Periode analisis: subset dari dataset, misalnya 3 bulan, 6 bulan, 1 tahun, atau seluruh 2,5 tahun jika memungkinkan.
- Unit analisis: meter, gedung, zona, atau kelompok fungsi gedung.
- Output: insight, visualisasi, rekomendasi efisiensi, dan rancangan dashboard.

Di luar ruang lingkup:

- Audit teknis detail sistem HVAC.
- Perhitungan biaya listrik aktual jika tarif tidak tersedia.
- Pengukuran langsung di kampus sendiri.
- Implementasi sistem IoT baru.
- Validasi fisik langsung terhadap perangkat listrik.

---

## 7. Dataset Utama Yang Direkomendasikan

### Nama Dataset

**A 2.5-year campus-level smart meter database with equipment data for energy analytics**

### Sumber

- Dryad dataset: https://doi.org/10.5061/dryad.k3j9kd5h6
- Artikel Scientific Data: https://doi.org/10.1038/s41597-024-04106-1

### Ringkasan Dataset

Dataset ini berasal dari Hong Kong University of Science and Technology (HKUST). Data berisi konsumsi energi listrik kampus yang dikumpulkan dari lebih dari 1.400 smart meter pada lebih dari 20 gedung selama sekitar 2,5 tahun.

Menurut halaman Dryad, periode data adalah:

> 2022-01-01 sampai 2024-05-27.

Dataset ini disusun untuk mendukung analisis energi kampus, seperti:

- Load pattern recognition.
- Fault detection.
- Demand response.
- Load forecasting.
- Analisis efisiensi energi.

### Karakteristik Data

| Aspek | Detail |
|---|---|
| Lokasi | HKUST, Sai Kung District, Hong Kong |
| Skala | Kampus |
| Jumlah meter | Lebih dari 1.400 meter |
| Jumlah gedung | Lebih dari 20 gedung |
| Periode | 2022-01-01 sampai 2024-05-27 |
| Format | `.xlsx` untuk time-series, `.ttl` untuk metadata Brick Schema |
| Ukuran data | Sekitar 1,43 GB terkompresi |
| Interval | 15 menit, 30 menit, 1 jam, dan 1 hari setelah resampling |
| Jenis data | Konsumsi listrik, metadata meter, metadata lokasi/gedung/equipment |

### Alasan Pemilihan Dataset

Dataset ini paling sesuai dengan topik karena:

1. **Konteksnya kampus nyata**
   - Data bukan simulasi, melainkan berasal dari sistem smart meter kampus.

2. **Skalanya relevan**
   - Tugas memilih topik gedung/kampus organisasi. Dataset ini tepat karena mencakup banyak gedung dan zona kampus.

3. **Mendukung banyak analisis**
   - Bisa digunakan untuk pola konsumsi, anomali, prediksi beban, dan rekomendasi efisiensi.

4. **Ada metadata**
   - Metadata membantu memahami hubungan meter, zona, equipment, dan gedung.

5. **Sumber kredibel**
   - Dipublikasikan di Dryad dan dibahas dalam artikel Scientific Data.

### Keterbatasan Awal

Beberapa keterbatasan yang perlu disebutkan di Bab 2 Obtain:

- Ukuran dataset cukup besar, sekitar 1,43 GB.
- Format metadata `.ttl` menggunakan Brick Schema, yang mungkin membutuhkan pemahaman tambahan.
- Tidak semua meter memiliki kualitas data yang sama.
- Ada missing value dan beberapa file yang dikecualikan karena data kosong atau nol.
- Dataset berasal dari Hong Kong, sehingga pola iklim, budaya penggunaan energi, dan operasional kampus dapat berbeda dari kampus di Indonesia.
- Jika analisis dilakukan dengan subset, hasil tidak mewakili seluruh kampus HKUST.

### Strategi Penggunaan Dataset Agar Realistis

Karena ukuran data cukup besar, proyek kelompok dapat dibuat lebih ringan dengan memilih subset:

- Pilih 3-5 gedung atau zona.
- Pilih data interval 1 jam atau 1 hari.
- Pilih periode 3-6 bulan.
- Fokus pada meter utama gedung atau area tertentu.
- Gunakan metadata untuk mengelompokkan berdasarkan lokasi atau tipe penggunaan.

Strategi analisis yang disarankan:

1. Ambil data resampled hourly atau daily.
2. Gabungkan dengan metadata meter.
3. Buat fitur waktu:
   - jam
   - hari
   - weekday/weekend
   - bulan
   - periode akademik/libur jika tersedia
4. Hitung total konsumsi per gedung/zona.
5. Deteksi outlier berdasarkan pola historis.
6. Buat dashboard ringkas.

---

## 8. Dataset Alternatif

### 8.1 Building Data Genome Project 2

Sumber:

- GitHub: https://github.com/buds-lab/building-data-genome-project-2
- Artikel Scientific Data: https://doi.org/10.1038/s41597-020-00712-x

Ringkasan:

Building Data Genome Project 2 adalah dataset open data yang berisi data meter energi dari 1.636 gedung non-residensial, 3.053 meter, dan data dua tahun, yaitu 2016-2017. Data tersedia dalam frekuensi per jam. Dataset juga memiliki metadata gedung dan data cuaca.

Kelebihan:

- Sangat populer untuk analisis energi gedung.
- Ada data meter listrik, air panas, chilled water, steam, gas, water, irrigation, dan solar.
- Ada metadata seperti luas bangunan, primary use, lokasi, timezone, dan EUI.
- Cocok untuk prediksi konsumsi, analisis EUI, dan anomali.
- Format CSV lebih ramah untuk pemula dibanding `.ttl`.

Kekurangan:

- Tidak spesifik satu kampus, melainkan kumpulan banyak situs di Amerika Utara dan Eropa.
- Beberapa metadata memiliki missing value tinggi.
- Skala sangat besar jika digunakan penuh.

Cocok jika:

- Kelompok ingin format CSV yang lebih mudah.
- Kelompok ingin analisis berbasis cuaca dan luas bangunan.
- Kelompok tidak keberatan jika konteksnya bukan satu kampus tunggal.

### 8.2 I-BLEND

Sumber:

- Artikel Scientific Data: https://doi.org/10.1038/sdata.2019.15

Ringkasan:

I-BLEND adalah dataset konsumsi energi listrik dari kampus akademik di India. Dataset mencakup 52 bulan data dengan sampling satu menit dari tujuh bangunan komersial dan residensial. Dataset juga menyediakan data occupancy dengan sampling 10 menit, kalender institut, detail arsitektur gedung, dan cuaca lokal untuk beberapa bulan.

Kelebihan:

- Konteks kampus sangat jelas.
- Sampling sangat detail, yaitu satu menit.
- Ada data occupancy, sehingga bisa dianalisis hubungan aktivitas manusia dan konsumsi energi.
- Cocok untuk anomali, pola beban, dan prediksi.

Kekurangan:

- Hanya tujuh bangunan.
- Data sangat granular, sehingga perlu agregasi agar mudah dianalisis.
- Perlu mengecek akses file dan struktur data sebelum digunakan penuh.

Cocok jika:

- Kelompok ingin fokus pada gedung kampus dengan occupancy.
- Kelompok ingin analisis pola jam operasional, malam, dan akhir pekan.

### 8.3 ASHRAE Great Energy Predictor III

Sumber:

- Kaggle: https://www.kaggle.com/c/ashrae-energy-prediction
- Dataset turunan Kaggle: https://www.kaggle.com/datasets/sumit261124/ashrae-great-energy-predictor-iii-dataset

Ringkasan:

Dataset ini digunakan untuk kompetisi prediksi konsumsi energi gedung. Isinya mencakup data meter, metadata gedung, dan data cuaca.

Kelebihan:

- Cocok untuk tugas machine learning.
- Banyak notebook referensi di Kaggle.
- Struktur data relatif jelas: meter reading, building metadata, weather data.

Kekurangan:

- Lebih berorientasi kompetisi prediksi daripada studi kampus.
- Data besar.
- Perlu akun Kaggle untuk akses.

Cocok jika:

- Kelompok ingin fokus pada prediksi konsumsi energi.
- Kelompok ingin memakai model machine learning dan membandingkan akurasi.

### 8.4 UCI Energy Efficiency Dataset

Sumber:

- UCI: https://archive.ics.uci.edu/dataset/242/energy+efficiency

Ringkasan:

Dataset ini berisi 768 contoh konfigurasi bangunan dengan fitur desain bangunan dan target heating load serta cooling load.

Kelebihan:

- Kecil dan mudah diproses.
- Cocok untuk regresi machine learning.
- Bagus untuk latihan model prediksi.

Kekurangan:

- Bukan data kampus nyata.
- Tidak memiliki time-series konsumsi listrik.
- Tidak cocok untuk analisis pola harian, anomali beban, atau dashboard smart meter.

Cocok jika:

- Waktu pengerjaan sangat singkat.
- Fokus tugas lebih ke model prediksi sederhana, bukan analisis kampus.

---

## 9. Perbandingan Dataset

| Dataset | Kesesuaian Topik | Kemudahan | Kekuatan Analitik | Risiko |
|---|---:|---:|---:|---|
| HKUST Campus Smart Meter | Sangat tinggi | Sedang | Sangat tinggi | Ukuran besar, metadata `.ttl` |
| Building Data Genome Project 2 | Tinggi | Sedang | Sangat tinggi | Tidak spesifik satu kampus |
| I-BLEND | Tinggi | Sedang | Tinggi | Gedung lebih sedikit, data sangat granular |
| ASHRAE Great Energy Predictor III | Sedang-tinggi | Sedang | Tinggi | Fokus kompetisi prediksi |
| UCI Energy Efficiency | Rendah-sedang | Sangat mudah | Sedang | Bukan kampus, bukan time-series |

Rekomendasi akhir:

1. **Pilihan utama:** HKUST Campus Smart Meter.
2. **Pilihan paling aman jika ingin CSV dan dokumentasi luas:** Building Data Genome Project 2.
3. **Pilihan paling kampus + occupancy:** I-BLEND.
4. **Pilihan paling sederhana:** UCI Energy Efficiency.

---

## 10. Ide Fokus Analitik

### 10.1 Analisis Pola Konsumsi

Pertanyaan:

- Pada jam berapa konsumsi energi tertinggi?
- Apakah pola hari kerja berbeda dengan akhir pekan?
- Apakah ada perbedaan pola antara gedung akademik, asrama, kantor, dan fasilitas umum?
- Apakah konsumsi berubah pada periode tertentu?

Visualisasi:

- Line chart konsumsi per jam.
- Heatmap jam vs hari.
- Bar chart konsumsi per gedung.
- Calendar heatmap konsumsi harian.

### 10.2 Analisis Efisiensi

Pertanyaan:

- Gedung mana yang konsumsi energinya paling tinggi?
- Gedung mana yang paling boros relatif terhadap fungsi atau ukurannya?
- Apakah konsumsi malam hari terlalu tinggi?

Metrik:

- Total kWh per gedung/zona.
- Rata-rata kWh per hari.
- Peak load.
- Base load malam hari.
- Load factor.
- Jika luas tersedia: kWh/m2 atau EUI.

Catatan:

Jika dataset utama tidak menyediakan luas gedung yang mudah digunakan, efisiensi dapat dinilai secara relatif berdasarkan pola konsumsi, base load, dan perbandingan antar zona/meter sejenis.

### 10.3 Deteksi Anomali Beban

Pertanyaan:

- Kapan terjadi lonjakan konsumsi yang tidak biasa?
- Apakah ada beban tinggi saat malam atau akhir pekan?
- Apakah ada meter yang tiba-tiba nol atau sangat tinggi?

Metode sederhana:

- Z-score.
- Interquartile Range (IQR).
- Rolling mean dan rolling standard deviation.
- Perbandingan nilai aktual dengan pola rata-rata historis pada jam/hari yang sama.

Output:

- Daftar tanggal/jam anomali.
- Gedung atau meter penyumbang anomali.
- Visualisasi titik anomali pada grafik time-series.

### 10.4 Prediksi Konsumsi Energi

Pertanyaan:

- Bisakah konsumsi energi periode berikutnya diprediksi dari pola historis?
- Fitur waktu apa yang paling memengaruhi beban?

Model yang mungkin:

- Baseline moving average.
- Linear Regression.
- Random Forest Regression.
- XGBoost/LightGBM jika diperbolehkan.
- ARIMA/Prophet jika ingin time-series.

Metrik evaluasi:

- MAE.
- RMSE.
- MAPE.

Untuk tugas presentasi, model tidak harus terlalu kompleks. Yang penting ada alasan pemilihan metode dan insight yang jelas.

---

## 11. Bab 2 - O: Obtain

### Sumber Data

Sumber data utama berasal dari dataset publik:

**A 2.5-year campus-level smart meter database with equipment data for energy analytics**  
Penyedia: Hong Kong University of Science and Technology (HKUST)  
Repositori: Dryad  
DOI: https://doi.org/10.5061/dryad.k3j9kd5h6  
Artikel pendukung: https://doi.org/10.1038/s41597-024-04106-1

### Cara Memperoleh Data

Langkah memperoleh data:

1. Buka halaman dataset Dryad.
2. Unduh file `README.md` untuk memahami struktur data.
3. Unduh `All_Data.zip` jika ingin dataset penuh.
4. Ekstrak data.
5. Pilih subset data yang diperlukan, misalnya file resampled hourly atau daily.
6. Baca file `.xlsx` menggunakan Python, R, Excel, atau Power BI.
7. Gunakan metadata `.ttl` jika perlu menghubungkan meter dengan gedung, zona, atau equipment.

### Periode Data

Periode data:

> 1 Januari 2022 sampai 27 Mei 2024.

Untuk proyek kelompok, periode analisis dapat dibatasi, misalnya:

- 3 bulan pertama tahun 2023.
- Semester akademik tertentu.
- Perbandingan tahun 2022 dan 2023.
- Periode sebelum dan setelah perubahan aktivitas kampus.

### Format Data

Format data:

- `.xlsx` untuk time-series konsumsi listrik.
- `.ttl` untuk metadata berbasis Brick Schema.
- Data bersih sudah di-resampling ke interval:
  - 15 menit
  - 30 menit
  - 1 jam
  - 1 hari

### Variabel Yang Berpotensi Digunakan

Variabel utama:

- Timestamp.
- Nilai konsumsi atau meter reading.
- ID meter.
- Lokasi meter.
- Gedung atau zona.
- Equipment terkait.
- Interval waktu.

Fitur turunan:

- Jam.
- Hari.
- Bulan.
- Weekday/weekend.
- Jam operasional/non-operasional.
- Konsumsi harian.
- Konsumsi rata-rata.
- Peak load.
- Base load malam.
- Indikator anomali.

### Alasan Pemilihan Data

Dataset dipilih karena:

- Sesuai dengan topik kampus dan gedung.
- Memiliki skala besar dan realistis.
- Memiliki data time-series untuk analisis pola konsumsi.
- Memungkinkan deteksi anomali dan prediksi beban.
- Memiliki metadata yang membantu interpretasi lokasi dan fungsi meter.
- Didukung oleh publikasi ilmiah dan repositori data terbuka.

### Keterbatasan Awal

Keterbatasan yang perlu dicatat:

- Dataset cukup besar sehingga perlu subset.
- Missing value perlu dianalisis sebelum modeling.
- Tidak semua meter memiliki interval yang sama.
- Metadata `.ttl` bisa lebih sulit dipahami daripada CSV biasa.
- Tidak semua hubungan meter-gedung langsung mudah dibaca tanpa parsing metadata.
- Dataset berasal dari Hong Kong, sehingga generalisasi ke kampus Indonesia perlu hati-hati.

---

## 12. Pembagian Peran Anggota Kelompok

Karena anggota kelompok ada 4 orang, sementara instruksi menyebut 5 peran, maka peran Documentation and Insight Lead dapat digabung dengan Visualization/Dashboard Developer.

| Anggota | Peran | Tanggung Jawab |
|---|---|---|
| Anggota 1 | Data Engineer | Mencari, mengunduh, menyeleksi dataset, memahami struktur file, mengatur folder data, memilih subset meter/gedung/periode |
| Anggota 2 | Data Preprocessing Lead | Membersihkan data, menangani missing value, menyamakan interval waktu, membuat fitur waktu, menyiapkan tabel final |
| Anggota 3 | Data Analyst / Modeler | Menganalisis pola konsumsi, membuat metrik efisiensi, mendeteksi anomali, membuat model prediksi sederhana jika diperlukan |
| Anggota 4 | Visualization / Dashboard Developer + Documentation and Insight Lead | Membuat grafik/dashboard, menyusun insight, rekomendasi, narasi presentasi, dan finalisasi slide |

Jika dosen meminta semua role tetap disebutkan, gunakan format:

- Data Engineer: Anggota 1
- Data Preprocessing Lead: Anggota 2
- Data Analyst / Modeler: Anggota 3
- Visualization / Dashboard Developer: Anggota 4
- Documentation and Insight Lead: dikerjakan bersama, koordinator Anggota 4

---

## 13. Struktur Slide Yang Disarankan

Minimal sesuai instruksi:

### Slide 1 - Judul

Judul:

> Analisis Konsumsi dan Efisiensi Energi Gedung Kampus Berbasis Data Smart Meter

Isi:

- Nama kelompok.
- Nama anggota.
- Mata kuliah.
- Topik.

### Slide 2 - Latar Belakang

Isi:

- Konsumsi energi kampus tinggi dan kompleks.
- Pengelola kampus perlu mengetahui pola dan pemborosan energi.
- Smart meter memungkinkan analisis berbasis data.
- Analitik energi dapat membantu efisiensi biaya dan keberlanjutan.

### Slide 3 - Rumusan Masalah

Isi:

- Pola konsumsi energi.
- Efisiensi antar gedung/zona.
- Anomali beban.
- Rekomendasi efisiensi.

### Slide 4 - Tujuan

Isi:

- Mengidentifikasi pola konsumsi.
- Membandingkan konsumsi antar gedung/zona.
- Mendeteksi anomali.
- Membuat visualisasi/dashboard.
- Menyusun rekomendasi.

### Slide 5 - Pengguna Sasaran dan Ruang Lingkup

Isi:

- Pengguna: sarpras, manajemen kampus, pengelola gedung, tim sustainability.
- Scope: data smart meter listrik gedung/zona kampus.
- Batasan: tidak melakukan audit fisik langsung.

### Slide 6 - O: Sumber Data

Isi:

- Dataset HKUST campus smart meter.
- Sumber: Dryad dan Scientific Data.
- Skala: lebih dari 1.400 meter, lebih dari 20 gedung, 2,5 tahun.
- Format: `.xlsx` dan `.ttl`.

### Slide 7 - O: Cara Memperoleh dan Format Data

Isi:

- Unduh dari Dryad.
- Pilih subset data.
- Gunakan file resampled hourly/daily.
- Gabungkan dengan metadata.
- Siapkan dataset final untuk analisis.

### Slide 8 - O: Alasan Pemilihan dan Keterbatasan

Isi:

- Alasan: relevan, kampus nyata, time-series, mendukung anomali dan prediksi.
- Keterbatasan: besar, missing value, metadata kompleks, konteks Hong Kong.

### Slide 9 - Rencana Analitik

Isi:

- EDA pola konsumsi.
- Perbandingan antar gedung/zona.
- Deteksi anomali.
- Prediksi beban sederhana.
- Dashboard.

### Slide 10 - Pembagian Peran

Isi:

- Tabel 4 anggota dan peran.

### Slide 11 - Output Yang Diharapkan

Isi:

- Grafik pola konsumsi.
- Daftar area boros/anomali.
- Dashboard monitoring.
- Rekomendasi efisiensi.

---

## 14. Rekomendasi Narasi Presentasi

Narasi utama yang bisa dipakai:

> Proyek ini berangkat dari kebutuhan kampus untuk memahami konsumsi energi secara lebih detail. Dengan data smart meter, konsumsi listrik tidak hanya dilihat sebagai total tagihan, tetapi dapat dianalisis berdasarkan waktu, gedung, zona, dan pola penggunaan. Analisis ini membantu menemukan area dengan konsumsi tinggi, mendeteksi anomali beban, dan menyusun rekomendasi efisiensi yang lebih tepat sasaran.

Narasi dataset:

> Dataset yang digunakan adalah dataset smart meter kampus HKUST yang tersedia secara publik melalui Dryad. Dataset ini mencakup lebih dari 1.400 meter di lebih dari 20 gedung selama sekitar 2,5 tahun. Karena ukurannya besar, analisis akan difokuskan pada subset tertentu, misalnya beberapa gedung atau periode tertentu, agar proses pengolahan data tetap realistis.

Narasi manfaat:

> Hasil analisis diharapkan dapat membantu pengelola kampus memantau konsumsi listrik, mengenali pola puncak beban, menemukan penggunaan energi yang tidak wajar, serta menentukan prioritas penghematan energi.

---

## 15. Rekomendasi Teknis Untuk Tahap Berikutnya

Langkah berikutnya setelah Bab 1 dan Bab 2:

1. Unduh README dataset HKUST terlebih dahulu.
2. Tentukan subset:
   - pilih 3-5 meter/gedung/zona,
   - pilih interval hourly atau daily,
   - pilih periode 3-6 bulan.
3. Buat data dictionary sederhana.
4. Lakukan exploratory data analysis:
   - missing value,
   - tren waktu,
   - pola harian/mingguan,
   - puncak konsumsi.
5. Buat visualisasi awal:
   - line chart,
   - heatmap,
   - bar chart,
   - anomaly plot.
6. Susun insight:
   - kapan konsumsi tertinggi,
   - area mana yang paling boros,
   - kapan anomali terjadi,
   - apa rekomendasi efisiensi.

---

## 16. Daftar Sumber

1. Li, M., Wang, Z., Qu, Y., Chui, K. M., & Leung-Shea, M. (2024). **A 2.5-year campus-level smart meter database with equipment data for energy analytics**. Dryad. https://doi.org/10.5061/dryad.k3j9kd5h6
2. Li, M., Wang, Z., Qu, Y., Chui, K. M., & Leung-Shea, M. (2024). **A multi-year campus-level smart meter database**. Scientific Data. https://doi.org/10.1038/s41597-024-04106-1
3. Miller, C., Kathirgamanathan, A., Picchetti, B., et al. (2020). **The Building Data Genome Project 2, energy meter data from the ASHRAE Great Energy Predictor III competition**. Scientific Data. https://doi.org/10.1038/s41597-020-00712-x
4. Building Data Genome Project 2 GitHub Repository. https://github.com/buds-lab/building-data-genome-project-2
5. Rashid, H., Singh, P., & Singh, A. (2019). **I-BLEND, a campus-scale commercial and residential buildings electrical energy dataset**. Scientific Data. https://doi.org/10.1038/sdata.2019.15
6. UCI Machine Learning Repository. **Energy Efficiency Dataset**. https://archive.ics.uci.edu/dataset/242/energy+efficiency

