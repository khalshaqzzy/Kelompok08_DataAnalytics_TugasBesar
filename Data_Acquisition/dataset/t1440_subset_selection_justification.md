# T1440 Subset Selection Justification

## Objective

Subset ini dibuat untuk mendukung tahap **Obtain** pada proyek Energy Efficiency Analytics. Tujuannya adalah memilih file time-series harian yang realistis untuk diproses tim berikutnya, tetap terdokumentasi, dan dapat dipertanggungjawabkan secara objektif.

## Selection Criteria

1. **Interval compatibility**: hanya file `T1440` yang dipilih sebagai basis utama karena intervalnya harian dan dapat digabung langsung dengan data cuaca harian HKO berdasarkan kolom tanggal.
2. **Completeness**: prioritas diberikan pada meter dengan coverage penuh periode proyek, yaitu 2022-01-01 sampai 2024-05-27.
3. **Data quality**: meter nol konstan, near-zero/low-signal, dan short coverage tidak dipakai pada model utama, tetapi tetap dicatat untuk data quality dashboard.
4. **TTL interpretability**: meter harus memiliki mapping TTL yang jelas ke building serta room/equipment agar hasil dashboard tidak berhenti pada ID meter saja.
5. **Analytical focus**: subset difokuskan pada satu building dengan banyak meter aktif supaya perbandingan antar meter/equipment lebih konsisten.

## Result

Building utama yang dipilih: `Cheng_Yu_Tung_Building`.

Meter utama yang dipilih:

`D0849`, `D0848`, `D0854`, `D0853`, `D0862`, `D0857`, `D0851`, `D0861`, `D0852`, `D0860`, `D0850`, `D0865`

Ringkasan quality flag:

| Quality flag | Meter count |
|---|---:|
| active | 18 |
| near_zero_low_signal | 3 |
| short_coverage | 1 |
| zero_constant | 4 |

## Exclusion Notes

- Zero constant: `D0821`, `D0823`, `D0844`, `D0847`
- Near-zero / low-signal: `D0863`, `D0864`, `D0846`
- Short coverage: `D0816`

## Recommended Explanation for Report

Berdasarkan inventory awal, semua file T1440 dicatat terlebih dahulu. Pemilihan subset dilakukan menggunakan kriteria objektif: kesesuaian interval harian dengan data cuaca HKO, coverage penuh, meter aktif dengan konsumsi non-zero, mapping TTL yang jelas, dan fokus pada satu gedung agar analisis tetap konsisten. Hasil profiling menunjukkan `Cheng_Yu_Tung_Building` memiliki kumpulan meter T1440 aktif dengan metadata yang lengkap, sehingga dipilih sebagai fokus utama untuk analisis konsumsi, anomaly detection, dan dashboard Power BI.
