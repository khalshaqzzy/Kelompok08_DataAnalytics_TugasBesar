# Power BI Manual Build Guide - Energy Anomaly Dashboard

Last updated: 2026-06-15, Asia/Jakarta

Dokumen ini adalah panduan operasional untuk membangun dashboard Power BI dari output CSV final proyek. Panduan ini tidak mengubah pipeline Python dan tidak mengotomasi Power BI Desktop.

Target file dashboard:

`outputs/powerbi/energy_anomaly_dashboard.pbix`

Scope dashboard:

- Analisis harian T1440 pada selected active meters.
- Fokus utama: `Cheng_Yu_Tung_Building`.
- Model utama: Isolation Forest anomaly detection dengan scenario `strict`, `balanced`, dan `sensitive`.
- Scenario default untuk dashboard: `balanced`.
- Cuaca HKO digunakan sebagai konteks, bukan bukti kausal tunggal.

Out of scope:

- Power BI Service deployment.
- Automation `.pbix`.
- Final academic report, slide deck, presentation, dan video/demo.

---

# 1. Prerequisite

Pastikan:

1. Power BI Desktop sudah terinstall.
2. Branch kerja sudah memiliki output final terbaru.
3. Folder repo:

```text
C:\Users\Khalfani Shaquille\Documents\GitHub\Kelompok08_DataAnalytics_TugasBesar
```

4. Folder sumber CSV:

```text
C:\Users\Khalfani Shaquille\Documents\GitHub\Kelompok08_DataAnalytics_TugasBesar\Data_Acquisition\dataset\processed
```

5. Folder output `.pbix`:

```text
C:\Users\Khalfani Shaquille\Documents\GitHub\Kelompok08_DataAnalytics_TugasBesar\outputs\powerbi
```

Jika folder `outputs\powerbi` belum ada, buat manual dari File Explorer sebelum save `.pbix`.

---

# 2. Import CSV

Di Power BI Desktop:

1. Klik **Get data**.
2. Pilih **Text/CSV**.
3. Import CSV dari folder `Data_Acquisition\dataset\processed`.
4. Klik **Transform Data** jika perlu cek tipe data, atau **Load** jika tipe sudah terbaca benar.

Import tabel berikut:

| Table | File | Role |
|---|---|---|
| `fact_energy_weather_daily` | `fact_energy_weather_daily.csv` | Fact konsumsi, cuaca, fitur, dan quality flag |
| `fact_anomaly_scenarios` | `fact_anomaly_scenarios.csv` | Fact output model anomaly per scenario |
| `dim_date` | `dim_date.csv` | Dimensi kalender |
| `dim_entity` | `dim_entity.csv` | Dimensi meter/entity dan quality decision |
| `dim_scenario` | `dim_scenario.csv` | Dimensi scenario model |
| `entity_scorecard` | `entity_scorecard.csv` | Ranking/prioritas audit entity |
| `anomaly_case_review` | `anomaly_case_review.csv` | Top anomaly case review |
| `data_quality_summary` | `data_quality_summary.csv` | Summary kualitas data |
| `model_evaluation_summary` | `model_evaluation_summary.csv` | Summary evaluasi model |
| `eda_summary` | `eda_summary.csv` | Summary evidence EDA |
| `insight_recommendation_matrix` | `insight_recommendation_matrix.csv` | Insight dan rekomendasi |
| `dashboard_validation_checklist` | `dashboard_validation_checklist.csv` | Checklist validasi dashboard |

Opsional, import hanya jika ingin halaman methodology lebih detail:

| Table | File |
|---|---|
| `feature_engineering_summary` | `feature_engineering_summary.csv` |
| `visual_interpretation_summary` | `visual_interpretation_summary.csv` |
| `data_dictionary_energy_dashboard` | `data_dictionary_energy_dashboard.csv` |

Best practice import:

- Jangan import file lama seperti `master_energy_weather_t1440_selected_daily.csv` ke dashboard utama.
- Jangan import raw dataset besar ke Power BI.
- Gunakan CSV final saja agar dashboard ringan dan relasi jelas.

---

# 3. Data Type Checks

