import React, { useMemo, useState } from "react";
import ReactDOM from "react-dom/client";
import {
  Pulse,
  CloudSun,
  Database,
  Gauge,
  ChartLine as LineChartIcon,
  ListChecks,
  Ranking,
  ShieldWarning,
} from "@phosphor-icons/react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ComposedChart,
  LabelList,
  Line,
  LineChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  SortingState,
  useReactTable,
} from "@tanstack/react-table";
import "./styles.css";

type DataRow = Record<string, string | number | null>;

type DashboardData = {
  manifest: {
    generated_at: string;
    default_scenario: string;
    target_building: string;
    date_range: { start: string; end: string };
    row_counts: Record<string, number>;
    limitations: string[];
  };
  dailyTrend: DataRow[];
  monthlyTrend: DataRow[];
  entityDaily: DataRow[];
  anomalies: DataRow[];
  dimensions: { entities: DataRow[]; scenarios: DataRow[] };
  entityScorecard: DataRow[];
  anomalyCaseReview: DataRow[];
  dataQualitySummary: DataRow[];
  modelEvaluationSummary: DataRow[];
  edaSummary: DataRow[];
  insightRecommendationMatrix: DataRow[];
};

type Filters = {
  startDate: string;
  endDate: string;
  scenario: string;
  entityId: string;
  anomalyFlag: string;
  dayType: string;
  weather: string;
  qualityFlag: string;
};

const dataFiles = {
  manifest: "manifest.json",
  dailyTrend: "daily_trend.json",
  monthlyTrend: "monthly_trend.json",
  entityDaily: "entity_daily.json",
  anomalies: "anomalies.json",
  dimensions: "dimensions.json",
  entityScorecard: "entity_scorecard.json",
  anomalyCaseReview: "anomaly_case_review.json",
  dataQualitySummary: "data_quality_summary.json",
  modelEvaluationSummary: "model_evaluation_summary.json",
  edaSummary: "eda_summary.json",
  insightRecommendationMatrix: "insight_recommendation_matrix.json",
} as const;

const pages = [
  { id: "executive", label: "Executive Overview", icon: Gauge },
  { id: "trend", label: "Consumption Trend", icon: LineChartIcon },
  { id: "anomaly", label: "Anomaly Explorer", icon: ShieldWarning },
  { id: "weather", label: "Weather Impact", icon: CloudSun },
  { id: "ranking", label: "Meter Ranking", icon: Ranking },
  { id: "quality", label: "Data Quality", icon: Database },
] as const;

const numberFormatter = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 1,
});

const compactFormatter = new Intl.NumberFormat("en-US", {
  notation: "compact",
  maximumFractionDigits: 1,
});

const percentFormatter = new Intl.NumberFormat("en-US", {
  style: "percent",
  maximumFractionDigits: 1,
});

function asNumber(value: DataRow[string]): number {
  if (typeof value === "number") return value;
  if (typeof value === "string" && value.trim() !== "") return Number(value);
  return 0;
}

function asString(value: DataRow[string]): string {
  if (value === null || value === undefined) return "";
  return String(value);
}

function inDateRange(row: DataRow, filters: Filters): boolean {
  const date = asString(row.date);
  return date >= filters.startDate && date <= filters.endDate;
}

async function fetchJson<T>(file: string): Promise<T> {
  const response = await fetch(`/data/${file}`);
  if (!response.ok) {
    throw new Error(`Unable to load ${file}`);
  }
  return response.json() as Promise<T>;
}

function useDashboardData() {
  const [data, setData] = React.useState<DashboardData | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let active = true;
    Promise.all(
      Object.entries(dataFiles).map(async ([key, file]) => [
        key,
        await fetchJson(file),
      ]),
    )
      .then((entries) => {
        if (!active) return;
        setData(Object.fromEntries(entries) as DashboardData);
      })
      .catch((err: Error) => {
        if (!active) return;
        setError(err.message);
      });
    return () => {
      active = false;
    };
  }, []);

  return { data, error };
}

function filterEntityRows(rows: DataRow[], filters: Filters) {
  return rows.filter((row) => {
    if (!inDateRange(row, filters)) return false;
    if (filters.entityId !== "all" && row.entity_id !== filters.entityId) return false;
    if (filters.dayType === "weekend" && asNumber(row.is_weekend) !== 1) return false;
    if (filters.dayType === "weekday" && asNumber(row.is_weekend) !== 0) return false;
    if (filters.weather === "hot" && asNumber(row.is_hot_day_28c) !== 1) return false;
    if (filters.weather === "rainy" && asNumber(row.is_rainy_day) !== 1) return false;
    if (filters.qualityFlag !== "all" && row.data_quality_flag !== filters.qualityFlag) return false;
    return true;
  });
}

