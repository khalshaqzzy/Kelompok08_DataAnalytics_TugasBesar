# Implementation Phase - OSEMN Finalization + Power BI Datamart

Last updated: 2026-06-15, Asia/Jakarta

Status markers used in this document:

| Status | Meaning |
|---|---|
| Not Started | Belum dikerjakan |
| In Progress | Sedang dikerjakan atau sudah sebagian |
| Done | Selesai dan sudah diverifikasi |
| Blocked | Tidak bisa lanjut tanpa input/perubahan eksternal |
| Deferred | Ditunda karena di luar scope fase ini |

---

# 0. Mandatory Working Rules

Dokumen ini adalah tracker implementasi utama untuk menyelesaikan pipeline dari kondisi saat ini menuju output final yang sesuai `cache/prd_energi_anomaly_powerbi.md` dan `cache/roadmap_improvement_energi_dashboard.md`.

Current scope guard:

- Perubahan teknis terbaru boleh menyentuh `scripts/`, `outputs/`, `Data_Acquisition/dataset/processed`, `notebooks/`, dan `cache/` sesuai instruksi user untuk final EDA, evidence matrix, notebook interpretation, dan dashboard readiness.
- Final academic report, presentation, slide deck, video/demo, README, Power BI `.pbix` automation, dan Power BI Service deployment tetap di luar scope kecuali diminta eksplisit.
- "Documentation out of scope" berarti final academic documentation/reporting artifacts di luar `cache/`; cache planning/handoff files tetap wajib diperbarui.
- PRD tetap diperlakukan sebagai source-of-truth dan tidak diubah kecuali diminta eksplisit.

Implementation update 2026-06-15:

- Scope teknis saat ini mencakup final EDA visuals, evidence tables, insight-recommendation matrix, dashboard validation checklist, formal notebook Explore/iNterpret sections, processed CSV outputs, cache tracker, dan penghapusan notebook builder scripts yang sudah tidak diperlukan.
- Final academic report, presentation, slide deck, video/demo, dan README tetap di luar scope.

Aturan wajib:

1. Setiap perubahan penting pada pipeline, dataset, notebook, model, visual, atau output Power BI-ready harus memperbarui dokumen ini.
2. Setiap perubahan penting juga harus memperbarui `cache/sessionHandoff.md` pada turn yang sama.
3. Jika path canonical, nama file output, schema dataset, atau keputusan modelling berubah, perubahan tersebut harus dicatat di bagian **Progress Log**, **Decisions**, dan **Known Issues** dokumen ini.
4. Sebelum melanjutkan pekerjaan pada sesi baru, baca berurutan:
   - `cache/sessionHandoff.md`
   - `cache/ImplementationPhase.md`
   - `cache/prd_energi_anomaly_powerbi.md`
   - `cache/roadmap_improvement_energi_dashboard.md`
5. Jangan membuat output final baru di root `dataset/processed`. Path canonical final adalah `Data_Acquisition/dataset`.
6. Notebook final aktif harus hanya satu file di `/notebooks`.
7. Logic pipeline utama harus berada di `/scripts`, bukan di notebook.
8. Power BI Desktop boleh dibangun manual dari CSV final; automation `.pbix` tidak diwajibkan dalam fase ini.
9. Branch dan commit message harus behavior-based, tidak boleh mengandung `/`, dan tidak boleh mereferensikan phase, milestone, sprint, atau nomor fase.
10. Notebook aktif hanya wajib mencakup output OSEMN yang sudah tersedia dan terverifikasi. Notebook harus ditulis formal seperti laporan analitis, dipisahkan berdasarkan OSEMN yang sudah siap, dan tidak boleh memakai bahasa development seperti phase, backlog, atau plan.
11. Progress teknis berikutnya harus mengevaluasi apakah notebook perlu diperbarui. Notebook hanya diperluas setelah output baru untuk EDA, model, atau interpretasi sudah tersedia dan layak ditulis secara formal.

---

# 1. Locked Decisions

| Area | Decision |
|---|---|
| Canonical dataset path | `Data_Acquisition/dataset` |
| Canonical processed path | `Data_Acquisition/dataset/processed` |
| Canonical profile path | `Data_Acquisition/dataset/profile_hkust_hko` |
| Main analytical grain | T1440 daily, meter-level selected subset |
| Main selected building | `Cheng_Yu_Tung_Building` |
| Main selected meters | `D0849`, `D0848`, `D0854`, `D0853`, `D0862`, `D0857`, `D0851`, `D0861`, `D0852`, `D0860`, `D0850`, `D0865` |
| Primary model | Isolation Forest anomaly detection |
| Baselines | IQR and Z-score |
| Scenario model | `strict=0.03`, `balanced=0.05`, `sensitive=0.10` |
| Default dashboard scenario | `balanced` |
| Notebook policy | Only one active notebook in `/notebooks` |
| Old notebook policy | Archive old notebooks to `cache/archive/notebooks` |
| Current active branch | `feat-energy-dashboard-evidence` |
| Current planned commit message | `Remove notebook builder scripts` |
| Power BI scope | Manual `.pbix` build plan, CSV datamart, measures, relationships, page checklist |
| Out of scope for current branch | Final academic report/documentation, slide deck, presentation script, video/demo, README, and automated Power BI Desktop manipulation |

Notebook scope note:

- Notebook aktif `notebooks/energy_analytics_osemn.ipynb` saat ini berisi O - Obtain, S - Scrub, E - Explore lengkap berbasis final EDA visuals, M - Model, N - iNterpret, Kesiapan Data Power BI, dan Catatan Keterbatasan.
- Notebook memuat iNterpret setelah `insight_recommendation_matrix.csv` tersedia dan terverifikasi.
- Notebook builder scripts sudah dihapus setelah notebook final tersedia: `scripts/build_osemn_notebook.py` dan `scripts/build_exploration_notebook.py`.
- Notebook tidak lagi diregenerate melalui script. Validasi notebook berikutnya dilakukan langsung pada file notebook atau dengan pemeriksaan programatik `nbformat`.
- Notebook tidak boleh menyebut istilah development seperti phase, backlog, atau implementation plan.
- Setiap progress analisis berikutnya harus mengevaluasi dan memperbarui notebook aktif jika ada output baru yang relevan untuk O, S, E, M, atau N.
- EDA di notebook harus diperluas secara bertahap sampai lengkap: trend harian, tren bulanan, weekday/weekend, kontribusi/Pareto meter, konteks cuaca, kualitas data, dan interpretasi singkat per visual setelah output final tersedia.

---

# 2. Current-State Analysis

## 2.1 Existing Inputs and Artifacts

| Artifact | Current Status | Notes |
|---|---|---|
| `cache/prd_energi_anomaly_powerbi.md` | Done | PRD v1.1 for anomaly detection and Power BI dashboard |
| `cache/roadmap_improvement_energi_dashboard.md` | Done | Roadmap from Obtain through Power BI |
| `cache/sessionHandoff.md` | In Progress | Needs new rule requiring this file to be updated |
| `notebooks/eksplorasi_hkust_hko.ipynb` | In Progress | Existing notebook for HKUST/HKO exploration |
| `Data_Acquisition/01_explore_and_select_subset.ipynb` | In Progress | Existing notebook for subset selection and TTL use |
| `scripts/download_hko_open_data.py` | In Progress | Existing HKO downloader |
| `scripts/profile_datasets.py` | In Progress | Existing profiling script |
| `scripts/explore_energy_weather.py` | In Progress | Existing EDA/model baseline script, still uses older aggregate flow |
| `scripts/select_t1440_subset.py` | In Progress | Existing T1440 profiling, TTL mapping, selected subset workflow |
| `scripts/build_energy_weather_master.py` | In Progress | Existing energy + weather join script |