Setelah import, buka **Transform Data** atau **Data view** dan cek tipe data berikut.

## 3.1 Date Columns

Set type menjadi **Date**:

| Table | Column |
|---|---|
| `fact_energy_weather_daily` | `date` |
| `fact_anomaly_scenarios` | `date` |
| `dim_date` | `date` |
| `anomaly_case_review` | `date` |

## 3.2 Whole Number Columns

Set type menjadi **Whole number**:

| Table | Columns |
|---|---|
| `fact_energy_weather_daily` | `year`, `quarter`, `month`, `day_of_week_num`, `is_weekend`, `is_rainy_day`, `is_hot_day_28c`, `is_model_eligible`, `feature_complete_flag` |
| `fact_anomaly_scenarios` | `anomaly_flag`, `anomaly_rank_within_scenario`, `iqr_anomaly_flag`, `zscore_anomaly_flag`, `baseline_agreement_count`, `scenario_anomaly_count`, `is_stable_anomaly_candidate`, `is_weekend`, `is_rainy_day`, `is_hot_day_28c` |
| `dim_scenario` | `is_default` |
| `entity_scorecard` | `model_eligible_days`, `balanced_anomaly_count`, `strict_anomaly_count`, `sensitive_anomaly_count`, `entity_priority_rank` |

## 3.3 Decimal Number Columns

Set type menjadi **Decimal number**:

| Table | Columns |
|---|---|
| `fact_energy_weather_daily` | `daily_consumption`, `meter_reading`, weather fields, rolling/lag features |
| `fact_anomaly_scenarios` | `daily_consumption`, `anomaly_score`, rolling/lag features, weather fields, z-score fields |
| `entity_scorecard` | `total_consumption`, `average_daily_consumption`, `peak_daily_consumption`, `balanced_anomaly_rate`, `entity_contribution_pct`, `entity_priority_score` |
| `model_evaluation_summary` | `contamination`, `anomaly_rate`, agreement rates |

Best practice type checks:

- `entity_id`, `meter_id`, `scenario`, `building`, `floor`, dan label fields harus **Text**.
- Jangan ubah `entity_id` atau `meter_id` menjadi number.
- Format persentase seperti `entity_contribution_pct`, `balanced_anomaly_rate`, dan `anomaly_rate` sebagai **Percentage** di Power BI.

---

# 4. Relationship Model

Buka **Model view** dan buat relationship berikut.

| From Table | From Column | To Table | To Column | Cardinality | Cross-filter |
|---|---|---|---|---|---|
| `fact_energy_weather_daily` | `date` | `dim_date` | `date` | Many to one | Single |
| `fact_energy_weather_daily` | `entity_id` | `dim_entity` | `entity_id` | Many to one | Single |
| `fact_anomaly_scenarios` | `date` | `dim_date` | `date` | Many to one | Single |
| `fact_anomaly_scenarios` | `entity_id` | `dim_entity` | `entity_id` | Many to one | Single |
| `fact_anomaly_scenarios` | `scenario` | `dim_scenario` | `scenario` | Many to one | Single |

Optional relationships:

| From Table | From Column | To Table | To Column | Notes |
|---|---|---|---|---|
| `entity_scorecard` | `entity_id` | `dim_entity` | `entity_id` | Use if ranking page needs entity slicer propagation |
| `anomaly_case_review` | `entity_id` | `dim_entity` | `entity_id` | Use if case table needs entity slicer propagation |
| `anomaly_case_review` | `date` | `dim_date` | `date` | Use if case table needs date slicer propagation |

Best practice relationship:

- Gunakan star schema: dimensions filter facts.
- Cross-filter direction tetap **Single**.
- Jangan buat relationship many-to-many jika tidak perlu.
- Jangan menghubungkan fact table ke fact table secara langsung.
- Jika Power BI membuat relationship otomatis yang salah, hapus dan buat manual.

---

# 5. DAX Measures

Buat table khusus measures:

1. Klik **Enter data**.
2. Buat table kosong bernama `Measures`.
3. Setelah dibuat, tambahkan measure berikut satu per satu.

