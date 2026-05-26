# Script Presentasi 3 Menit - Slide 4

Slide 4 menjelaskan strategi pipeline data yang akan kita pakai di proyek ini. Intinya, kita tidak hanya melihat angka konsumsi listrik dari smart meter, tetapi juga menambahkan konteks cuaca agar interpretasinya lebih masuk akal.

Langkah pertama adalah mengambil data energi dari dataset HKUST. Dataset ini menjadi sumber utama karena berisi pembacaan smart meter kampus selama sekitar dua setengah tahun. Data mentahnya tetap disimpan apa adanya, lalu kita membaca metadata `.ttl` untuk memahami relasi meter, gedung, zona, dan equipment. Di tahap awal, kita tidak langsung memakai semua file yang besar, tetapi memilih subset yang realistis.

Langkah kedua adalah memilih subset energi. Strateginya adalah memakai tiga sampai lima gedung atau zona, lalu memilih periode tiga sampai enam bulan atau satu tahun. Untuk integrasi awal, interval T1440 atau data harian menjadi pilihan paling aman karena cocok dengan data cuaca harian. Kalau nanti ingin melihat pola jam, kita bisa memakai T60 untuk beberapa meter yang terpilih.

Langkah ketiga adalah mengambil data cuaca dari Hong Kong Observatory. Variabel yang dipakai antara lain suhu rata-rata, suhu maksimum, suhu minimum, kelembapan relatif, curah hujan, radiasi matahari, dan kecepatan angin. Data ini relevan karena konsumsi listrik kampus, terutama untuk pendinginan ruangan, bisa dipengaruhi oleh kondisi cuaca.

Langkah keempat adalah menggabungkan data energi dan data cuaca. Prosesnya dilakukan berdasarkan tanggal, karena analisis awal menggunakan level harian. Pada tahap ini, kita juga menyamakan format tanggal, mengecek missing value, dan memastikan data cuaca yang ditempelkan sesuai dengan periode data energi.

Langkah kelima adalah menyiapkan fitur untuk analisis. Dari sisi energi, kita hitung konsumsi harian dari selisih pembacaan meter. Dari sisi waktu, kita buat fitur seperti weekday, weekend, bulan, dan tahun. Dari sisi cuaca, kita tambahkan fitur seperti rainy day, hot day, dan cooling degree day.

Output dari pipeline ini adalah dataset analitik yang sudah siap dipakai untuk eksplorasi, deteksi anomali, forecasting sederhana, dan dashboard. Jadi, slide ini menunjukkan bahwa proyek kita mengikuti alur OSEMN: data diperoleh dengan jelas, dibersihkan, disiapkan fiturnya, lalu bisa dipakai untuk analisis dan rekomendasi efisiensi energi.
