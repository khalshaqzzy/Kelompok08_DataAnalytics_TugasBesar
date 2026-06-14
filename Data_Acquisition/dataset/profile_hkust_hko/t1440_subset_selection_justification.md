# T1440 Subset Selection Justification

## Objective

Subset ini dibuat untuk mendukung tahap Obtain dan Scrub pada proyek Energy Efficiency Analytics. Pemilihan dilakukan secara objektif berdasarkan interval harian, coverage, kualitas sinyal, metadata TTL, dan fokus analitis pada satu gedung.

## Selection Criteria

1. Interval compatibility: hanya file T1440 yang dipilih karena selaras dengan HKO daily weather.
2. Completeness: prioritas pada meter dengan coverage penuh 2022-01-01 sampai 2024-05-27.
3. Data quality: zero constant, near-zero/low-signal, dan short coverage tidak dipakai dalam model utama.
4. TTL interpretability: meter harus punya mapping building/room/equipment yang dapat dijelaskan.
5. Analytical focus: subset difokuskan pada satu building agar perbandingan antar meter lebih konsisten.

## Result

Building utama yang dipilih: `Cheng_Yu_Tung_Building`.

Meter utama yang dipilih: `D0849`, `D0848`, `D0854`, `D0853`, `D0862`, `D0857`, `D0851`, `D0861`, `D0852`, `D0860`, `D0850`, `D0865`

## Quality Flag Summary

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

Berdasarkan inventory awal, semua file T1440 dicatat terlebih dahulu. Pemilihan subset menggunakan kriteria objektif: kesesuaian interval harian dengan data HKO, coverage penuh, meter aktif non-zero, mapping TTL yang jelas, dan fokus pada `Cheng_Yu_Tung_Building` agar analisis konsumsi, anomaly detection, dan dashboard Power BI tetap konsisten.