function filterAnomalies(rows: DataRow[], filters: Filters) {
  return rows.filter((row) => {
    if (!inDateRange(row, filters)) return false;
    if (row.scenario !== filters.scenario) return false;
    if (filters.entityId !== "all" && row.entity_id !== filters.entityId) return false;
    if (filters.anomalyFlag === "anomaly" && asNumber(row.anomaly_flag) !== 1) return false;
    if (filters.anomalyFlag === "normal" && asNumber(row.anomaly_flag) !== 0) return false;
    if (filters.dayType === "weekend" && asNumber(row.is_weekend) !== 1) return false;
    if (filters.dayType === "weekday" && asNumber(row.is_weekend) !== 0) return false;
    if (filters.weather === "hot" && asNumber(row.is_hot_day_28c) !== 1) return false;
    if (filters.weather === "rainy" && asNumber(row.is_rainy_day) !== 1) return false;
    if (filters.qualityFlag !== "all" && row.data_quality_flag !== filters.qualityFlag) return false;
    return true;
  });
}

function App() {
  const { data, error } = useDashboardData();
  const [activePage, setActivePage] = useState<(typeof pages)[number]["id"]>("executive");

  if (error) {
    return (
      <main className="shell error-shell">
        <section className="empty-state">
          <ShieldWarning size={34} />
          <h1>Dashboard data could not be loaded.</h1>
          <p>{error}</p>
        </section>
      </main>
    );
  }

  if (!data) {
    return (
      <main className="shell loading-shell">
        <section className="loading-grid">
          <div />
          <div />
          <div />
          <div />
        </section>
      </main>
    );
  }

  return (
    <Dashboard data={data} activePage={activePage} setActivePage={setActivePage} />
  );
}

function Dashboard({
  data,
  activePage,
  setActivePage,
}: {
  data: DashboardData;
  activePage: (typeof pages)[number]["id"];
  setActivePage: (page: (typeof pages)[number]["id"]) => void;
}) {
  const [filters, setFilters] = useState<Filters>({
    startDate: data.manifest.date_range.start,
    endDate: data.manifest.date_range.end,
    scenario: data.manifest.default_scenario,
    entityId: "all",
    anomalyFlag: "all",
    dayType: "all",
    weather: "all",
    qualityFlag: "all",
  });

  const qualityOptions = useMemo(() => {
    const flags = new Set(data.entityDaily.map((row) => asString(row.data_quality_flag)));
    return [...flags].filter(Boolean).sort();
  }, [data.entityDaily]);

  const entityRows = useMemo(
    () => filterEntityRows(data.entityDaily, filters),
    [data.entityDaily, filters],
  );

  const anomalyRows = useMemo(
    () => filterAnomalies(data.anomalies, filters),
    [data.anomalies, filters],
  );

  const selectedDaily = useMemo(
    () => aggregateDaily(entityRows, anomalyRows),
    [entityRows, anomalyRows],
  );

  const selectedScorecard = useMemo(() => {
    const entityIds = new Set(entityRows.map((row) => asString(row.entity_id)));
    return data.entityScorecard.filter(
      (row) => filters.entityId === "all" || entityIds.has(asString(row.entity_id)),
    );
  }, [data.entityScorecard, entityRows, filters.entityId]);

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand-lockup">
          <div className="brand-mark">
            <Pulse size={23} weight="bold" />
          </div>
          <div>
            <strong>Energy Anomaly</strong>
            <span>HKUST smart meter analytics</span>
          </div>
        </div>
        <nav className="nav-list" aria-label="Dashboard pages">
          {pages.map((page) => {
            const Icon = page.icon;
            return (
              <button
                key={page.id}
                className={activePage === page.id ? "nav-item active" : "nav-item"}
                onClick={() => setActivePage(page.id)}
              >
                <Icon size={20} />
                <span>{page.label}</span>
              </button>
            );
          })}
        </nav>
        <div className="scope-note">
          <span>Scope</span>
          <p>Selected T1440 meter-level case study for Cheng Yu Tung Building.</p>
        </div>
      </aside>

      <section className="content-shell">
        <header className="topbar">
          <div>
            <p className="eyebrow">React dashboard target</p>
            <h1>{pages.find((page) => page.id === activePage)?.label}</h1>
          </div>
          <div className="status-pill">
            <ListChecks size={18} />
            <span>{data.manifest.row_counts.selected_entities} selected meters</span>
          </div>
        </header>

        <MobileNav activePage={activePage} setActivePage={setActivePage} />

        <FiltersPanel
          data={data}
          filters={filters}
          setFilters={setFilters}
          qualityOptions={qualityOptions}
        />

        {activePage === "executive" && (
          <ExecutivePage
            data={data}
            daily={selectedDaily}
            anomalies={anomalyRows}
            scorecard={selectedScorecard}
          />
        )}
        {activePage === "trend" && (
          <TrendPage daily={selectedDaily} entityRows={entityRows} monthly={data.monthlyTrend} />
        )}
        {activePage === "anomaly" && (
          <AnomalyPage
            anomalies={anomalyRows}
            cases={data.anomalyCaseReview}
            evaluation={data.modelEvaluationSummary}
          />
        )}
        {activePage === "weather" && (
          <WeatherPage daily={selectedDaily} entityRows={entityRows} />
        )}
        {activePage === "ranking" && <RankingPage scorecard={selectedScorecard} />}
        {activePage === "quality" && <QualityPage data={data} />}
      </section>
    </main>
  );
}