## 2.2 Existing Processed Outputs

| File | Current Status | Current Role |
|---|---|---|
| `Data_Acquisition/dataset/processed/dim_entity_t1440.csv` | In Progress | Entity mapping draft, not final `dim_entity.csv` |
| `Data_Acquisition/dataset/processed/selected_t1440_meters.csv` | Done | Selected meter inventory |
| `Data_Acquisition/dataset/processed/fact_energy_t1440_selected_long.csv` | In Progress | Long energy fact before final datamart |
| `Data_Acquisition/dataset/processed/master_energy_t1440_selected_daily.csv` | In Progress | Energy master table |
| `Data_Acquisition/dataset/processed/hko_weather_daily.csv` | In Progress | Weather daily table |
| `Data_Acquisition/dataset/processed/master_energy_weather_t1440_selected_daily.csv` | In Progress | Joined energy-weather master table |
| `Data_Acquisition/dataset/t1440_meter_inventory_with_decision.csv` | Done | 26-meter inventory with decisions and quality flags |
| `Data_Acquisition/dataset/t1440_subset_selection_justification.md` | Done | Subset justification |

## 2.3 Verified Data Facts

| Metric | Value |
|---|---:|
| T1440 meter inventory | 26 meters |
| Selected main subset | 12 active meters |
| Selected fact rows before first-reading removal | 10,536 rows |
| Final daily rows after first-reading removal | 10,524 rows |
| Selected date range after differencing | 2022-01-02 to 2024-05-27 |
| HKO weather date range | 2022-01-01 to 2024-05-27 |
| HKO weather days | 878 days |
| Missing rainfall days | 5 days |
| Missing global solar radiation days | 1 day |
| Duplicate `date + meter_id` in current master | 0 |
| Selected meter negative consumption rows | 0 |

Problematic T1440 meters to keep visible in data quality outputs:

| Category | Meters |
|---|---|
| Zero constant | `D0821`, `D0823`, `D0844`, `D0847` |
| Near-zero / low signal | `D0863`, `D0864`, `D0846` |
| Short coverage | `D0816` |

## 2.4 Gap Against PRD and Roadmap

| Required Output / Capability | Current Status | Gap |
|---|---|---|
| `fact_energy_weather_daily.csv` | Done | No gap; final Date x Entity fact table exists and is key-unique |
| `fact_anomaly_scenarios.csv` | Done | No gap; scenario-based Isolation Forest output exists |
| `dim_date.csv` | Done | No gap; Power BI date dimension exists |
| `dim_entity.csv` | Done | No gap; includes all 26 T1440 meters with selection and quality fields |
| `dim_scenario.csv` | Done | No gap; strict, balanced, and sensitive scenarios exist |
| `data_quality_summary.csv` | Done | No gap; quality summary table exists |
| `data_dictionary_energy_dashboard.csv` | Done | No gap; schema dictionary includes final datamart, model, EDA, and dashboard evidence tables |
| `final_data_sources.md` | Done | No gap; canonical source manifest exists |
| `model_evaluation_summary.csv` | Done | No gap; evaluation without labels exists |
| `anomaly_case_review.csv` | Done | No gap; top anomaly case review exists |
| `entity_scorecard.csv` | Done | No gap; audit-priority scorecard exists |
| Final OSEMN notebook | Done | No gap; one active notebook in `/notebooks` with O, S, E, M, and N sections |
| Old notebook archive | Done | No gap; old notebooks archived under `cache/archive/notebooks` |
| Final EDA plots | Done | No gap; dashboard-aligned visuals exist under `outputs/eda/final` |
| Manual Power BI checklist | Done | No gap for checklist; actual `.pbix` build remains manual outside Python automation |

## 2.5 Alignment Audit Against PRD, Roadmap, and Grading Guide

Audit ini mencatat kesesuaian kondisi saat ini terhadap PRD, roadmap improvement, dan panduan penilaian tugas besar. Scope audit adalah repo pipeline/dashboard readiness; final academic report, presentation, video/demo, dan README tidak dikerjakan pada task cache-only ini.

### 2.5.1 Alignment Summary

| Area | Alignment Status | Evidence | Improvement Needed |
|---|---|---|---|
| Problem framing | Mostly aligned | Topik energi dan efisiensi gedung/kampus sudah konsisten dengan PRD dan roadmap | Tegaskan scope sebagai selected meter/building-level HKUST case study, bukan full-campus generalization |
| Obtain | Strong | HKUST sebagai primary source, HKO sebagai supporting source, TTL sebagai metadata entity, source manifest final tersedia | Perkuat analytical question matrix dan source-to-output traceability di cache tracker |
| Scrub | Strong | Canonical datamart, quality flags, imputation flags, selected/excluded meter decisions, data dictionary | Tambahkan summary pembersihan yang langsung memetakan missing, duplicates, types, outliers, integration, feature engineering |
| Explore | Aligned | Final EDA visuals, `eda_summary.csv`, `visual_interpretation_summary.csv`, and notebook Explore expansion are complete | Actual Power BI visual validation remains manual |
| Model | Aligned | Scenario outputs, baseline agreement, evaluation without labels, and case review are complete | No supervised labels are available |
| iNterpret | Aligned | `insight_recommendation_matrix.csv` provides evidence, target user, priority, action, and limitation fields | Final academic narrative remains out of scope |
| Power BI readiness | Aligned for repo outputs | Star schema, model outputs, EDA evidence, relationship plan, DAX draft, page checklist, and validation checklist are available | Manual `.pbix` build remains the next external step |
| Notebook policy | Aligned after correction | Notebook formal dan hanya memuat output tersedia | Jangan memaksa bagian Model/iNterpret sebelum output final tersedia |

### 2.5.2 Rubric-Based Gap Analysis

| Rubric Area | Current Readiness | Risk to Score | Cache-Recorded Improvement |
|---|---|---|---|
| Problem Framing and Relevance | Medium-High | Scope HKUST/Hong Kong bisa terlihat kurang relevan jika diklaim terlalu luas | Frame sebagai transferable campus/building energy analytics case study dan selected-building subset |
| O - Obtain | High | Source documentation bisa tersebar antara PRD, roadmap, data dictionary, dan source manifest | Maintain `final_data_sources.md` as canonical source manifest and mirror key scope notes here |
| S - Scrub | High | Treatment data quality kuat tetapi perlu ringkasan naratif untuk penilaian | Keep explicit quality treatment table and ensure future notebook/report text follows it |
| E - Explore | High | Final visual evidence and notebook Explore section are complete | Maintain visual interpretation table for Power BI and notebook traceability |
| M - Model | High | Scenario-based Isolation Forest, IQR/Z-score baseline, evaluation without labels, and case review are complete | Keep no-ground-truth limitation explicit |
| N - iNterpret | High | Insight/recommendation matrix exists and is evidence-backed | Final academic narrative remains separate and out of scope |
| System/Dashboard | High for repo readiness | Datamart, model, EDA evidence, and dashboard validation checklist are ready | Manual Power BI Desktop build and screenshot validation remain next |
| Report/Presentation/Demo | Out of scope for current task | Tetap dibutuhkan untuk final grading, tetapi tidak dikerjakan di task ini | Track as external/future deliverable only if requested later |
| Teamwork/AI Ethics | Out of scope for current task | Belum dibahas pada implementation tracker teknis | Track as external/future deliverable only if requested later |

### 2.5.3 Scope Correction Required

The analysis must be described as:

- selected T1440 daily meter-level analysis;
- selected active meters primarily mapped to `Cheng_Yu_Tung_Building`;
- HKO daily weather as contextual support, not a causal proof engine;
- Power BI-ready analytical dataset for monitoring and decision support.

The analysis must not be described as:

- full-campus HKUST coverage;
- complete building comparison across all HKUST buildings;
- supervised anomaly detection with ground-truth labels;
- production monitoring system;
- final academic report/presentation/video deliverable within this cache-only task.

### 2.5.4 Improvement Backlog to Preserve

| Backlog Item | Priority | Output Target | Notebook Impact | Scope Note |
|---|---|---|---|---|
| EDA completeness | P0 | final EDA plots and `eda_summary.csv` | Expand formal Explore section after outputs exist | Repo pipeline/dashboard scope |
| Feature engineering readiness | P0 | engineered feature table/columns and feature dictionary updates | Explain engineered variables only after they exist in outputs | Repo pipeline/model/dashboard scope |
| Interpretation per visual | P0 | visual interpretation notes or summary table | Add concise interpretation under each EDA result | Repo pipeline/dashboard scope |
| Model readiness | P0 | `fact_anomaly_scenarios.csv`, `model_evaluation_summary.csv` | Add Model section only after final model outputs exist | Repo pipeline/dashboard scope |
| Baseline agreement | P0 | IQR/Z-score agreement fields and evaluation summary | Include method comparison in Model section | Repo pipeline/dashboard scope |
| Anomaly case review | P0 | `anomaly_case_review.csv` | Add selected case review after output exists | Repo pipeline/dashboard scope |
| Interpretation readiness | P0 | insight-recommendation matrix | Add iNterpret section only after evidence matrix exists | Repo pipeline/dashboard scope |
| Dashboard validation | P1 | Power BI relationship, DAX, slicer, page checklist | Mention dashboard-ready structure only; no `.pbix` automation required | Repo dashboard scope |
| Scope correction | P0 | updated cache tracker notes | Maintain limitations section in notebook | Required to avoid overclaiming |
| Notebook policy | P0 | formal notebook updated incrementally | Never add incomplete OSEMN sections or development language | Required by user decision |

### 2.5.5 Feature Improvement Candidates

These are feature additions for future implementation work. They are recorded here only; this cache-only task does not implement them.

| Feature Candidate | Value | Acceptance Target |
|---|---|---|
| Analytical question matrix | Makes PRD and rubric traceable to outputs | Each question maps to dataset table, visual/model output, and dashboard page |
| Feature engineering layer | Makes EDA/model/dashboard more explainable | Feature groups are documented, validated, and reusable across EDA, model, and Power BI |
| Final EDA summary dataset | Makes Explore evidence reusable | Summary table includes trend, contribution, weekday/weekend, weather, and quality observations |
| Entity priority score | Converts analysis into actionable audit ranking | Score combines consumption contribution, anomaly rate, and quality status |
| Anomaly stability flag | Improves model defensibility | Cases flagged in multiple scenarios are identifiable |
| Weather context bands | Prevents weak causal claims | Dashboard distinguishes hot/rainy/contextual days from anomaly drivers |
| Data quality methodology page | Makes limitations transparent | Dashboard includes excluded meters, imputed weather, and model eligibility counts |
| Insight-recommendation matrix | Strengthens iNterpret scoring | At least 3 insights and 3 recommendations have evidence, target user, priority, and limitation |

### 2.5.6 Feature Engineering Plan to Add to Implementation Phases

Feature engineering must be treated as a traceable layer between Scrub, Explore, Model, and Power BI. It should not be hidden inside notebook cells or model code.

| Feature Family | Example Fields | Main Use | Required Treatment |
|---|---|---|---|
| Consumption level | `daily_consumption`, `log_daily_consumption`, `consumption_per_selected_meter_day` | EDA, model, ranking | Preserve original `daily_consumption`; derived transforms must be clearly named |
| Rolling consumption | `rolling_mean_7d`, `rolling_std_7d`, `deviation_from_rolling_mean_7d`, `pct_deviation_from_rolling_mean_7d` | Model, anomaly case review | Calculate per `entity_id`, ordered by `date`; avoid using future rows |
| Lag consumption | `lag_1d_consumption`, `lag_7d_consumption`, `diff_from_lag_7d` | Model diagnostics, trend interpretation | Calculate per `entity_id`; first lag rows become non-eligible if required |
| Calendar | `is_weekend`, `month`, `quarter`, `day_of_week_num`, `year_month`, `is_month_start`, `is_month_end` | EDA, slicers, model | Use `dim_date` as source of truth |
| Weather raw/context | `mean_temperature_c`, `relative_humidity_pct`, `rainfall_mm`, `global_solar_radiation_mj_m2`, `mean_wind_speed_kmh` | EDA, dashboard context | Preserve raw values and completeness columns |
| Weather model-safe | `rainfall_mm_model`, `global_solar_radiation_mj_m2_model`, weather imputation flags | Model | Use only imputed/model-safe fields for model features |
| Weather engineered | `cooling_degree_day_24c`, `is_hot_day_28c`, `is_rainy_day`, `temperature_band`, `rainfall_band` | EDA, model, slicers | Define thresholds explicitly in data dictionary |
| Entity contribution | `entity_total_consumption`, `entity_consumption_rank`, `entity_contribution_pct`, `entity_cumulative_contribution_pct` | EDA, ranking, recommendations | Compute from eligible selected fact and document denominator |
| Quality and eligibility | `meter_quality_flag`, `data_quality_flag`, `is_model_eligible`, `feature_complete_flag` | Filtering, methodology page | Use for filtering/interpretation, not as primary model signal |
| Scenario stability | `scenario_anomaly_count`, `is_stable_anomaly_candidate`, `baseline_agreement_count` | Interpretation, dashboard | Build after model outputs exist |

Feature rules:

1. All reusable feature logic belongs in `/scripts`, not notebook cells.
2. Every engineered feature used in final outputs must be documented in `data_dictionary_energy_dashboard.csv`.
3. Feature generation must preserve raw source fields where practical.
4. Model features must be numeric and non-null for eligible rows.
5. Quality flags can filter or explain model rows, but should not be used as primary anomaly detection features.
6. Features that use future information are not allowed for anomaly detection.
7. If a feature is dashboard-only, it should be labelled as interpretation/slicer support, not model input.
8. Notebook may describe engineered features only after the corresponding columns or outputs exist.

Feature acceptance criteria:

1. Feature columns have stable names and documented definitions.
2. Rolling and lag features are calculated within each `entity_id`.
3. No model feature has missing values for `is_model_eligible = 1` rows.
4. Raw weather fields and model-safe weather fields remain distinguishable.
5. Feature dictionary or data dictionary identifies source, formula, intended use, and limitations.

---

# 3. Target Final Outputs

## 3.1 Canonical Directory Layout

```text
cache/
  ImplementationPhase.md
  sessionHandoff.md
  archive/
    notebooks/

notebooks/
  energy_analytics_osemn.ipynb

scripts/
  config.py
  io_utils.py
  hko_weather.py
  hkust_t1440.py
  ttl_entity_mapping.py
  build_powerbi_datamart.py
  feature_engineering.py
  model_anomaly_scenarios.py
  build_final_eda.py

Data_Acquisition/
  dataset/
    processed/
      hko_weather_daily.csv
      fact_energy_weather_daily.csv
      fact_anomaly_scenarios.csv
      dim_date.csv
      dim_entity.csv
      dim_scenario.csv
      feature_engineering_summary.csv
      data_quality_summary.csv
      data_dictionary_energy_dashboard.csv
      model_evaluation_summary.csv
      anomaly_case_review.csv
      entity_scorecard.csv
    profile_hkust_hko/
      final_data_sources.md

outputs/
  eda/
    final/
```

