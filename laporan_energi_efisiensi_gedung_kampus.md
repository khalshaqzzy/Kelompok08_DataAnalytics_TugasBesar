# Laporan Analisis Konsumsi dan Efisiensi Energi Gedung/Kampus

## Identitas Proyek

| Komponen | Keterangan |
|---|---|
| Topik | Analisis konsumsi dan efisiensi energi gedung/kampus organisasi |
| Dataset utama | A 2.5-year campus-level smart meter database with equipment data for energy analytics |
| Sumber data | Dryad dan artikel Scientific Data |
| Lokasi data | Hong Kong University of Science and Technology (HKUST), Hong Kong |
| Fokus analisis | Pola konsumsi, efisiensi relatif antar gedung/zona, anomali beban listrik, dan rancangan dashboard |

---

# Bab 1. Pendahuluan

## 1.1 Latar Belakang

Kampus dan organisasi modern menggunakan energi listrik untuk menunjang banyak aktivitas operasional, mulai dari perkuliahan, laboratorium, kantor administrasi, perpustakaan, asrama, pencahayaan, sistem pendingin ruangan, server, hingga fasilitas umum. Pola konsumsi energi pada lingkungan kampus tidak selalu stabil. Beban listrik dapat meningkat pada jam operasional tertentu, berbeda antar jenis gedung, dan berpotensi tetap tinggi di luar jam aktif.

Efisiensi energi menjadi isu penting karena konsumsi listrik berpengaruh langsung terhadap biaya operasional, target keberlanjutan, dan upaya green campus. Upaya penghematan energi tidak cukup dilakukan melalui imbauan umum, tetapi perlu didukung analisis data agar keputusan pengelolaan energi dapat diarahkan ke area yang paling membutuhkan perhatian.

Dengan pendekatan data analytics, data smart meter dapat digunakan untuk mengidentifikasi pola konsumsi, membandingkan efisiensi antar gedung atau zona, mendeteksi anomali beban listrik, serta menyusun rekomendasi efisiensi yang lebih berbasis bukti.

## 1.2 Rumusan Masalah

Rumusan masalah dalam proyek ini adalah sebagai berikut:

1. Bagaimana pola konsumsi energi pada gedung/kampus berdasarkan waktu, jenis gedung, dan area penggunaan?
2. Gedung atau zona mana yang menunjukkan konsumsi energi paling tinggi dan berpotensi kurang efisien?
3. Apakah terdapat anomali beban listrik, seperti lonjakan mendadak atau konsumsi tinggi di luar jam operasional?
4. Bagaimana data smart meter dapat membantu mendukung keputusan efisiensi energi di lingkungan kampus?
5. Visualisasi atau dashboard seperti apa yang dapat membantu pengelola kampus memantau konsumsi dan potensi pemborosan energi?

## 1.3 Tujuan

Tujuan proyek analitik ini adalah:

1. Mengidentifikasi pola konsumsi energi berdasarkan jam, hari, bulan, dan jenis area atau gedung.
2. Membandingkan konsumsi energi antar gedung atau zona kampus.
3. Menemukan anomali beban listrik yang berpotensi menunjukkan pemborosan atau gangguan operasional.
4. Menghasilkan insight yang dapat digunakan untuk rekomendasi efisiensi energi.
5. Merancang visualisasi atau dashboard untuk memudahkan pemantauan konsumsi energi.

## 1.4 Pengguna Sasaran

Pengguna sasaran dari hasil proyek ini meliputi:

- Tim sarana dan prasarana kampus.
- Manajemen kampus atau organisasi.
- Pengelola gedung.
- Tim sustainability atau green campus.
- Dosen dan peneliti bidang energi, lingkungan, atau data analytics.
- Mahasiswa yang ingin memahami pola konsumsi energi di lingkungan kampus.

## 1.5 Ruang Lingkup

Ruang lingkup proyek ini meliputi:

- Objek analisis: gedung, zona, dan meter listrik pada lingkungan kampus.
- Fokus analisis: konsumsi listrik, pola beban, efisiensi relatif, dan anomali.
- Dataset utama: data smart meter kampus HKUST.
- Periode data sumber: 2022-01-01 sampai 2024-05-27.
- Unit analisis: meter, gedung, zona, atau kelompok fungsi gedung.
- Output: insight, visualisasi, rekomendasi efisiensi, dan rancangan dashboard.

Batasan di luar ruang lingkup proyek:

- Audit teknis detail sistem HVAC.
- Perhitungan biaya listrik aktual jika tarif tidak tersedia.
- Pengukuran langsung di kampus sendiri.
- Implementasi sistem IoT baru.
- Validasi fisik langsung terhadap perangkat listrik.

---

# Bab 2. O - Obtain

## 2.1 Sumber Data

Dataset utama yang digunakan adalah **A 2.5-year campus-level smart meter database with equipment data for energy analytics**. Dataset ini berasal dari Hong Kong University of Science and Technology (HKUST) dan tersedia melalui Dryad.

Sumber utama:

- Dryad dataset: <https://doi.org/10.5061/dryad.k3j9kd5h6>
- Artikel Scientific Data: <https://doi.org/10.1038/s41597-024-04106-1>

Dataset ini berisi data konsumsi energi listrik kampus yang dikumpulkan dari **lebih dari 1.400 smart meter** pada **lebih dari 20 gedung** selama sekitar **2,5 tahun**. Dataset ini disusun untuk mendukung analisis energi kampus, seperti load pattern recognition, fault detection, demand response, load forecasting, dan analisis efisiensi energi.

## 2.2 Cara Memperoleh Data

Data dapat diperoleh melalui halaman Dryad dengan mengunduh paket dataset **All_Data.zip**. Paket tersebut berisi data time-series dan metadata yang dapat digunakan untuk analisis energi kampus.

Langkah memperoleh data:

1. Buka halaman Dryad dataset melalui DOI resmi.
2. Unduh file `All_Data.zip`.
3. Ekstrak file dataset ke direktori kerja proyek.
4. Pilih data clean/resampled sesuai kebutuhan analisis.
5. Gunakan metadata `HKUST_Meter_Metadata.ttl` untuk memahami hubungan meter, zona, equipment, dan gedung.
6. Siapkan subset data agar ukuran data lebih realistis untuk pengerjaan kelompok.

## 2.3 Periode Data

Periode data pada dataset utama adalah:

| Komponen | Nilai |
|---|---|
| Tanggal awal | 2022-01-01 |
| Tanggal akhir | 2024-05-27 |
| Durasi | Sekitar 2,5 tahun |
| Lokasi | Sai Kung District, Hong Kong |
| Institusi | Hong Kong University of Science and Technology |

Untuk pengerjaan tugas besar, penggunaan seluruh periode data dapat diganti dengan subset yang lebih ringan, misalnya 3 bulan, 6 bulan, atau 1 tahun, selama subset tersebut tetap cukup untuk menangkap pola konsumsi harian dan bulanan.

## 2.4 Format Data

Karakteristik data utama:

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

Dataset tersedia dalam beberapa format dan tingkat pemrosesan:

| Jenis data | Format | Keterangan |
|---|---|---|
| Time-series konsumsi listrik | `.xlsx` | Data konsumsi per titik meter |
| Metadata meter dan relasi gedung/zona/equipment | `.ttl` | Metadata berbasis Brick Schema |
| Raw dataset | `.xlsx` dan `.ttl` | Data asli sebelum standardisasi interval |
| Clean dataset | `.xlsx` dan `.ttl` | Data yang sudah diresampling |

Data clean/resampled tersedia dalam beberapa interval:

| Kode interval | Frekuensi |
|---|---|
| T15 | 15 menit |
| T30 | 30 menit |
| T60 | 1 jam |
| T1440 | 1 hari |

Untuk analisis awal, interval **T60 atau T1440** disarankan karena lebih ringan dan cukup untuk melihat pola konsumsi harian, perbandingan antar gedung, serta tren umum.

## 2.5 Alasan Pemilihan Dataset

Dataset HKUST dipilih sebagai dataset utama karena:

1. **Konteksnya sesuai dengan topik**
   Dataset berasal dari kampus nyata, sehingga relevan untuk analisis energi gedung/kampus organisasi.

2. **Skalanya kuat untuk analitik**
   Dataset mencakup lebih dari 1.400 smart meter pada lebih dari 20 gedung, sehingga memungkinkan analisis pada level meter, zona, dan gedung.

3. **Periode observasi cukup panjang**
   Periode sekitar 2,5 tahun memungkinkan analisis tren, pola musiman, perubahan operasional, dan potensi anomali.

4. **Mendukung banyak kasus analitik**
   Dataset dapat digunakan untuk load pattern recognition, fault detection, demand response, load forecasting, dan analisis efisiensi energi.