function MobileNav({
  activePage,
  setActivePage,
}: {
  activePage: (typeof pages)[number]["id"];
  setActivePage: (page: (typeof pages)[number]["id"]) => void;
}) {
  return (
    <div className="mobile-nav">
      {pages.map((page) => (
        <button
          key={page.id}
          className={activePage === page.id ? "mobile-nav-item active" : "mobile-nav-item"}
          onClick={() => setActivePage(page.id)}
        >
          {page.label}
        </button>
      ))}
    </div>
  );
}

function FiltersPanel({
  data,
  filters,
  setFilters,
  qualityOptions,
}: {
  data: DashboardData;
  filters: Filters;
  setFilters: React.Dispatch<React.SetStateAction<Filters>>;
  qualityOptions: string[];
}) {
  const entities = data.dimensions.entities.filter(
    (entity) => asNumber(entity.is_selected_main_subset) === 1,
  );

  const update = (key: keyof Filters, value: string) => {
    setFilters((current) => ({ ...current, [key]: value }));
  };

  return (
    <section className="filters-panel">
      <label>
        <span>Date start</span>
        <input
          type="date"
          value={filters.startDate}
          min={data.manifest.date_range.start}
          max={filters.endDate}
          onChange={(event) => update("startDate", event.target.value)}
        />
      </label>
      <label>
        <span>Date end</span>
        <input
          type="date"
          value={filters.endDate}
          min={filters.startDate}
          max={data.manifest.date_range.end}
          onChange={(event) => update("endDate", event.target.value)}
        />
      </label>
      <label>
        <span>Scenario</span>
        <select value={filters.scenario} onChange={(event) => update("scenario", event.target.value)}>
          {data.dimensions.scenarios.map((scenario) => (
            <option key={asString(scenario.scenario)} value={asString(scenario.scenario)}>
              {asString(scenario.scenario_label)}
            </option>
          ))}
        </select>
      </label>
      <label>
        <span>Entity</span>
        <select value={filters.entityId} onChange={(event) => update("entityId", event.target.value)}>
          <option value="all">All selected meters</option>
          {entities.map((entity) => (
            <option key={asString(entity.entity_id)} value={asString(entity.entity_id)}>
              {asString(entity.entity_id)} · {asString(entity.room_or_equipment)}
            </option>
          ))}
        </select>
      </label>
      <label>
        <span>Anomaly flag</span>
        <select value={filters.anomalyFlag} onChange={(event) => update("anomalyFlag", event.target.value)}>
          <option value="all">All rows</option>
          <option value="anomaly">Anomaly only</option>
          <option value="normal">Normal only</option>
        </select>
      </label>
      <label>
        <span>Day type</span>
        <select value={filters.dayType} onChange={(event) => update("dayType", event.target.value)}>
          <option value="all">All days</option>
          <option value="weekday">Weekday</option>
          <option value="weekend">Weekend</option>
        </select>
      </label>
      <label>
        <span>Weather</span>
        <select value={filters.weather} onChange={(event) => update("weather", event.target.value)}>
          <option value="all">All weather</option>
          <option value="hot">Hot days</option>
          <option value="rainy">Rainy days</option>
        </select>
      </label>
      <label>
        <span>Quality</span>
        <select value={filters.qualityFlag} onChange={(event) => update("qualityFlag", event.target.value)}>
          <option value="all">All flags</option>
          {qualityOptions.map((flag) => (
            <option key={flag} value={flag}>
              {flag}
            </option>
          ))}
        </select>
      </label>
    </section>
  );
}