## 5.1 Consumption Measures

```DAX
Total Consumption =
SUM ( fact_energy_weather_daily[daily_consumption] )
```

```DAX
Average Daily Consumption =
AVERAGE ( fact_energy_weather_daily[daily_consumption] )
```

```DAX
Peak Daily Consumption =
MAX ( fact_energy_weather_daily[daily_consumption] )
```

```DAX
Active Entity Count =
DISTINCTCOUNT ( fact_energy_weather_daily[entity_id] )
```

```DAX
Model Eligible Count =
CALCULATE (
    COUNTROWS ( fact_energy_weather_daily ),
    fact_energy_weather_daily[is_model_eligible] = 1
)
```

## 5.2 Anomaly Measures

```DAX
Anomaly Count =
CALCULATE (
    COUNTROWS ( fact_anomaly_scenarios ),
    fact_anomaly_scenarios[anomaly_flag] = 1
)
```

```DAX
Anomaly Rate =
DIVIDE (
    [Anomaly Count],
    COUNTROWS ( fact_anomaly_scenarios )
)
```

```DAX
Average Anomaly Score =
AVERAGE ( fact_anomaly_scenarios[anomaly_score] )
```

```DAX
Top Anomaly Rank =
MIN ( fact_anomaly_scenarios[anomaly_rank_within_scenario] )
```

## 5.3 Data Quality Measures

```DAX
Data Quality Issue Count =
CALCULATE (
    COUNTROWS ( fact_energy_weather_daily ),
    fact_energy_weather_daily[data_quality_flag] <> "valid"
)
```

```DAX
Rainy Day Count =
CALCULATE (
    DISTINCTCOUNT ( fact_energy_weather_daily[date] ),
    fact_energy_weather_daily[is_rainy_day] = 1
)
```

```DAX
Hot Day Count =
CALCULATE (
    DISTINCTCOUNT ( fact_energy_weather_daily[date] ),
    fact_energy_weather_daily[is_hot_day_28c] = 1
)
```

```DAX
Excluded Entity Count =
CALCULATE (
    DISTINCTCOUNT ( dim_entity[entity_id] ),
    dim_entity[is_model_eligible_entity] = 0
)
```

## 5.4 Scorecard Measures

```DAX
Average Priority Score =
AVERAGE ( entity_scorecard[entity_priority_score] )
```

```DAX
Highest Priority Score =
MAX ( entity_scorecard[entity_priority_score] )
```

Formatting:

- Consumption measures: whole number or 1 decimal.
- Rates: percentage with 1-2 decimals.
- Scores: 1-2 decimals.

---

# 6. Dashboard Design System

Use a clean analytical style.

## 6.1 Page Setup

Recommended canvas:

- Size: 16:9.
- Background: light gray `#F7F8FA` or white.
- Page padding: consistent.
- Use grid alignment.

## 6.2 Color Rules

| Meaning | Color | Usage |
|---|---|---|
| Consumption | Blue `#1F4E79` | Main consumption bars/lines |
| Anomaly | Red `#C43B3B` | Anomaly flags/points only |
| Weather | Orange `#F58518` | Temperature/rainfall context |
| Valid/quality positive | Teal/green `#2A9D8F` | Valid or healthy status |
| Neutral/context | Gray `#6B7280` | Labels, methodology, inactive context |

Best practice:

- Red hanya untuk anomaly atau issue.
- Jangan pakai terlalu banyak warna per page.
- Warna scenario harus konsisten:
  - strict: dark red;
  - balanced: blue;
  - sensitive: orange.

## 6.3 Layout Rules

Default page structure:

1. Top row: title and slicers.
2. Second row: KPI cards.
3. Middle area: primary charts.
4. Bottom area: detail table or evidence notes.

Best practice:

- Slicer selalu di posisi atas atau kiri.
- KPI cards jangan terlalu banyak; 4-6 cukup.
- Detail table jangan mendominasi first view.
- Hindari visual dekoratif yang tidak menjawab pertanyaan analitik.
- Gunakan tooltip untuk konteks, bukan menumpuk terlalu banyak label.

## 6.4 Text Rules