## 3.2 Power BI Star Schema

| Table | Grain | Required Key |
|---|---|---|
| `fact_energy_weather_daily` | `date x entity_id` | `date`, `entity_id` |
| `fact_anomaly_scenarios` | `date x entity_id x scenario` | `date`, `entity_id`, `scenario` |
| `dim_date` | `date` | `date` |
| `dim_entity` | `entity_id` | `entity_id` |
| `dim_scenario` | `scenario` | `scenario` |

Power BI relationships:

| From | To | Key |
|---|---|---|
| `fact_energy_weather_daily` | `dim_date` | `date` |
| `fact_energy_weather_daily` | `dim_entity` | `entity_id` |
| `fact_anomaly_scenarios` | `dim_date` | `date` |
| `fact_anomaly_scenarios` | `dim_entity` | `entity_id` |
| `fact_anomaly_scenarios` | `dim_scenario` | `scenario` |

---

# 4. Implementation Phases

## Phase 0 - Governance and Planning Artifacts

Status: Done

Goal:

Create implementation governance so all subsequent work is traceable, resumable, and aligned with PRD/roadmap.

Deliverables:

| Deliverable | Status |
|---|---|
| `cache/ImplementationPhase.md` | Done |
| Updated `cache/sessionHandoff.md` with progress tracking rules | Done |

Subplan:

1. Create this document.
2. Add mandatory rules to the top of `sessionHandoff.md`.
3. Record canonical decisions.
4. Add current-state analysis and gap checklist.
5. Add runbook, verification plan, Power BI manual build plan, and progress log.

Acceptance criteria:

1. `ImplementationPhase.md` exists and includes phases, subplans, outputs, runbook, tests, and progress log.
2. `sessionHandoff.md` explicitly says `ImplementationPhase.md` must be updated with project progress.
3. Both files state the canonical dataset path is `Data_Acquisition/dataset`.

---

## Phase 1 - Script Consolidation

Status: Done

Goal:

Move reusable logic from notebooks into scripts and make scripts the source of truth for pipeline execution.

Deliverables:

| Deliverable | Status | Purpose |
|---|---|---|
| `scripts/config.py` | Done | Project constants, paths, dates, scenarios, selected meters |
| `scripts/io_utils.py` | Done | Read/write helpers and common validation utilities |
| `scripts/hko_weather.py` | Done | Parse HKO raw CSV into daily weather |
| `scripts/hkust_t1440.py` | Done | Parse T1440 Excel, differencing, profiling, selected subset |
| `scripts/ttl_entity_mapping.py` | Done | Parse TTL metadata into entity mapping |
| Existing scripts compatibility note | Done | Canonical scripts supersede older flows for new final outputs |

Subplan:

1. Create `config.py`.
   - Define `ROOT`, `DATA_ROOT`, `RAW_HKUST_DIR`, `HKO_RAW_DIR`, `PROCESSED_DIR`, `PROFILE_DIR`, `OUTPUT_DIR`.
   - Define `PROJECT_START = 2022-01-01` and `PROJECT_END = 2024-05-27`.
   - Define selected building and selected meter list.
   - Define scenario dictionary:
     - `strict: 0.03`
     - `balanced: 0.05`
     - `sensitive: 0.10`
2. Create `io_utils.py`.
   - Add `ensure_dir(path)`.
   - Add `read_csv_dates(path, date_columns)`.
   - Add `write_csv(df, path)`.
   - Add duplicate-key assertion helper.
   - Add required-column assertion helper.
3. Refactor HKO parsing into `hko_weather.py`.
   - Preserve existing parsing rules.
   - Keep completeness columns.
   - Preserve missing values; do not silently drop incomplete rows.
4. Refactor HKUST T1440 parsing into `hkust_t1440.py`.
   - Parse Excel files.
   - Normalize `date`, `meter_reading`, `meter_id`.
   - Calculate `daily_consumption` with per-meter `diff()`.
   - Set negative diff to missing.
   - Produce inventory and selected long fact.
5. Refactor TTL parsing into `ttl_entity_mapping.py`.
   - Reuse current regex/BFS approach unless it fails validation.
   - Output entity mapping for all 26 T1440 meters.
6. Mark old scripts with a short header note if they are no longer canonical.

Acceptance criteria:

1. `python -m py_compile scripts/*.py` passes.
2. No final script writes to root `dataset/processed`.
3. Current data outputs can be regenerated without running notebook cells manually.
4. All final scripts use canonical `Data_Acquisition/dataset` paths.

---

## Phase 2 - Notebook Unification

Status: Done

Goal:

Create one final OSEMN notebook and archive old notebooks.

Deliverables:

| Deliverable | Status |
|---|---|
| `notebooks/energy_analytics_osemn.ipynb` | Done |
| `cache/archive/notebooks/eksplorasi_hkust_hko.ipynb` | Done |
| `cache/archive/notebooks/01_explore_and_select_subset.ipynb` | Done |
| Remove old active notebook from `Data_Acquisition` after archive | Done |

Notebook structure:

1. Formal project overview.
2. O - Obtain: source data and analytical scope.
3. S - Scrub: cleaning, integration, quality treatment, and datamart structure.
4. E - Explore: early consumption and data quality summaries.
5. Power BI readiness: final CSV list and relationship-ready tables.
6. Catatan keterbatasan.

Rules:

1. Notebook must call functions or scripts from `/scripts`.
2. Notebook must not contain long duplicated parsing/model functions.
3. Notebook must execute end-to-end with 0 error outputs.
4. `/notebooks` must contain exactly one active notebook after this phase.

Acceptance criteria:

1. Old notebooks archived.
2. Final notebook runs without errors.
3. Final notebook covers only completed OSEMN sections supported by generated outputs.
4. Final notebook references final datamart outputs.

---

## Phase 3 - Power BI Datamart

Status: Done

Goal:

Build final Power BI-ready star schema tables aligned to PRD v1.1.

Deliverables:

| Deliverable | Status |
|---|---|
| `Data_Acquisition/dataset/processed/fact_energy_weather_daily.csv` | Done |
| `Data_Acquisition/dataset/processed/dim_date.csv` | Done |
| `Data_Acquisition/dataset/processed/dim_entity.csv` | Done |
| `Data_Acquisition/dataset/processed/dim_scenario.csv` | Done |
| `Data_Acquisition/dataset/processed/data_quality_summary.csv` | Done |
| `Data_Acquisition/dataset/processed/data_dictionary_energy_dashboard.csv` | Done |
| `Data_Acquisition/dataset/profile_hkust_hko/final_data_sources.md` | Done |

Subplan:

1. Build `dim_date.csv`.
   - Date range: 2022-01-01 to 2024-05-27.
   - Columns:
     - `date`
     - `year`
     - `quarter`
     - `month`
     - `month_name`
     - `day`
     - `day_of_week`
     - `day_of_week_num`
     - `is_weekend`
     - `year_month`
2. Build `dim_entity.csv`.
   - Include all 26 T1440 meters.
   - Columns:
     - `entity_id`
     - `meter_id`
     - `meter_name`
     - `entity_type`
     - `building`
     - `floor`
     - `room_or_equipment`
     - `usage_type`
     - `mapping_status`
     - `meter_quality_flag`
     - `selection_decision`
     - `is_selected_main_subset`
     - `is_model_eligible_entity`
     - `coverage_ratio`
     - `total_consumption`
     - `rank_total_consumption`