5. **Memiliki metadata**
   Metadata berbasis Brick Schema membantu memahami hubungan antara meter, zona, equipment, dan gedung.

6. **Sumber kredibel**
   Dataset dipublikasikan di Dryad dan didukung artikel di jurnal Scientific Data.

## 2.6 Keterbatasan Awal

Beberapa keterbatasan awal yang perlu diperhatikan:

- Ukuran dataset cukup besar, yaitu sekitar 1,43 GB terkompresi.
- Metadata `.ttl` menggunakan Brick Schema, sehingga membutuhkan pemahaman tambahan.
- Tidak semua meter memiliki kualitas data yang sama.
- Terdapat missing value dan sebagian file dikecualikan karena data kosong atau bernilai nol.
- Dataset berasal dari Hong Kong, sehingga pola iklim, budaya penggunaan energi, dan operasional kampus dapat berbeda dari kampus di Indonesia.
- Jika analisis dilakukan menggunakan subset, hasil tidak dapat langsung mewakili seluruh kampus HKUST.

## 2.7 Strategi Obtain untuk Proyek Kelompok

Agar pengerjaan realistis, strategi obtain yang digunakan adalah:

1. Menggunakan dataset HKUST sebagai dataset utama.
2. Memilih data clean/resampled agar preprocessing awal lebih ringan.
3. Mengutamakan interval 1 jam atau 1 hari.
4. Memilih 3-5 gedung atau zona sebagai subset analisis.
5. Menggabungkan data konsumsi dengan metadata meter.
6. Menyimpan data kerja dalam format yang mudah dianalisis, misalnya CSV atau Parquet setelah proses ekstraksi.

---

# Pembagian Peran Anggota Kelompok

Jumlah anggota kelompok adalah 4 orang. Karena terdapat 5 fungsi kerja, peran **Visualization / Dashboard Developer** digabung dengan **Documentation and Insight Lead**.

| Anggota | Peran | Tanggung Jawab Utama | Output |
|---|---|---|---|
| Anggota 1 | Data Engineer | Mengunduh dataset, menata struktur folder data, memilih subset, memastikan file dapat dibaca | Dataset siap pakai dan dokumentasi sumber data |
| Anggota 2 | Data Preprocessing Lead | Membersihkan data, menangani missing value, mengatur interval waktu, membuat fitur waktu | Data bersih dan data hasil transformasi |
| Anggota 3 | Data Analyst / Modeler | Menganalisis pola konsumsi, membandingkan gedung/zona, mendeteksi anomali sederhana | Insight analitik, tabel ringkasan, dan model/statistik pendukung |
| Anggota 4 | Visualization / Dashboard Developer + Documentation and Insight Lead | Membuat visualisasi/dashboard, menyusun narasi insight, merapikan laporan dan slide | Dashboard, visualisasi final, laporan, dan presentasi |

## Alur Kerja Kelompok

| Tahap | Penanggung Jawab Utama | Aktivitas |
|---|---|---|
| Obtain | Anggota 1 | Mengambil dataset utama, membaca metadata, menentukan subset |
| Clean/Preprocess | Anggota 2 | Membersihkan dan menyiapkan data analitik |
| Analyze/Model | Anggota 3 | Menghasilkan insight pola konsumsi dan anomali |
| Visualize/Communicate | Anggota 4 | Membuat dashboard, laporan, dan slide presentasi |

---

# Ringkasan Expected Output

Output akhir yang diharapkan dari proyek ini adalah:

- Dataset subset yang siap dianalisis.
- Ringkasan pola konsumsi energi berdasarkan waktu dan gedung/zona.
- Identifikasi area atau periode dengan konsumsi tinggi.
- Deteksi awal anomali beban listrik.
- Rekomendasi efisiensi berbasis data.
- Dashboard atau visualisasi yang membantu pengelola kampus mengambil keputusan.

---

# Daftar Sumber

1. Li, M., Wang, Z., Qu, Y., Chui, K. M., & Leung-Shea, M. (2024). *A 2.5-year campus-level smart meter database with equipment data for energy analytics* [Dataset]. Dryad. <https://doi.org/10.5061/dryad.k3j9kd5h6>
2. Li, M., Wang, Z., Qu, Y., Chui, K. M., & Leung-Shea, M. (2024). *A multi-year campus-level smart meter database*. Scientific Data, 11, 1284. <https://doi.org/10.1038/s41597-024-04106-1>