- Judul page harus literal: `Executive Overview`, `Anomaly Explorer`, dan seterusnya.
- Judul visual harus menyebut metric dan grain.
- Hindari klaim kausal seperti "weather causes anomaly".
- Gunakan wording "candidate anomaly", "review candidate", atau "context".

---

# 7. Global Slicers

Slicer wajib:

| Slicer | Table | Column | Recommended style |
|---|---|---|---|
| Date range | `dim_date` | `date` | Between |
| Scenario | `dim_scenario` | `scenario` | Dropdown or tile |
| Entity | `dim_entity` | `entity_id` or `meter_name` | Dropdown |
| Building | `dim_entity` | `building` | Dropdown |
| Anomaly flag | `fact_anomaly_scenarios` | `anomaly_flag` | Tile |
| Weekend | `dim_date` or fact | `is_weekend` | Tile |
| Rainy day | fact | `is_rainy_day` | Tile |
| Hot day | fact | `is_hot_day_28c` | Tile |
| Data quality flag | fact | `data_quality_flag` | Dropdown |

Default slicer recommendation:

- Scenario default should be `balanced`.
- Date default can use full period.
- Anomaly flag default can show all rows on overview, anomaly-only on Anomaly Explorer.

---

# 8. Page Build Specification

## 8.1 Page 1 - Executive Overview

Purpose:

Ringkasan cepat konsumsi, anomaly candidates, dan entity prioritas.

Visuals:

| Area | Visual | Fields / Measures |
|---|---|---|
| KPI | Card | `Total Consumption` |
| KPI | Card | `Average Daily Consumption` |
| KPI | Card | `Peak Daily Consumption` |
| KPI | Card | `Anomaly Count` |
| KPI | Card | `Anomaly Rate` |
| Main | Line chart | Axis `dim_date[date]`; Value `Total Consumption` |
| Main | Bar chart | Axis `dim_entity[entity_id]`; Value `Total Consumption`; sort descending |
| Detail | Table | `anomaly_case_review[date]`, `entity_id`, `daily_consumption`, `anomaly_score`, `weather_context_label` |

Slicers:

- Date range.
- Scenario.
- Entity.
- Anomaly flag.

Design:

- KPI cards in one horizontal row.
- Use red only for anomaly KPI or anomaly table indicator.
- Keep the line chart wider than the ranking chart.

Validation:

- Scenario slicer changes anomaly count.
- Entity slicer changes consumption and anomaly table.

## 8.2 Page 2 - Consumption Trend

Purpose:

Menjelaskan pola konsumsi harian, bulanan, dan weekday/weekend.

Visuals:

| Area | Visual | Fields / Measures |
|---|---|---|
| Main | Line chart | Axis `dim_date[date]`; Value `Total Consumption`; tooltip weather fields |
| Main | Column chart | Axis `dim_date[year_month]` if available, or month/year from `dim_date`; Value `Total Consumption` |
| Comparison | Box/column style chart | `is_weekend` vs `Total Consumption` |
| Matrix | Matrix | Rows `dim_entity[entity_id]`; Columns month; Values `Total Consumption` |
| Detail | Table | date, entity, consumption, data quality flag |

Slicers:

- Date range.
- Entity.
- Weekend.

Design:

- Put daily trend as largest visual.
- Use monthly chart below or beside daily trend.
- Use matrix only if it remains readable.

Validation:

- Weekend slicer changes line chart and matrix.
- Date filter changes all trend visuals.

## 8.3 Page 3 - Anomaly Explorer

Purpose:

Menelusuri anomaly candidates dari Isolation Forest.

Visuals:

| Area | Visual | Fields / Measures |
|---|---|---|
| KPI | Card | `Anomaly Count` |
| KPI | Card | `Anomaly Rate` |
| KPI | Card | `Average Anomaly Score` |
| Main | Scatter chart | X `daily_consumption`; Y `anomaly_score`; Legend `scenario`; Details `entity_id` |
| Main | Bar chart | Axis `entity_id`; Value `Anomaly Count`; sort descending |
| Main | Bar chart | Axis month; Value `Anomaly Count` |
| Detail | Table | date, entity, scenario, anomaly score, rank, baseline agreement, weather context |