3. Build `dim_scenario.csv`.
   - Rows:
     - `strict`, contamination `0.03`, default flag `0`
     - `balanced`, contamination `0.05`, default flag `1`
     - `sensitive`, contamination `0.10`, default flag `0`
   - Columns:
     - `scenario`
     - `contamination`
     - `scenario_label`
     - `scenario_description`
     - `is_default`
4. Build `fact_energy_weather_daily.csv`.
   - Grain: one row per selected meter per date after first reading.
   - Key: `date + entity_id`.
   - Columns:
     - `date`
     - `entity_id`
     - `meter_id`
     - `entity_type`
     - `building`
     - `floor`
     - `room_or_equipment`
     - `meter_reading`
     - `daily_consumption`
     - weather variables
     - weather completeness columns
     - engineered weather flags
     - calendar columns
     - `meter_quality_flag`
     - `data_quality_flag`
     - `is_model_eligible`
5. Data quality rules.
   - `first_reading`: first row per meter before differencing; excluded from fact final or flagged if retained.
   - `negative_diff`: negative diff set to missing and excluded from model.
   - `zero_constant`: excluded from model.
   - `near_zero_low_signal`: excluded from model.
   - `short_coverage`: excluded from model.
   - `missing_weather`: not eligible for model unless imputed columns are added.
   - `valid`: selected active meter, valid consumption, valid model weather fields.
6. Missing weather treatment.
   - Keep original weather fields unchanged.
   - Add model-safe fields if needed:
     - `rainfall_mm_model`
     - `global_solar_radiation_mj_m2_model`
   - Record imputation method in data dictionary.
   - Recommended treatment:
     - rainfall missing -> `0` only for model field and flag as imputed;
     - solar radiation missing -> median by month or global median for model field and flag as imputed.
7. Generate `data_quality_summary.csv`.
   - Summary by quality flag.
   - Summary by selected/excluded decision.
   - Missing weather summary.
   - Duplicate-key checks.
8. Generate `data_dictionary_energy_dashboard.csv`.
   - One row per final column.
   - Include table name, column name, data type, description, source, treatment notes.
9. Generate `final_data_sources.md`.
   - HKUST source.
   - HKO source.
   - Local canonical paths.
   - Period.
   - Scope limitations.

Acceptance criteria:

1. `fact_energy_weather_daily(date, entity_id)` has no duplicates.
2. `dim_date.date` has no duplicates.
3. `dim_entity.entity_id` has no duplicates.
4. `dim_scenario.scenario` has no duplicates.
5. All selected meters map to `Cheng_Yu_Tung_Building`.
6. Excluded meters remain visible in `dim_entity`.
7. All PRD-required datamart tables exist.

---

## Phase 3.5 - Feature Engineering Readiness

Status: Done

Goal:

Create a reusable, documented feature layer that supports final EDA, scenario-based anomaly modelling, anomaly interpretation, and Power BI slicers without duplicating logic in the notebook.

Deliverables:

| Deliverable | Status | Purpose |
|---|---|---|
| Feature engineering logic in canonical scripts | Done | `scripts/feature_engineering.py` generates reusable features outside notebook cells |
| Updated `fact_energy_weather_daily.csv` feature columns | Done | Added dashboard/model-safe features at the daily entity grain |
| Feature dictionary rows in `data_dictionary_energy_dashboard.csv` | Done | Documented formulas, sources, use cases, and limitations |
| Feature completeness checks | Done | Confirmed 10,420 rows with complete model feature set |
| `feature_engineering_summary.csv` | Done | Summarizes engineered feature coverage and missingness |

Verified output facts:

| Metric | Value |
|---|---:|
| `fact_energy_weather_daily` rows | 10,524 |
| Duplicate `date + entity_id` after feature update | 0 |
| Feature-complete rows | 10,420 |
| `feature_engineering_summary.csv` rows | 29 |
| Model feature set version | `energy_anomaly_v1` |

Recommended feature groups:

| Group | Candidate Features | Used By |
|---|---|---|
| Consumption transform | `log_daily_consumption`, `consumption_rank_within_entity`, `consumption_percentile_within_entity` | EDA, anomaly review |
| Rolling window | `rolling_mean_7d`, `rolling_std_7d`, `deviation_from_rolling_mean_7d`, `pct_deviation_from_rolling_mean_7d` | Model, case review |
| Lag comparison | `lag_1d_consumption`, `lag_7d_consumption`, `diff_from_lag_1d`, `diff_from_lag_7d` | Model diagnostics, trend interpretation |
| Calendar | `is_weekend`, `month`, `quarter`, `day_of_week_num`, `year_month`, `is_month_start`, `is_month_end` | EDA, model, Power BI slicers |
| Weather context | `cooling_degree_day_24c`, `is_hot_day_28c`, `is_rainy_day`, `temperature_band`, `rainfall_band` | EDA, model, dashboard |
| Weather model-safe | `rainfall_mm_model`, `global_solar_radiation_mj_m2_model`, imputation flags | Model |
| Entity contribution | `entity_contribution_pct`, `entity_cumulative_contribution_pct`, `entity_consumption_rank` | EDA, entity scorecard |
| Quality/eligibility | `feature_complete_flag`, `is_model_eligible`, quality flag rollups | Filtering, methodology page |

Subplan:

1. Define feature ownership.
   - Calendar features come from `dim_date`.
   - Entity contribution features come from selected meter-level fact rows.
   - Rolling and lag features are computed per `entity_id`, ordered by `date`.
   - Weather model-safe features preserve original weather values and add separate imputed/model columns.
2. Add formulas to data dictionary before or during implementation.
3. Generate features in scripts, not notebook cells.
4. Validate feature completeness for model-eligible rows.
5. Separate feature usage:
   - EDA features for explanation and visualization;
   - model features for Isolation Forest;
   - dashboard features for slicers, tooltips, and methodology page.
6. Prevent leakage.
   - Do not use future consumption values.
   - Do not use anomaly labels or scenario outputs as model input.
   - Do not use quality flags as primary anomaly model features.
7. Keep raw and engineered fields side by side.
   - Raw weather fields remain unchanged.
   - Imputed/model-safe weather fields have explicit suffixes and flags.
8. Update notebook only after feature outputs exist.
   - Explain formulas and uses in formal analytical language.
   - Avoid mentioning development phase, backlog, or implementation plan in the notebook.

Acceptance criteria:

1. All engineered features used by EDA, model, or dashboard are documented.
2. Rolling and lag features are calculated within each `entity_id`.
3. No future information is used for model features.
4. Model-eligible rows have non-null numeric values for all selected model features.
5. Dashboard-only features are not misrepresented as model inputs.
6. `data_dictionary_energy_dashboard.csv` identifies each engineered feature's source, formula, use case, and limitation.

---

## Phase 4 - Anomaly Modelling

Status: Done

Goal:

Create defensible anomaly detection outputs for Power BI and interpretation.

Deliverables:

| Deliverable | Status |
|---|---|
| `Data_Acquisition/dataset/processed/fact_anomaly_scenarios.csv` | Done |
| `Data_Acquisition/dataset/processed/model_evaluation_summary.csv` | Done |
| `Data_Acquisition/dataset/processed/anomaly_case_review.csv` | Done |
| `Data_Acquisition/dataset/processed/entity_scorecard.csv` | Done |

Verified output facts:

| Metric | Value |
|---|---:|
| Model-eligible feature-complete rows | 10,420 |
| `fact_anomaly_scenarios.csv` rows | 31,260 |
| Duplicate `date + entity_id + scenario` | 0 |
| Strict anomaly count / rate | 313 / 0.030038 |
| Balanced anomaly count / rate | 521 / 0.050000 |
| Sensitive anomaly count / rate | 1,042 / 0.100000 |
| `anomaly_case_review.csv` rows | 20 |
| `entity_scorecard.csv` rows | 12 |

Prerequisite:

Phase 3.5 feature engineering readiness should be completed before final Isolation Forest output is treated as dashboard-ready.

Feature set:

| Group | Features |
|---|---|
| Consumption | `daily_consumption`, `rolling_mean_7d`, `rolling_std_7d`, `deviation_from_rolling_mean_7d`, `pct_deviation_from_rolling_mean_7d` |
| Calendar | `is_weekend`, `month`, `day_of_week_num` |
| Weather | `mean_temperature_c`, `relative_humidity_pct`, `rainfall_mm_model`, `global_solar_radiation_mj_m2_model`, `mean_wind_speed_kmh` |
| Engineered weather | `cooling_degree_day_24c`, `is_rainy_day`, `is_hot_day_28c` |

Do not use as model features:

1. Raw `meter_id` as ordinal number.
2. `data_quality_flag`.
3. `meter_quality_flag`.
4. Completeness string columns.
5. Non-imputed weather fields with missing values.

Subplan:

1. Load `fact_energy_weather_daily.csv`.
2. Filter `is_model_eligible = 1`.
3. Create rolling features per `entity_id`, ordered by date.
4. Add IQR baseline per entity or across selected eligible fact.
5. Add Z-score baseline.
6. Run Isolation Forest for each scenario:
   - `strict`, contamination `0.03`
   - `balanced`, contamination `0.05`
   - `sensitive`, contamination `0.10`
7. Export `fact_anomaly_scenarios.csv`.
8. Generate `model_evaluation_summary.csv`.
   - scenario
   - contamination
   - eligible row count
   - anomaly count
   - anomaly rate
   - IQR agreement count/rate
   - Z-score agreement count/rate
   - note: no ground-truth labels
9. Generate `anomaly_case_review.csv`.
   - top cases from balanced scenario by anomaly score.
   - include date, entity, consumption, rolling deviation, weather, quality, baseline flags.
10. Generate `entity_scorecard.csv`.
   - total consumption
   - average daily consumption
   - peak daily consumption
   - anomaly count and rate by balanced scenario
   - model eligible days
   - data quality status
   - priority score

Acceptance criteria:

1. `fact_anomaly_scenarios(date, entity_id, scenario)` has no duplicates.
2. All eligible rows have one output per scenario.
3. `anomaly_score` is non-null for eligible rows.
4. `balanced` scenario is present and marked as default in `dim_scenario`.
5. Scenario anomaly rates are close to configured contamination.
6. Evaluation clearly says there is no supervised ground truth.

---

## Phase 5 - Final EDA and Dashboard Preparation

Status: Done

Goal:

Generate final visuals and prepare exact manual Power BI build checklist.

Deliverables:

| Deliverable | Status |
|---|---|
| `outputs/eda/final/daily_consumption_trend.png` | Done |
| `outputs/eda/final/monthly_consumption_trend.png` | Done |
| `outputs/eda/final/weekday_weekend_consumption.png` | Done |
| `outputs/eda/final/top_meter_contribution_pareto.png` | Done |
| `outputs/eda/final/weather_consumption_context.png` | Done |
| `outputs/eda/final/data_quality_flags.png` | Done |
| `outputs/eda/final/anomaly_case_review.png` | Done |
| `Data_Acquisition/dataset/processed/eda_summary.csv` | Done |
| `Data_Acquisition/dataset/processed/visual_interpretation_summary.csv` | Done |
| `Data_Acquisition/dataset/processed/insight_recommendation_matrix.csv` | Done |
| `Data_Acquisition/dataset/processed/dashboard_validation_checklist.csv` | Done |
| Power BI manual build section in this document | Done |

Subplan:

1. Generate daily trend.
   - x-axis: date.
   - y-axis: total selected-meter consumption.
   - optional markers for balanced anomaly dates.
2. Generate monthly trend.
   - group by year-month.
   - show total or average daily consumption.
3. Generate weekday/weekend comparison.
   - boxplot or barplot.
   - use selected fact.
4. Generate top meter contribution/Pareto.
   - rank selected meters by total consumption.
   - show cumulative contribution.
5. Generate weather context.
   - scatter consumption vs mean temperature.
   - optional color by hot day or anomaly flag.
6. Generate data quality flags.
   - show inventory quality counts.
   - show selected vs excluded.
7. Generate anomaly case review visual.
   - balanced scenario top cases.
   - show consumption and anomaly score.

Acceptance criteria:

1. Final EDA plots exist under `outputs/eda/final`. Done: 7 PNG files exist and are non-empty.
2. Visuals align with dashboard pages. Done: visual summary maps each figure to a Power BI page.
3. Visuals support at least 3 insight-ready and 3 recommendation-ready findings. Done: `insight_recommendation_matrix.csv` has 4 insight rows and 3 recommendation rows.
4. Power BI manual checklist is complete enough to build `.pbix` without additional decisions. Done: `dashboard_validation_checklist.csv` covers imports, relationships, DAX, slicers, pages, interactions, and screenshots.

---

## Phase 6 - Verification and Handoff Update

Status: Done

Goal:

Verify the full implementation and update handoff documentation.

Deliverables:

| Deliverable | Status |
|---|---|
| Updated `cache/sessionHandoff.md` | Done |
| Updated `cache/ImplementationPhase.md` | Done |
| Verification command output reviewed | Done |

Subplan:

1. Run static compile checks.
2. Run canonical pipeline in order.
3. Execute final notebook.
4. Validate dataset keys and required columns.
5. Validate model output counts.
6. Validate final EDA outputs.
7. Update `sessionHandoff.md`.
8. Update this document with completed statuses and final notes.

Acceptance criteria:

1. `sessionHandoff.md` reflects latest outputs and decisions. Done.
2. This document marks completed phases accurately. Done.
3. Known limitations are explicitly recorded. Done: subset scope, no supervised labels, weather context, and manual Power BI validation remain explicit.
4. No undocumented generated final output remains. Done: final EDA visuals and evidence CSVs are listed here and in `sessionHandoff.md`.

---

# 5. Canonical Runbook

Run commands from repo root:

```powershell
cd "C:\Users\Khalfani Shaquille\Documents\GitHub\Kelompok08_DataAnalytics_TugasBesar"
```

Recommended execution order after implementation:

```powershell
python scripts\download_hko_open_data.py
python scripts\hkust_t1440.py
python scripts\hko_weather.py
python scripts\build_powerbi_datamart.py
python scripts\feature_engineering.py
python scripts\model_anomaly_scenarios.py
python scripts\build_final_eda.py
```

Validation commands:

```powershell
python -m py_compile scripts\config.py scripts\io_utils.py scripts\hko_weather.py scripts\hkust_t1440.py scripts\ttl_entity_mapping.py scripts\build_powerbi_datamart.py scripts\feature_engineering.py scripts\model_anomaly_scenarios.py scripts\build_final_eda.py
```

Notebook validation:

```powershell
python -c "import nbformat; nb=nbformat.read('notebooks/energy_analytics_osemn.ipynb', as_version=4); print(len(nb.cells))"
```

Notebook builder scripts have been removed after the final notebook was generated. Do not attempt to regenerate the notebook from `/scripts`.

Expected final output checks:

```powershell
Get-ChildItem Data_Acquisition\dataset\processed
Get-ChildItem outputs\eda\final
Get-ChildItem notebooks
```

---

# 6. Data Quality Rules

| Case | Treatment | Model Eligible |
|---|---|---:|
| Selected active meter, valid consumption, valid/imputed model weather | `valid` | 1 |
| First reading per meter | `first_reading` | 0 |
| Negative differencing | `negative_diff` | 0 |
| Zero constant meter | `zero_constant` | 0 |
| Near-zero / low-signal meter | `near_zero_low_signal` | 0 |
| Short coverage meter | `short_coverage` | 0 |
| Missing rainfall original value | preserve original, impute model field, flag `weather_imputed` | 1 if only model-safe field is used |
| Missing solar radiation original value | preserve original, impute model field, flag `weather_imputed` | 1 if only model-safe field is used |
| Missing required model feature after treatment | `missing_model_feature` | 0 |

Recommended `data_quality_flag` values:

1. `valid`
2. `first_reading`
3. `negative_diff`
4. `weather_imputed`
5. `missing_model_feature`
6. `excluded_meter_quality`
7. `unmapped_entity`

If multiple flags apply, use a semicolon-delimited string in a stable order.

---

# 7. Power BI Manual Build Plan

## 7.1 Import CSV Files

Import these tables into Power BI Desktop:

1. `Data_Acquisition/dataset/processed/fact_energy_weather_daily.csv`
2. `Data_Acquisition/dataset/processed/fact_anomaly_scenarios.csv`
3. `Data_Acquisition/dataset/processed/dim_date.csv`
4. `Data_Acquisition/dataset/processed/dim_entity.csv`
5. `Data_Acquisition/dataset/processed/dim_scenario.csv`
6. `Data_Acquisition/dataset/processed/entity_scorecard.csv`
7. `Data_Acquisition/dataset/processed/data_quality_summary.csv`
8. `Data_Acquisition/dataset/processed/feature_engineering_summary.csv`
9. `Data_Acquisition/dataset/processed/model_evaluation_summary.csv`
10. `Data_Acquisition/dataset/processed/anomaly_case_review.csv`

## 7.2 Relationships

Create relationships:

| Table | Column | Related Table | Related Column | Cardinality |
|---|---|---|---|---|
| `fact_energy_weather_daily` | `date` | `dim_date` | `date` | Many-to-one |
| `fact_energy_weather_daily` | `entity_id` | `dim_entity` | `entity_id` | Many-to-one |
| `fact_anomaly_scenarios` | `date` | `dim_date` | `date` | Many-to-one |
| `fact_anomaly_scenarios` | `entity_id` | `dim_entity` | `entity_id` | Many-to-one |
| `fact_anomaly_scenarios` | `scenario` | `dim_scenario` | `scenario` | Many-to-one |

Recommended cross-filter direction: single direction from dimensions to facts.

## 7.3 Required DAX Measures

```DAX
Total Consumption =
SUM ( fact_energy_weather_daily[daily_consumption] )

Average Daily Consumption =
AVERAGE ( fact_energy_weather_daily[daily_consumption] )

Peak Daily Consumption =
MAX ( fact_energy_weather_daily[daily_consumption] )

Active Entity Count =
DISTINCTCOUNT ( fact_energy_weather_daily[entity_id] )

Model Eligible Count =
CALCULATE (
    COUNTROWS ( fact_energy_weather_daily ),
    fact_energy_weather_daily[is_model_eligible] = 1
)

Anomaly Count =
CALCULATE (
    COUNTROWS ( fact_anomaly_scenarios ),
    fact_anomaly_scenarios[anomaly_flag] = 1
)

Anomaly Rate =
DIVIDE ( [Anomaly Count], COUNTROWS ( fact_anomaly_scenarios ) )

Average Anomaly Score =
AVERAGE ( fact_anomaly_scenarios[anomaly_score] )

Data Quality Issue Count =
CALCULATE (
    COUNTROWS ( fact_energy_weather_daily ),
    fact_energy_weather_daily[data_quality_flag] <> "valid"
)

Rainy Day Count =
CALCULATE (
    DISTINCTCOUNT ( fact_energy_weather_daily[date] ),
    fact_energy_weather_daily[is_rainy_day] = 1
)

Hot Day Count =
CALCULATE (
    DISTINCTCOUNT ( fact_energy_weather_daily[date] ),
    fact_energy_weather_daily[is_hot_day_28c] = 1
)
```

## 7.4 Dashboard Pages

### Page 1 - Executive Overview

Visuals:

1. KPI: Total Consumption
2. KPI: Average Daily Consumption
3. KPI: Peak Daily Consumption
4. KPI: Anomaly Count
5. KPI: Anomaly Rate
6. Line chart: daily or monthly consumption
7. Bar chart: top entities by consumption
8. Table: top anomaly cases

Slicers:

1. Date range
2. Scenario
3. Entity
4. Anomaly flag

### Page 2 - Consumption Trend

Visuals:

1. Daily trend with anomaly marker.
2. Monthly trend.
3. Weekday/weekend comparison.
4. Month x weekday matrix.
5. Tooltip fields: weather, anomaly score, data quality.

Slicers:

1. Date range
2. Entity
3. Weekday/weekend

### Page 3 - Anomaly Explorer

Visuals:

1. Scatter: consumption vs anomaly score.
2. Detail table: date, entity, consumption, score, scenario, weather.
3. Bar chart: anomaly count by entity.
4. Bar chart: anomaly count by month.
5. Scenario comparison.

Slicers:

1. Scenario
2. Anomaly flag
3. Entity
4. Date range

### Page 4 - Weather Impact

Visuals:

1. Scatter: consumption vs mean temperature.
2. Scatter: consumption vs rainfall.
3. Line chart: consumption and temperature over time.
4. Table: hot/rainy anomaly days.
5. Weather feature summary.

Slicers:

1. Rainy day
2. Hot day
3. Scenario
4. Date range

### Page 5 - Meter / Building Ranking

Visuals:

1. Ranked bar: total consumption.
2. Ranked bar: anomaly rate.
3. Entity scorecard table.
4. Conditional formatting matrix by entity and month.
5. Quality flag by entity.

Slicers:

1. Entity
2. Building
3. Entity type
4. Scenario

### Page 6 - Data Quality and Methodology

Visuals:

1. KPI: active meter count.
2. KPI: excluded meter count.
3. KPI: missing weather count.
4. Bar chart: quality flag counts.
5. Table: excluded meter list.
6. Source table.
7. OSEMN method summary.

Slicers:

1. Data quality flag
2. Meter quality flag
3. Date range

## 7.5 Screenshot Checklist

Before using dashboard screenshots in report/presentation later:

1. Executive Overview screenshot.
2. Consumption Trend screenshot with balanced scenario.
3. Anomaly Explorer screenshot filtered to anomaly rows.
4. Weather Impact screenshot showing weather context.
5. Ranking screenshot showing entity scorecard.
6. Data Quality screenshot showing excluded meters.

---

# 8. Verification Plan

## 8.1 Static Checks

```powershell
python -m py_compile scripts\*.py
```

If wildcard fails in PowerShell context, enumerate script files explicitly.

## 8.2 Data Integrity Checks

Required checks:

1. `dim_date.date` unique.
2. `dim_entity.entity_id` unique.
3. `dim_scenario.scenario` unique.
4. `fact_energy_weather_daily(date, entity_id)` unique.
5. `fact_anomaly_scenarios(date, entity_id, scenario)` unique.
6. All selected meters have `meter_quality_flag = active`.
7. All selected meters have `coverage_ratio = 1.0`.
8. Problematic meters are not model eligible.
9. Rainfall missing count remains documented as 5 days.
10. Solar radiation missing count remains documented as 1 day.