function aggregateDaily(entityRows: DataRow[], anomalyRows: DataRow[]) {
  const dailyMap = new Map<string, DataRow>();
  for (const row of entityRows) {
    const date = asString(row.date);
    const current = dailyMap.get(date) ?? {
      date,
      total_consumption: 0,
      average_consumption: 0,
      peak_meter_consumption: 0,
      entity_count: 0,
      mean_temperature_c: 0,
      rainfall_mm_model: 0,
      is_weekend: 0,
      is_hot_day_28c: 0,
      is_rainy_day: 0,
      quality_issue_rows: 0,
      balanced_anomaly_count: 0,
      average_anomaly_score: 0,
    };
    const count = asNumber(current.entity_count) + 1;
    current.total_consumption = asNumber(current.total_consumption) + asNumber(row.daily_consumption);
    current.peak_meter_consumption = Math.max(
      asNumber(current.peak_meter_consumption),
      asNumber(row.daily_consumption),
    );
    current.mean_temperature_c =
      (asNumber(current.mean_temperature_c) * (count - 1) + asNumber(row.mean_temperature_c)) / count;
    current.rainfall_mm_model =
      (asNumber(current.rainfall_mm_model) * (count - 1) + asNumber(row.rainfall_mm_model)) / count;
    current.entity_count = count;
    current.average_consumption = asNumber(current.total_consumption) / count;
    current.is_weekend = Math.max(asNumber(current.is_weekend), asNumber(row.is_weekend));
    current.is_hot_day_28c = Math.max(asNumber(current.is_hot_day_28c), asNumber(row.is_hot_day_28c));
    current.is_rainy_day = Math.max(asNumber(current.is_rainy_day), asNumber(row.is_rainy_day));
    current.quality_issue_rows =
      asNumber(current.quality_issue_rows) + (row.data_quality_flag === "valid" ? 0 : 1);
    dailyMap.set(date, current);
  }

  const anomalyMap = new Map<string, { count: number; totalScore: number }>();
  for (const row of anomalyRows) {
    const date = asString(row.date);
    const current = anomalyMap.get(date) ?? { count: 0, totalScore: 0 };
    if (asNumber(row.anomaly_flag) === 1) {
      current.count += 1;
      current.totalScore += asNumber(row.anomaly_score);
    }
    anomalyMap.set(date, current);
  }

  for (const [date, anomaly] of anomalyMap.entries()) {
    const current = dailyMap.get(date);
    if (!current) continue;
    current.balanced_anomaly_count = anomaly.count;
    current.average_anomaly_score = anomaly.count ? anomaly.totalScore / anomaly.count : 0;
  }

  return [...dailyMap.values()].sort((a, b) => asString(a.date).localeCompare(asString(b.date)));
}