Slicers:

- Scenario.
- Anomaly flag.
- Entity.
- Date range.

Design:

- Default table filter: `anomaly_flag = 1`.
- Put anomaly score table below scatter for drill-through style review.
- Use red marks only for flagged anomalies.

Validation:

- Default scenario `balanced` shows expected anomaly rows.
- Strict has fewer anomalies than balanced.
- Sensitive has more anomalies than balanced.

## 8.4 Page 4 - Weather Impact

Purpose:

Membaca konteks cuaca tanpa klaim kausal berlebihan.

Visuals:

| Area | Visual | Fields / Measures |
|---|---|---|
| Main | Scatter chart | X `mean_temperature_c`; Y `daily_consumption`; color anomaly flag |
| Main | Scatter chart | X `rainfall_mm_model`; Y `daily_consumption`; color rainy day |
| Context | Line chart | Date axis; consumption and mean temperature |
| Detail | Table | hot/rainy anomaly dates with entity and anomaly score |
| Summary | Table | rows from `eda_summary` where `analysis_area = weather_context` |

Slicers:

- Rainy day.
- Hot day.
- Scenario.
- Date range.

Design:

- Label the page as "Weather Context", not "Weather Cause".
- Use orange for weather variables.
- Avoid cluttered dual-axis charts if labels become hard to read.

Validation:

- Rainy/hot slicers filter all weather visuals.
- Anomaly table remains connected to scenario slicer.

## 8.5 Page 5 - Meter / Building Ranking

Purpose:

Menentukan prioritas audit berdasarkan konsumsi, anomaly rate, dan scorecard.

Visuals:

| Area | Visual | Fields / Measures |
|---|---|---|
| KPI | Card | `Highest Priority Score` |
| KPI | Card | `Active Entity Count` |
| Main | Bar chart | Axis `entity_scorecard[entity_id]`; Value `total_consumption`; sort descending |
| Main | Bar chart | Axis `entity_scorecard[entity_id]`; Value `balanced_anomaly_rate`; sort descending |
| Detail | Table | entity priority rank, entity, total consumption, anomaly rate, peak consumption, priority score |
| Context | Bar chart | quality flag by entity |

Slicers:

- Entity.
- Building.
- Entity type.
- Scenario.

Design:

- Do not imply high consumption equals inefficiency.
- Title priority table as "Audit Priority Candidates".
- Use conditional formatting on `entity_priority_score`.

Validation:

- Top-ranked entity should appear first when sorted by `entity_priority_rank`.
- Entity slicer filters scorecard and anomaly visuals.

## 8.6 Page 6 - Data Quality and Methodology

Purpose:

Menjelaskan sumber data, kualitas, exclusion logic, dan method agar dashboard transparan.

Visuals:

| Area | Visual | Fields / Measures |
|---|---|---|
| KPI | Card | active meter count |
| KPI | Card | `Excluded Entity Count` |
| KPI | Card | `Data Quality Issue Count` |
| Main | Bar chart | `dim_entity[meter_quality_flag]` count |
| Main | Bar chart | `fact_energy_weather_daily[data_quality_flag]` count |
| Detail | Table | `data_quality_summary` |
| Detail | Table | `model_evaluation_summary` |
| Detail | Table | `insight_recommendation_matrix` |

Slicers:

- Data quality flag.
- Meter quality flag.
- Date range.

Design:

- Keep this page transparent and text-light.
- Use tables for source/methodology, not long paragraphs.
- Show excluded meters clearly.

Validation:

- Excluded meters are visible in `dim_entity`.
- Data quality issue counts match summary table.

---

# 9. Tooltip and Interaction Guidance

Recommended tooltip fields:

| Visual type | Tooltip fields |
|---|---|
| Consumption trend | date, total consumption, mean temperature, rainfall, hot day, rainy day, data quality flag |
| Anomaly scatter | date, entity, scenario, anomaly score, rank, daily consumption, rolling deviation, baseline agreement |
| Entity ranking | total consumption, anomaly count, anomaly rate, priority score, quality issue count |
| Weather visuals | temperature, rainfall, consumption, anomaly flag, weather context label |

