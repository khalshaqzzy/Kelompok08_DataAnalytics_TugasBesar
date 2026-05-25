# Proposal Tugas Besar Data Analitik

## Analisis Konsumsi dan Efisiensi Energi Gedung Kampus

| Komponen | Keterangan |
|---|---|
| Mata kuliah | Data Analitik |
| Topik panduan | Energi dan Efisiensi Gedung/Kampus |
| Fokus proyek | Pola konsumsi listrik, efisiensi relatif antar gedung/zona, dan anomali beban |
| Kerangka kerja | OSEMN: Obtain, Scrub, Explore, Model, iNterpret |
| Dataset utama | A 2.5-year campus-level smart meter database with equipment data for energy analytics |
| Dataset pendukung | Hong Kong Observatory Open Data |
| Jumlah anggota | 4 orang |

---

# Bab 1. Pendahuluan

## 1.1 Latar Belakang

Kampus modern menggunakan energi listrik untuk banyak aktivitas, seperti perkuliahan, laboratorium, kantor administrasi, asrama, perpustakaan, pencahayaan, server, fasilitas umum, dan sistem pendingin ruangan. Pola konsumsi energi pada lingkungan kampus tidak selalu stabil. Ada jam puncak, beban dasar yang terus berjalan, serta kemungkinan konsumsi tinggi di luar jam operasional.

Efisiensi energi menjadi penting karena konsumsi listrik berdampak pada biaya operasional, keberlanjutan lingkungan, dan target green campus. Namun, efisiensi tidak cukup dilakukan dengan imbauan umum. Pengelola kampus membutuhkan analisis berbasis data untuk mengetahui gedung atau zona mana yang paling besar konsumsi energinya, kapan beban meningkat, serta apakah ada pola pemakaian yang tidak wajar.

Proyek ini menggunakan data smart meter kampus sebagai sumber utama dan data cuaca sebagai sumber pendukung. Data smart meter digunakan untuk membaca pola konsumsi listrik, sedangkan data cuaca digunakan untuk membantu menjelaskan variasi konsumsi, terutama karena suhu dan kondisi lingkungan dapat memengaruhi kebutuhan pendinginan ruangan.

## 1.2 Rumusan Masalah

Rumusan masalah yang akan dijawab dalam proyek ini adalah:

1. Bagaimana pola konsumsi energi listrik kampus berdasarkan waktu, gedung, dan zona?
2. Gedung atau zona mana yang memiliki konsumsi listrik paling tinggi dan berpotensi menjadi prioritas efisiensi?
3. Apakah terdapat anomali beban listrik, seperti lonjakan konsumsi atau pemakaian tinggi di luar jam operasional?
4. Bagaimana kondisi cuaca dapat membantu menjelaskan perubahan konsumsi energi listrik?
5. Visualisasi atau dashboard seperti apa yang dapat membantu pengelola kampus memantau konsumsi energi dan mengambil keputusan?

## 1.3 Tujuan

Tujuan proyek ini adalah:

1. Mengidentifikasi pola konsumsi listrik berdasarkan jam, hari, bulan, dan periode operasional.
2. Membandingkan konsumsi listrik antar gedung atau zona kampus.
3. Menemukan sinyal anomali beban listrik yang perlu ditinjau lebih lanjut.
4. Mengintegrasikan data cuaca sebagai konteks pendukung interpretasi konsumsi energi.
5. Menyusun insight, rekomendasi efisiensi, dan rancangan dashboard berbasis data.

## 1.4 Pengguna Sasaran

Pengguna sasaran dari hasil analisis ini adalah:

- Tim sarana dan prasarana kampus.
- Pengelola gedung.
- Manajemen kampus atau organisasi.
- Tim sustainability atau green campus.
- Dosen dan peneliti bidang energi, lingkungan, atau data analytics.
- Mahasiswa yang mempelajari penerapan data analytics pada masalah operasional kampus.

## 1.5 Ruang Lingkup

Ruang lingkup proyek meliputi:

- Objek analisis: gedung, zona, dan meter listrik pada lingkungan kampus.
- Fokus analisis: konsumsi listrik, pola beban, efisiensi relatif, anomali awal, dan pengaruh konteks cuaca.
- Periode data utama: 2022-01-01 sampai 2024-05-27.
- Unit analisis: meter, gedung, zona, waktu, dan variabel cuaca yang dapat diselaraskan.
- Output: dataset bersih, visualisasi eksploratif, model/analisis lanjutan, insight, rekomendasi, dan rancangan dashboard.

Batasan proyek:

- Tidak melakukan audit teknis detail sistem HVAC.
- Tidak melakukan pengukuran langsung di kampus sendiri.
- Tidak membangun sistem IoT baru.
- Tidak menghitung biaya listrik aktual jika data tarif tidak tersedia.
- Tidak mengklaim hasil subset sebagai representasi penuh seluruh kampus tanpa catatan keterbatasan.

---

# Bab 2. O - Obtain

## 2.1 Ringkasan Sumber Data