function ExecutivePage({
  data,
  daily,
  anomalies,
  scorecard,
}: {
  data: DashboardData;
  daily: DataRow[];
  anomalies: DataRow[];
  scorecard: DataRow[];
}) {
  const totalConsumption = daily.reduce((sum, row) => sum + asNumber(row.total_consumption), 0);
  const anomalyCount = anomalies.filter((row) => asNumber(row.anomaly_flag) === 1).length;
  const anomalyRate = anomalies.length ? anomalyCount / anomalies.length : 0;
  const peakDay = daily.reduce((max, row) => Math.max(max, asNumber(row.total_consumption)), 0);
  const topEntities = [...scorecard].sort(
    (a, b) => asNumber(b.total_consumption) - asNumber(a.total_consumption),
  );
  const insights = data.insightRecommendationMatrix.slice(0, 4);

  return (
    <div className="page-grid">
      <KpiStrip>
        <KpiCard label="Total consumption" value={compactFormatter.format(totalConsumption)} detail="Selected meters" />
        <KpiCard label="Peak daily total" value={compactFormatter.format(peakDay)} detail="Highest filtered day" />
        <KpiCard label="Anomaly candidates" value={numberFormatter.format(anomalyCount)} detail="Current scenario" tone="alert" />
        <KpiCard label="Anomaly rate" value={percentFormatter.format(anomalyRate)} detail="Filtered model rows" />
      </KpiStrip>
      <ChartPanel title="Daily selected-meter consumption" span="wide">
        <ResponsiveContainer width="100%" height={320}>
          <ComposedChart data={daily}>
            <CartesianGrid stroke="#e5e7eb" vertical={false} />
            <XAxis dataKey="date" minTickGap={36} tickLine={false} />
            <YAxis tickFormatter={(value) => compactFormatter.format(value)} tickLine={false} />
            <Tooltip content={<ChartTooltip />} />
            <Bar dataKey="balanced_anomaly_count" fill="#dc2626" barSize={4} />
            <Line type="monotone" dataKey="total_consumption" stroke="#2563eb" strokeWidth={2.2} dot={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </ChartPanel>
      <ChartPanel title="Top meter contribution">
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={topEntities.slice(0, 8)} layout="vertical" margin={{ left: 14 }}>
            <CartesianGrid stroke="#e5e7eb" horizontal={false} />
            <XAxis type="number" tickFormatter={(value) => compactFormatter.format(value)} />
            <YAxis type="category" dataKey="entity_id" width={62} />
            <Tooltip content={<ChartTooltip />} />
            <Bar dataKey="total_consumption" fill="#2563eb" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartPanel>
      <EvidencePanel rows={insights} />
      <DataTable
        title="Top anomaly case review"
        rows={data.anomalyCaseReview.slice(0, 8)}
        columns={[
          column("date", "Date"),
          column("entity_id", "Entity"),
          column("daily_consumption", "Consumption", "number"),
          column("anomaly_score", "Score", "number"),
          column("consumption_context_label", "Consumption context"),
        ]}
      />
    </div>
  );
}

function TrendPage({
  daily,
  entityRows,
  monthly,
}: {
  daily: DataRow[];
  entityRows: DataRow[];
  monthly: DataRow[];
}) {
  const weekend = compareWeekdayWeekend(entityRows);

  return (
    <div className="page-grid">
      <ChartPanel title="Daily consumption trend" span="wide">
        <ResponsiveContainer width="100%" height={340}>
          <LineChart data={daily}>
            <CartesianGrid stroke="#e5e7eb" vertical={false} />
            <XAxis dataKey="date" minTickGap={34} tickLine={false} />
            <YAxis tickFormatter={(value) => compactFormatter.format(value)} />
            <Tooltip content={<ChartTooltip />} />
            <Line type="monotone" dataKey="total_consumption" stroke="#2563eb" strokeWidth={2.3} dot={false} />
            <Line type="monotone" dataKey="peak_meter_consumption" stroke="#0f766e" strokeWidth={1.6} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </ChartPanel>
      <ChartPanel title="Monthly total and average">
        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart data={monthly}>
            <CartesianGrid stroke="#e5e7eb" vertical={false} />
            <XAxis dataKey="year_month" minTickGap={18} />
            <YAxis tickFormatter={(value) => compactFormatter.format(value)} />
            <Tooltip content={<ChartTooltip />} />
            <Bar dataKey="total_consumption" fill="#93c5fd" radius={[4, 4, 0, 0]} />
            <Line dataKey="average_daily_consumption" stroke="#1d4ed8" strokeWidth={2} dot={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </ChartPanel>
      <ChartPanel title="Weekday and weekend comparison">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={weekend}>
            <CartesianGrid stroke="#e5e7eb" vertical={false} />
            <XAxis dataKey="label" />
            <YAxis tickFormatter={(value) => compactFormatter.format(value)} />
            <Tooltip content={<ChartTooltip />} />
            <Bar dataKey="average_consumption" fill="#0f766e" radius={[4, 4, 0, 0]}>
              <LabelList dataKey="average_consumption" formatter={(value: number) => compactFormatter.format(value)} position="top" />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </ChartPanel>
      <DataTable
        title="Daily trend detail"
        rows={daily.slice(-30).reverse()}
        columns={[
          column("date", "Date"),
          column("total_consumption", "Total", "number"),
          column("peak_meter_consumption", "Peak meter", "number"),
          column("balanced_anomaly_count", "Anomaly count", "number"),
          column("quality_issue_rows", "Quality rows", "number"),
        ]}
      />
    </div>
  );
}

function AnomalyPage({
  anomalies,
  cases,
  evaluation,
}: {
  anomalies: DataRow[];
  cases: DataRow[];
  evaluation: DataRow[];
}) {
  const flagged = anomalies.filter((row) => asNumber(row.anomaly_flag) === 1);
  const entityCounts = countBy(flagged, "entity_id", "anomaly_count")
    .sort((a, b) => asNumber(b.anomaly_count) - asNumber(a.anomaly_count))
    .slice(0, 10);

  return (
    <div className="page-grid">
      <KpiStrip>
        <KpiCard label="Model rows" value={numberFormatter.format(anomalies.length)} detail="After filters" />
        <KpiCard label="Flagged candidates" value={numberFormatter.format(flagged.length)} detail="Scenario output" tone="alert" />
        <KpiCard label="Baseline-supported cases" value={numberFormatter.format(flagged.filter((row) => asNumber(row.baseline_agreement_count) > 0).length)} detail="IQR or Z-score" />
        <KpiCard label="Top case score" value={flagged.length ? numberFormatter.format(asNumber(flagged[0].anomaly_score)) : "0"} detail="Lower score is more anomalous" />
      </KpiStrip>
      <ChartPanel title="Consumption versus anomaly score" span="wide">
        <ResponsiveContainer width="100%" height={340}>
          <ScatterChart>
            <CartesianGrid stroke="#e5e7eb" />
            <XAxis dataKey="daily_consumption" name="Consumption" tickFormatter={(value) => compactFormatter.format(value)} />
            <YAxis dataKey="anomaly_score" name="Anomaly score" />
            <Tooltip cursor={{ strokeDasharray: "3 3" }} content={<ChartTooltip />} />
            <Scatter data={anomalies} fill="#2563eb">
              {anomalies.map((row, index) => (
                <Cell key={`${row.date}-${row.entity_id}-${index}`} fill={asNumber(row.anomaly_flag) === 1 ? "#dc2626" : "#93c5fd"} />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </ChartPanel>
      <ChartPanel title="Anomaly count by entity">
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={entityCounts} layout="vertical">
            <CartesianGrid stroke="#e5e7eb" horizontal={false} />
            <XAxis type="number" />
            <YAxis type="category" dataKey="entity_id" width={62} />
            <Tooltip content={<ChartTooltip />} />
            <Bar dataKey="anomaly_count" fill="#dc2626" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartPanel>
      <DataTable
        title="Scenario evaluation"
        rows={evaluation}
        columns={[
          column("scenario", "Scenario"),
          column("contamination", "Contamination", "number"),
          column("anomaly_count", "Anomalies", "number"),
          column("anomaly_rate", "Rate", "percent"),
          column("iqr_agreement_rate", "IQR agreement", "percent"),
          column("zscore_agreement_rate", "Z-score agreement", "percent"),
        ]}
      />
      <DataTable
        title="Balanced case review"
        rows={cases.slice(0, 12)}
        columns={[
          column("date", "Date"),
          column("entity_id", "Entity"),
          column("daily_consumption", "Consumption", "number"),
          column("pct_deviation_from_rolling_mean_7d", "Rolling deviation", "percent"),
          column("weather_context_label", "Weather context"),
        ]}
      />
    </div>
  );
}

function WeatherPage({
  daily,
  entityRows,
}: {
  daily: DataRow[];
  entityRows: DataRow[];
}) {
  const weatherRows: DataRow[] = daily.map((row) => ({
    ...row,
    anomaly_marker: asNumber(row.balanced_anomaly_count) > 0 ? "Anomaly day" : "Normal day",
  }));
  const bands = countBy(entityRows, "temperature_band", "row_count");

  return (
    <div className="page-grid">
      <ChartPanel title="Temperature context versus consumption" span="wide">
        <ResponsiveContainer width="100%" height={340}>
          <ScatterChart>
            <CartesianGrid stroke="#e5e7eb" />
            <XAxis dataKey="mean_temperature_c" name="Mean temperature" unit=" C" />
            <YAxis dataKey="total_consumption" name="Daily consumption" tickFormatter={(value) => compactFormatter.format(value)} />
            <Tooltip content={<ChartTooltip />} />
            <Scatter data={weatherRows} fill="#2563eb">
              {weatherRows.map((row, index) => (
                <Cell key={`${row.date}-${index}`} fill={asNumber(row.balanced_anomaly_count) > 0 ? "#dc2626" : "#2563eb"} />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </ChartPanel>
      <ChartPanel title="Rainfall and consumption over time">
        <ResponsiveContainer width="100%" height={320}>
          <ComposedChart data={daily}>
            <CartesianGrid stroke="#e5e7eb" vertical={false} />
            <XAxis dataKey="date" minTickGap={38} />
            <YAxis yAxisId="left" tickFormatter={(value) => compactFormatter.format(value)} />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip content={<ChartTooltip />} />
            <Bar yAxisId="right" dataKey="rainfall_mm_model" fill="#7dd3fc" radius={[4, 4, 0, 0]} />
            <Line yAxisId="left" dataKey="total_consumption" stroke="#2563eb" strokeWidth={2} dot={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </ChartPanel>
      <ChartPanel title="Temperature band row coverage">
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={bands}>
            <CartesianGrid stroke="#e5e7eb" vertical={false} />
            <XAxis dataKey="temperature_band" />
            <YAxis />
            <Tooltip content={<ChartTooltip />} />
            <Bar dataKey="row_count" fill="#0f766e" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartPanel>
      <MethodNote
        title="Weather interpretation guardrail"
        body="Weather variables are used as context for reading consumption and anomaly candidates. The dashboard should not treat weather as causal proof because the model is unsupervised and the dataset is a selected meter-level case study."
      />
    </div>
  );
}

function RankingPage({ scorecard }: { scorecard: DataRow[] }) {
  const ranked = [...scorecard].sort(
    (a, b) => asNumber(a.entity_priority_rank) - asNumber(b.entity_priority_rank),
  );

  return (
    <div className="page-grid">
      <ChartPanel title="Entity priority score" span="wide">
        <ResponsiveContainer width="100%" height={340}>
          <BarChart data={ranked} layout="vertical">
            <CartesianGrid stroke="#e5e7eb" horizontal={false} />
            <XAxis type="number" domain={[0, 1]} />
            <YAxis type="category" dataKey="entity_id" width={64} />
            <Tooltip content={<ChartTooltip />} />
            <Bar dataKey="entity_priority_score" fill="#2563eb" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartPanel>
      <ChartPanel title="Contribution and anomaly rate">
        <ResponsiveContainer width="100%" height={320}>
          <ComposedChart data={ranked}>
            <CartesianGrid stroke="#e5e7eb" vertical={false} />
            <XAxis dataKey="entity_id" />
            <YAxis tickFormatter={(value) => percentFormatter.format(value)} />
            <Tooltip content={<ChartTooltip />} />
            <Bar dataKey="entity_contribution_pct" fill="#93c5fd" radius={[4, 4, 0, 0]} />
            <Line dataKey="balanced_anomaly_rate" stroke="#dc2626" strokeWidth={2} />
          </ComposedChart>
        </ResponsiveContainer>
      </ChartPanel>
      <DataTable
        title="Entity scorecard"
        rows={ranked}
        columns={[
          column("entity_priority_rank", "Rank", "number"),
          column("entity_id", "Entity"),
          column("total_consumption", "Total", "number"),
          column("peak_daily_consumption", "Peak", "number"),
          column("balanced_anomaly_count", "Balanced anomalies", "number"),
          column("balanced_anomaly_rate", "Anomaly rate", "percent"),
          column("entity_priority_score", "Priority score", "number"),
        ]}
      />
    </div>
  );
}

function QualityPage({ data }: { data: DashboardData }) {
  const selected = data.dimensions.entities.filter((row) => asNumber(row.is_selected_main_subset) === 1);
  const excluded = data.dimensions.entities.filter((row) => asNumber(row.is_selected_main_subset) !== 1);
  const qualityCounts = countBy(data.dimensions.entities, "meter_quality_flag", "entity_count");

  return (
    <div className="page-grid">
      <KpiStrip>
        <KpiCard label="All T1440 meters" value={numberFormatter.format(data.dimensions.entities.length)} detail="Visible in entity dimension" />
        <KpiCard label="Selected meters" value={numberFormatter.format(selected.length)} detail="Model and dashboard scope" />
        <KpiCard label="Excluded meters" value={numberFormatter.format(excluded.length)} detail="Quality or coverage decision" tone="alert" />
        <KpiCard label="Top cases reviewed" value={numberFormatter.format(data.anomalyCaseReview.length)} detail="Balanced scenario" />
      </KpiStrip>
      <ChartPanel title="Meter quality flag counts">
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={qualityCounts}>
            <CartesianGrid stroke="#e5e7eb" vertical={false} />
            <XAxis dataKey="meter_quality_flag" />
            <YAxis />
            <Tooltip content={<ChartTooltip />} />
            <Bar dataKey="entity_count" fill="#0f766e" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartPanel>
      <DataTable
        title="Data quality summary"
        rows={data.dataQualitySummary}
        columns={[
          column("summary_group", "Group"),
          column("metric", "Metric"),
          column("value", "Value", "number"),
          column("notes", "Notes"),
        ]}
      />
      <DataTable
        title="Excluded and monitored meters"
        rows={excluded}
        columns={[
          column("entity_id", "Entity"),
          column("building", "Building"),
          column("meter_quality_flag", "Quality flag"),
          column("selection_decision", "Decision"),
          column("coverage_ratio", "Coverage", "percent"),
        ]}
      />
      <MethodNote
        title="Methodology notes"
        body={data.manifest.limitations.join(" ")}
      />
    </div>
  );
}

function KpiStrip({ children }: { children: React.ReactNode }) {
  return <section className="kpi-strip">{children}</section>;
}

function KpiCard({
  label,
  value,
  detail,
  tone = "normal",
}: {
  label: string;
  value: string;
  detail: string;
  tone?: "normal" | "alert";
}) {
  return (
    <article className={`kpi-card ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{detail}</p>
    </article>
  );
}

function ChartPanel({
  title,
  children,
  span,
}: {
  title: string;
  children: React.ReactNode;
  span?: "wide";
}) {
  return (
    <section className={span === "wide" ? "panel wide" : "panel"}>
      <div className="panel-header">
        <h2>{title}</h2>
      </div>
      {children}
    </section>
  );
}

function EvidencePanel({ rows }: { rows: DataRow[] }) {
  return (
    <section className="panel evidence-panel">
      <div className="panel-header">
        <h2>Evidence-backed interpretation</h2>
      </div>
      <div className="evidence-list">
        {rows.map((row, index) => (
          <article key={`${row.item_type}-${index}`}>
            <span>{asString(row.priority)}</span>
            <strong>{asString(row.finding)}</strong>
            <p>{asString(row.expected_action)}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function MethodNote({ title, body }: { title: string; body: string }) {
  return (
    <section className="method-note">
      <ListChecks size={22} />
      <div>
        <h2>{title}</h2>
        <p>{body}</p>
      </div>
    </section>
  );
}

function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip">
      {label && <strong>{label}</strong>}
      {payload.slice(0, 6).map((item: any) => (
        <p key={item.dataKey}>
          <span style={{ background: item.color }} />
          {item.name || item.dataKey}: {formatCell(item.value)}
        </p>
      ))}
    </div>
  );
}

function column(key: string, label: string, type: "text" | "number" | "percent" = "text"): ColumnDef<DataRow> {
  return {
    accessorKey: key,
    header: label,
    cell: ({ getValue }) => formatCell(getValue(), type),
  };
}

function formatCell(value: unknown, type: "text" | "number" | "percent" = "text") {
  if (value === null || value === undefined || value === "") return "n/a";
  if (type === "percent") return percentFormatter.format(Number(value));
  if (type === "number") return numberFormatter.format(Number(value));
  if (typeof value === "number") return numberFormatter.format(value);
  return String(value);
}

function DataTable({
  title,
  rows,
  columns,
}: {
  title: string;
  rows: DataRow[];
  columns: ColumnDef<DataRow>[];
}) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const table = useReactTable({
    data: rows,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  return (
    <section className="panel table-panel wide">
      <div className="panel-header">
        <h2>{title}</h2>
        <span>{numberFormatter.format(rows.length)} rows</span>
      </div>
      <div className="table-scroll">
        <table>
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th key={header.id}>
                    <button onClick={header.column.getToggleSortingHandler()}>
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      <span>{header.column.getIsSorted() === "asc" ? "↑" : header.column.getIsSorted() === "desc" ? "↓" : ""}</span>
                    </button>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.slice(0, 80).map((row) => (
              <tr key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function compareWeekdayWeekend(rows: DataRow[]) {
  const groups = [
    { key: 0, label: "Weekday" },
    { key: 1, label: "Weekend" },
  ];
  return groups.map((group) => {
    const subset = rows.filter((row) => asNumber(row.is_weekend) === group.key);
    const total = subset.reduce((sum, row) => sum + asNumber(row.daily_consumption), 0);
    return {
      label: group.label,
      average_consumption: subset.length ? total / subset.length : 0,
      row_count: subset.length,
    };
  });
}

function countBy(rows: DataRow[], key: string, valueName: string) {
  const counts = new Map<string, number>();
  for (const row of rows) {
    const label = asString(row[key]) || "unknown";
    counts.set(label, (counts.get(label) ?? 0) + 1);
  }
  return [...counts.entries()].map(([label, count]) => ({
    [key]: label,
    [valueName]: count,
  }));
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
