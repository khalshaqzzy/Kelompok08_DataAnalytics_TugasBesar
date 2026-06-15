# React Dashboard Vercel Build Guide

Last updated: 2026-06-15, Asia/Jakarta

This guide replaces the previous Power BI manual build path as the primary dashboard implementation target. The Power BI guide remains available as a historical/manual alternative, but the main deliverable is now a standalone React dashboard published through Vercel.

## 1. Output Target

Recommended production app:

`web/` Vite React app deployed to Vercel.

Recommended Vercel project name:

`energy-anomaly-dashboard`

Primary dashboard source data:

`web/public/data/*.json`

Canonical analytical source remains:

`Data_Acquisition/dataset/processed/*.csv`

The JSON files are generated delivery artifacts for the React app. Do not manually edit them unless debugging a deployment issue.

## 2. Local Commands

Run from repo root:

```powershell
npm install
npm run build:web-data
npm run dev:web
```

Open:

`http://127.0.0.1:5173`

Production build check:

```powershell
npm run build:web
```

Preview production build:

```powershell
npm run preview:web
```

## 3. Data Build

The data packaging script is:

`scripts/build_react_dashboard_data.py`

It reads final CSV outputs from:

`Data_Acquisition/dataset/processed`

It writes compact JSON files to:

`web/public/data`

Expected JSON files:

1. `manifest.json`
2. `daily_trend.json`
3. `monthly_trend.json`
4. `entity_daily.json`
5. `anomalies.json`
6. `dimensions.json`
7. `entity_scorecard.json`
8. `anomaly_case_review.json`
9. `data_quality_summary.json`
10. `model_evaluation_summary.json`
11. `eda_summary.json`
12. `insight_recommendation_matrix.json`

Default dashboard scenario:

`balanced`

## 4. Vercel Settings

The repo includes `vercel.json`.

Use these settings if importing manually in Vercel:

| Setting | Value |
|---|---|
| Framework Preset | Vite |
| Install Command | `npm install` |
| Build Command | `npm run build:web` |
| Output Directory | `web/dist` |
| Root Directory | repo root |

If Vercel asks for environment variables, none are required for the static dashboard.

## 5. Dashboard Design Rules

Use a restrained analytical style:

1. Light background and high-contrast text.
2. Blue for consumption metrics.
3. Red only for anomaly states.
4. Teal or green for valid/quality states.
5. Consistent 8px radius.
6. KPI cards at the top, charts in the middle, detail tables at the bottom.
7. Keep data quality and limitations visible.
8. Do not claim weather causes anomalies; weather is context.
9. Do not describe anomaly candidates as confirmed faults.
10. Preserve the selected T1440 meter-level scope.

## 6. Dashboard Pages

The React app includes:

1. Executive Overview
2. Consumption Trend
3. Anomaly Explorer
4. Weather Impact
5. Meter Ranking
6. Data Quality and Methodology

Global filters:

1. Date start
2. Date end
3. Scenario
4. Entity
5. Anomaly flag
6. Day type
7. Weather
8. Data quality flag

## 7. Validation Checklist

Before publishing:

1. `npm run build:web-data` succeeds.
2. `npm run build:web` succeeds.
3. `web/public/data/manifest.json` has `default_scenario = balanced`.
4. `manifest.json` lists 12 selected entities and 26 `dim_entity` rows.
5. All six dashboard pages render locally.
6. Browser console has no runtime errors.
7. Desktop layout has no chart/table overlap.
8. Mobile layout shows horizontal mobile navigation and stacked filters.
9. Limitation text is visible in Data Quality and Methodology.
10. Vercel output directory is `web/dist`.

## 8. Publish Steps

If Vercel CLI is installed and authenticated:

```powershell
npx vercel --prod
```

If not authenticated, use Vercel web import:

1. Go to Vercel dashboard.
2. Import the GitHub repository.
3. Use the settings in section 4.
4. Deploy.
5. Open the production URL and repeat the validation checklist.

## 9. Known Limitations

1. The dashboard is static and uses prebuilt JSON.
2. It does not retrain Isolation Forest in the browser.
3. It covers selected active T1440 meters, not full HKUST campus coverage.
4. Weather is contextual support, not causal proof.
5. No supervised anomaly labels are available.
