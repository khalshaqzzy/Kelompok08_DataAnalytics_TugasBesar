# Final Data Sources

Canonical dataset root: `Data_Acquisition/dataset`

## HKUST Smart Meter

- Source: Dryad, https://doi.org/10.5061/dryad.k3j9kd5h6
- Local raw files: `Data_Acquisition/dataset/hkust_raw_data/T1440`
- Metadata: `Data_Acquisition/dataset/hkust_raw_data/HKUST_Meter_Metadata.ttl`
- Analytical scope: T1440 daily meter readings.
- Selected building: `Cheng_Yu_Tung_Building`
- Selected meters: D0849, D0848, D0854, D0853, D0862, D0857, D0851, D0861, D0852, D0860, D0850, D0865

## Hong Kong Observatory Weather

- Source: Hong Kong Observatory Open Data.
- Local raw files: `Data_Acquisition/dataset/weather_raw_data`
- Processed file: `Data_Acquisition/dataset/processed/hko_weather_daily.csv`
- Role: weather context for energy interpretation.

## Final Power BI Tables

- `fact_energy_weather_daily.csv`
- `dim_date.csv`
- `dim_entity.csv`
- `dim_scenario.csv`
- `data_quality_summary.csv`
- `data_dictionary_energy_dashboard.csv`

## Limitations

- T1440 has only 26 daily meters.
- The main fact table uses 12 selected active meters from one building.
- Weather is contextual and should not be interpreted as sole causal evidence.
- Final anomaly modelling outputs are backlog after this datamart foundation.