Interaction best practice:

- Dimension slicers should filter both fact tables.
- Avoid visual interactions that make KPI cards misleading.
- Use **Edit interactions** if a slicer should not affect a methodology table.
- Keep anomaly page filtered to scenario-aware visuals.

---

# 10. Validation Checklist

Use this after dashboard build.

## 10.1 Data Import

- [ ] All required CSV files imported.
- [ ] Date fields are Date type.
- [ ] Numeric fields are numeric, not text.
- [ ] `entity_id`, `meter_id`, and `scenario` remain text.

## 10.2 Relationships

- [ ] `fact_energy_weather_daily` relates to `dim_date`.
- [ ] `fact_energy_weather_daily` relates to `dim_entity`.
- [ ] `fact_anomaly_scenarios` relates to `dim_date`.
- [ ] `fact_anomaly_scenarios` relates to `dim_entity`.
- [ ] `fact_anomaly_scenarios` relates to `dim_scenario`.
- [ ] All core relationships are many-to-one.
- [ ] Cross-filter direction is single.

## 10.3 Measures

- [ ] Consumption KPI measures return non-blank values.
- [ ] Anomaly Count changes when scenario slicer changes.
- [ ] Anomaly Rate is formatted as percentage.
- [ ] Data Quality Issue Count is visible on methodology page.
- [ ] Rainy Day Count and Hot Day Count return plausible values.

## 10.4 Pages

- [ ] Executive Overview exists.
- [ ] Consumption Trend exists.
- [ ] Anomaly Explorer exists.
- [ ] Weather Impact exists.
- [ ] Meter / Building Ranking exists.
- [ ] Data Quality and Methodology exists.

## 10.5 Slicers and Interactions

- [ ] Date slicer filters trend, anomaly, weather, and ranking visuals.
- [ ] Scenario slicer filters anomaly visuals.
- [ ] Entity slicer filters fact and scorecard visuals.
- [ ] Anomaly flag slicer works on Anomaly Explorer.
- [ ] Rainy/hot day slicers work on Weather Impact.
- [ ] Data quality slicers work on methodology page.

## 10.6 Interpretation Safety

- [ ] Weather page uses contextual wording.
- [ ] Anomaly labels use candidate/review wording.
- [ ] Data quality limitations are visible.
- [ ] Dashboard does not claim full-campus coverage.
- [ ] Dashboard does not claim supervised anomaly accuracy.

---

# 11. Screenshot Checklist

After validation, capture screenshots if later needed for report or presentation.

Recommended naming:

```text
outputs/powerbi/screenshots/01_executive_overview.png
outputs/powerbi/screenshots/02_consumption_trend.png
outputs/powerbi/screenshots/03_anomaly_explorer.png
outputs/powerbi/screenshots/04_weather_impact.png
outputs/powerbi/screenshots/05_meter_building_ranking.png
outputs/powerbi/screenshots/06_data_quality_methodology.png
```

Screenshot requirements:

- [ ] Executive Overview: balanced scenario, full date range.
- [ ] Consumption Trend: trend visible and readable.
- [ ] Anomaly Explorer: filtered to anomaly rows.
- [ ] Weather Impact: hot/rainy context visible.
- [ ] Meter / Building Ranking: entity scorecard visible.
- [ ] Data Quality and Methodology: excluded meters and quality flags visible.

---

# 12. Save and Handoff

Save dashboard as:

```text
outputs/powerbi/energy_anomaly_dashboard.pbix
```

Recommended final manual checks:

1. Close and reopen `.pbix`.
2. Click **Refresh**.
3. Confirm no broken relationships.
4. Confirm all visuals render.
5. Confirm scenario slicer works.
6. Confirm the file path remains inside repo under `outputs/powerbi`.

After `.pbix` is created, update:

- `cache/sessionHandoff.md`
- `cache/ImplementationPhase.md`

Record:

- `.pbix` path;
- build date;
- pages completed;
- validation result;
- screenshots path if created;
- known limitations.