Sesuai panduan tugas besar, proyek ini menggunakan minimal dua sumber data: satu dataset utama dan satu dataset pendukung.

| No | Nama Dataset | Sumber | Periode | Format | Peran |
|---|---|---|---|---|---|
| 1 | A 2.5-year campus-level smart meter database with equipment data for energy analytics | Dryad dan Scientific Data | 2022-01-01 sampai 2024-05-27 | `.xlsx` untuk time-series, `.ttl` untuk metadata Brick Schema | Dataset utama |
| 2 | Hong Kong Observatory Open Data | Hong Kong Observatory | Disesuaikan dengan subset data HKUST | API/CSV/JSON sesuai endpoint yang digunakan | Dataset pendukung |

## 2.2 Dataset Utama

Dataset utama yang digunakan adalah **A 2.5-year campus-level smart meter database with equipment data for energy analytics**. Dataset ini berasal dari Hong Kong University of Science and Technology (HKUST), Sai Kung District, Hong Kong.

Sumber:

- Dryad dataset: <https://doi.org/10.5061/dryad.k3j9kd5h6>
- Artikel Scientific Data: <https://doi.org/10.1038/s41597-024-04106-1>

Karakteristik dataset utama:

| Aspek | Detail |
|---|---|
| Lokasi | HKUST, Sai Kung District, Hong Kong |
| Skala | Kampus |
| Jumlah meter | Lebih dari 1.400 smart meter |
| Jumlah gedung | Lebih dari 20 gedung |
| Periode | 2022-01-01 sampai 2024-05-27 |
| Ukuran data | Sekitar 1,43 GB terkompresi |
| Format | `.xlsx` untuk time-series, `.ttl` untuk metadata Brick Schema |
| Interval | 15 menit, 30 menit, 1 jam, dan 1 hari setelah resampling |
| Jenis data | Konsumsi listrik, metadata meter, metadata lokasi/gedung/equipment |

Dataset ini dipilih karena konteksnya sangat sesuai dengan topik energi dan efisiensi gedung/kampus. Data berasal dari kampus nyata, memiliki cakupan meter dan gedung yang luas, serta mendukung analisis pola beban, fault detection, demand response, load forecasting, dan efisiensi energi.

## 2.3 Dataset Pendukung

Dataset pendukung yang digunakan adalah **Hong Kong Observatory Open Data**. Dataset ini dipilih karena lokasi dataset utama berada di Hong Kong, sehingga data cuaca lokal dapat digunakan untuk memperkaya interpretasi konsumsi listrik.

Sumber:

- Hong Kong Observatory Open Data: <https://www.weather.gov.hk/en/abouthko/opendata_intro.htm>

Variabel yang direncanakan:

- Suhu udara.
- Kelembapan relatif.
- Curah hujan.
- Kondisi cuaca atau indikator iklim lain yang tersedia pada endpoint yang digunakan.

Peran dataset pendukung:

- Menjelaskan kemungkinan hubungan antara kondisi cuaca dan konsumsi listrik.
- Membantu interpretasi kenaikan beban listrik, terutama jika terkait kebutuhan pendinginan ruangan.
- Memperkaya fitur analitik pada tahap Scrub dan Model.

## 2.4 Cara Memperoleh Data

Langkah memperoleh dataset utama:

1. Membuka halaman Dryad dataset melalui DOI resmi.
2. Mengunduh paket dataset `All_Data.zip`.
3. Mengekstrak data ke direktori raw data.
4. Memilih data clean/resampled sesuai kebutuhan analisis.
5. Membaca metadata `.ttl` untuk memahami relasi meter, zona, equipment, dan gedung.

Langkah memperoleh dataset pendukung:

1. Membuka portal Open Data Hong Kong Observatory.
2. Menentukan endpoint atau file cuaca yang relevan dengan periode analisis.
3. Mengambil data cuaca sesuai periode subset HKUST.
4. Menyimpan data mentah cuaca secara terpisah dari data hasil preprocessing.
5. Menyamakan format tanggal/waktu agar dapat digabungkan dengan data konsumsi listrik.

## 2.5 Strategi Subset Data

Karena dataset utama berukuran besar, proyek akan menggunakan subset yang tetap cukup representatif untuk analisis:

| Komponen | Strategi |
|---|---|
| Gedung/zona | Memilih 3-5 gedung atau zona |
| Periode | Menggunakan 3-6 bulan atau 1 tahun data, menyesuaikan kapasitas pemrosesan |
| Interval | Mengutamakan T60 atau T1440 agar data lebih ringan |
| Integrasi | Menggabungkan konsumsi listrik dengan data cuaca berdasarkan waktu |
| Penyimpanan | Raw data dan clean data disimpan terpisah |

## 2.6 Alasan Pemilihan Dataset

Alasan pemilihan dataset utama:

1. Relevan dengan topik energi dan efisiensi gedung/kampus.
2. Berasal dari kampus nyata, bukan data simulasi.
3. Memiliki cakupan lebih dari 1.400 smart meter dan lebih dari 20 gedung.
4. Memiliki periode observasi sekitar 2,5 tahun.
5. Memiliki metadata yang membantu analisis pada level meter, zona, gedung, dan equipment.
6. Didukung publikasi ilmiah dan repository data terbuka.

Alasan pemilihan dataset pendukung:

1. Data cuaca relevan untuk menjelaskan variasi konsumsi listrik, terutama beban pendinginan ruangan.
2. Sumbernya resmi dan sesuai lokasi dataset utama.
3. Dapat digunakan untuk memperkaya fitur analitik dan interpretasi hasil.

## 2.7 Keterbatasan Awal

Keterbatasan awal yang perlu diperhatikan:

- Dataset HKUST berukuran besar, sehingga perlu strategi subset.
- Metadata `.ttl` menggunakan Brick Schema dan membutuhkan pemahaman tambahan.
- Tidak semua meter mungkin memiliki kualitas data yang sama.
- Terdapat kemungkinan missing value, data nol, atau outlier.
- Data berasal dari Hong Kong, sehingga hasil interpretasi tidak otomatis sama dengan kondisi kampus di Indonesia.
- Data cuaca tidak selalu menjelaskan semua variasi konsumsi listrik karena faktor operasional kampus juga sangat berpengaruh.

---

# Rencana Kesesuaian OSEMN

| Tahap | Rencana Pengerjaan | Luaran Minimal |
|---|---|---|
| Obtain | Mengambil dataset HKUST dan data cuaca, mendokumentasikan sumber, periode, format, dan keterbatasan | Raw data, tabel sumber dataset, pertanyaan analitik |
| Scrub | Membersihkan missing value, duplikasi, tipe tanggal, outlier, serta mengintegrasikan data energi dan cuaca | Clean dataset, kode preprocessing, fitur baru |
| Explore | Melihat statistik deskriptif, tren waktu, perbandingan gedung/zona, dan pola awal | Minimal 3 visualisasi eksploratif |
| Model | Melakukan anomaly detection sederhana atau forecasting konsumsi energi | Model/analisis lanjutan dan evaluasi |
| iNterpret | Menyusun insight dan rekomendasi efisiensi | Minimal 3 insight dan 3 rekomendasi |

---

# Pembagian Peran Anggota Kelompok

Jumlah anggota kelompok adalah 4 orang. Mengikuti catatan pada panduan, peran **Documentation and Insight Lead** digabung dengan **Visualization / Dashboard Developer**.

| Anggota | Peran | Tanggung Jawab Utama | Output |
|---|---|---|---|
| Anggota 1 | Data Engineer | Mengambil data, menyusun struktur folder, menyimpan raw data, mencatat sumber dan legalitas data | Raw dataset, dokumentasi sumber data |
| Anggota 2 | Data Preprocessing Lead | Membersihkan data, menangani missing value, resampling, integrasi data cuaca, dan feature engineering | Clean dataset dan kode preprocessing |
| Anggota 3 | Data Analyst / Modeler | Melakukan EDA, analisis perbandingan, anomaly detection sederhana, forecasting opsional, dan evaluasi | Temuan analitik, model/analisis lanjutan |
| Anggota 4 | Visualization / Dashboard Developer + Documentation and Insight Lead | Membuat visualisasi/dashboard, menyusun insight, rekomendasi, laporan, slide, README, dan deklarasi AI | Dashboard, laporan, slide, insight, dokumentasi akhir |

---

# Deklarasi Penggunaan AI

Dalam pengerjaan tugas besar ini, kelompok menggunakan kakas AI generatif untuk membantu eksplorasi ide, penyusunan draf laporan, perapihan bahasa, dan perancangan struktur slide. Seluruh kode, analisis, visualisasi, insight, rekomendasi, dan kesimpulan tetap harus diperiksa, dijalankan ulang, dan divalidasi oleh anggota kelompok. Kelompok bertanggung jawab penuh atas kebenaran hasil, interpretasi, dan kesimpulan yang disampaikan.

| No | Kakas AI | Tujuan Penggunaan | Bagian yang Dibantu | Diverifikasi oleh |
|---|---|---|---|---|
| 1 | ChatGPT / Codex | Penyusunan draf dan struktur proposal | Bab 1, Bab 2, slide proposal | Anggota kelompok |

---

# Daftar Sumber

1. Li, M., Wang, Z., Qu, Y., Chui, K. M., & Leung-Shea, M. (2024). *A 2.5-year campus-level smart meter database with equipment data for energy analytics* [Dataset]. Dryad. <https://doi.org/10.5061/dryad.k3j9kd5h6>
2. Li, M., Wang, Z., Qu, Y., Chui, K. M., & Leung-Shea, M. (2024). *A multi-year campus-level smart meter database*. Scientific Data, 11, 1284. <https://doi.org/10.1038/s41597-024-04106-1>
3. Hong Kong Observatory. *Open Data*. <https://www.weather.gov.hk/en/abouthko/opendata_intro.htm>