## 8.3 Model Checks

Required checks:

1. `strict`, `balanced`, and `sensitive` all exist in `fact_anomaly_scenarios`.
2. All eligible fact rows appear once per scenario.
3. `anomaly_score` non-null for eligible rows.
4. Anomaly rate is close to configured contamination.
5. Baseline agreement columns exist.
6. Evaluation summary includes no-ground-truth note.

## 8.4 Notebook Checks

Required checks:

1. `/notebooks` contains exactly one active notebook.
2. Final notebook has OSEMN sections.
3. Final notebook executes with 0 error outputs.
4. Final notebook reads or calls script outputs, not duplicated long logic.

## 8.5 Power BI Readiness Checks

Required checks:

1. All required CSVs exist.
2. Relationship keys exist in fact and dimension tables.
3. DAX measures are listed.
4. Dashboard pages and slicers are specified.
5. Screenshot checklist is present.

---

# 9. Insight and Recommendation Targets

The implementation should produce data artifacts that support, but do not yet write, final report insights.

Insight-ready targets:

1. Consumption is concentrated in a small number of selected meters.
2. Consumption patterns differ by time period, weekday/weekend, or month.
3. Anomaly candidates can be ranked by score and reviewed with weather context.
4. Some data quality issues require explicit exclusion or explanation.
5. Weather is useful as context, not as a sole causal explanation.

Recommendation-ready targets:

1. Prioritize audit for entities with high consumption and high anomaly rate.
2. Review selected anomaly dates in balanced scenario.
3. Keep zero/near-zero/short-coverage meters out of model and ranking.
4. Use Power BI dashboard for periodic monitoring.
5. Improve TTL mapping and extend beyond T1440 if broader campus claims are needed.

---

# 10. Known Issues and Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Root `dataset/processed` appears in older docs/scripts | Confusing reproducibility | Use `Data_Acquisition/dataset` as canonical and update docs/scripts |
| T1440 only has 26 meters | Not campus-wide representative | State subset scope clearly |
| Final selected subset only has 12 meters from one building | Limits building comparison | Use meter-level dashboard and transparent limitations |
| Missing rainfall and solar values | Model feature gaps | Preserve originals, add model-safe imputed fields and flags |
| No anomaly labels | No supervised evaluation | Use baseline agreement, visual checks, scenario stability, case review |
| TTL floor missing for some meters | Drill-down limitations | Use building/meter fallback and `mapping_status` |
| Top meters dominate consumption | Ranking bias | Include contribution/Pareto analysis |
| Notebook duplication | Confusing workflow | Archive old notebooks and keep one final active notebook |

---

# 11. Progress Log

| Date | Phase | Status | Notes |
|---|---|---|---|
| 2026-06-14 | Phase 0 | In Progress | Created initial `ImplementationPhase.md` with full implementation plan, phase checklist, datamart spec, model spec, Power BI manual build plan, and verification plan. |
| 2026-06-14 | Governance | Done | Created branch `feat-powerbi-datamart-foundation`, added behavior-based branch/commit naming rule, and updated `sessionHandoff.md` with dual-update requirements. |
| 2026-06-14 | Scripts | Done | Added canonical scripts: `config.py`, `io_utils.py`, `hko_weather.py`, `hkust_t1440.py`, `ttl_entity_mapping.py`, and `build_powerbi_datamart.py`. Notebook builder script existed historically but was removed after the final notebook was generated. |
| 2026-06-14 | Datamart | Done | Generated `dim_date.csv`, `dim_entity.csv`, `dim_scenario.csv`, `fact_energy_weather_daily.csv`, `data_quality_summary.csv`, `data_dictionary_energy_dashboard.csv`, and `final_data_sources.md`. |
| 2026-06-14 | Notebook | Done | Archived old notebooks and generated formal active notebook `notebooks/energy_analytics_osemn.ipynb` with O, S, E, Power BI readiness, and limitations only. |
| 2026-06-14 | Verification | Done | Compile checks passed; notebook executed with 0 error outputs; datamart key checks passed. Fact table has 10,524 rows, 12 entities, no duplicate `date + entity_id`; `dim_entity` has 26 meters; rainfall missing 5 days and solar radiation missing 1 day remain documented. |
| 2026-06-15 | Cache alignment | Done | Updated cache-only alignment analysis against PRD, roadmap, and grading guide. Added scope guard, rubric-based gap analysis, improvement backlog, notebook policy correction, and out-of-scope notes for final academic documentation, presentation, and video/demo. |
| 2026-06-15 | Feature engineering planning | Done | Added Phase 3.5 feature engineering readiness with feature families, feature rules, leakage prevention, data dictionary requirements, notebook policy, and acceptance criteria before final anomaly modelling. |
| 2026-06-15 | Feature engineering implementation | Done | Added `scripts/feature_engineering.py`; generated feature-ready `fact_energy_weather_daily.csv`, `feature_engineering_summary.csv`, and updated data dictionary. Feature-complete model rows: 10,420. |
| 2026-06-15 | Anomaly modelling implementation | Done | Added `scripts/model_anomaly_scenarios.py`; generated `fact_anomaly_scenarios.csv`, `model_evaluation_summary.csv`, `anomaly_case_review.csv`, and `entity_scorecard.csv`. Strict/balanced/sensitive anomaly rates: 0.030038 / 0.050000 / 0.100000. |
| 2026-06-15 | Notebook Model section | Done | Updated active notebook with formal M - Model section using generated model outputs only. Notebook execution completed with 0 error outputs and markdown contains no development wording: phase, backlog, development, or plan. |
| 2026-06-15 | Final EDA evidence implementation | Done | Added `scripts/build_final_eda.py`; generated 7 final EDA visuals under `outputs/eda/final` and evidence tables `eda_summary.csv`, `visual_interpretation_summary.csv`, `insight_recommendation_matrix.csv`, and `dashboard_validation_checklist.csv`. |
| 2026-06-15 | Notebook Explore and iNterpret sections | Done | Updated active notebook with formal E - Explore visuals and N - iNterpret section based on verified evidence outputs. Notebook execution completed with 0 error outputs and markdown contains no development wording: phase, backlog, development, or plan. |
| 2026-06-15 | Final EDA verification and handoff | Done | Verified final EDA PNG files are non-empty, evidence tables have required columns, insight/recommendation count is 4/3, fact/model keys remain unique, and cache trackers were updated. |
| 2026-06-15 | Notebook builder cleanup | Done | Removed `scripts/build_osemn_notebook.py` and `scripts/build_exploration_notebook.py` because the final notebook now exists as the active artifact. Updated runbook and handoff notes so future validation does not call removed builder scripts. |

---

# 12. Phase Status Summary

| Phase | Name | Status |
|---:|---|---|
| 0 | Governance and Planning Artifacts | Done |
| 1 | Script Consolidation | Done |
| 2 | Notebook Unification | Done |
| 3 | Power BI Datamart | Done |
| 3.5 | Feature Engineering Readiness | Done |
| 4 | Anomaly Modelling | Done |
| 5 | Final EDA and Dashboard Preparation | Done |
| 6 | Verification and Handoff Update | Done |

Backlog after this branch:

1. Build manual Power BI `.pbix` from final CSV outputs.
2. Validate Power BI relationship, DAX, slicer, page, tooltip/cross-filter, and screenshot checklist in Power BI Desktop.
3. Final academic report/documentation, presentation, slide deck, and video/demo remain out of scope unless requested explicitly.
