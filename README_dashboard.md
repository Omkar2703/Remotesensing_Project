# 🛰️ AgriRisk-Sat Dashboard

> **Module 5 — Interactive Crop Stress & Agricultural Loss Intelligence Dashboard**
> Streamlit web application for real-time crop monitoring, CLI visualization, and PMFBY insurance payout simulation across Gujarat, Maharashtra & Madhya Pradesh.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Live Demo Screenshot](#live-demo-screenshot)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running the Dashboard](#running-the-dashboard)
- [Dashboard Tabs](#dashboard-tabs)
- [Data Model](#data-model)
- [CLI Formula](#cli-formula)
- [Sidebar Controls](#sidebar-controls)
- [Bug Fixes Applied](#bug-fixes-applied)
- [Production Integration](#production-integration)
- [Full Project Modules](#full-project-modules)
- [Datasets Used](#datasets-used)
- [Troubleshooting](#troubleshooting)
- [Glossary](#glossary)

---

## Overview

AgriRisk-Sat Dashboard is the **interactive front-end** for the AgriRisk-Sat satellite pipeline. It bridges earth observation data from Sentinel-1/2, Landsat, MODIS, CHIRPS, and SMAP with actuarial insurance logic to produce real-time crop stress alerts and PMFBY payout estimates at the district level.

India pays **₹25,000+ crore/year** in PMFBY crop insurance claims — mostly assessed by slow ground surveys. This dashboard replaces or validates those surveys with satellite-first loss adjudication.

**Target users:**
- 🏢 Insurance field officers — stress alerts + payout calculation
- 🏛️ State agriculture department analysts — CLI maps + trend analysis
- 🔬 Researchers — CLI vs PMFBY validation and crop phenology

---

## Features

```
✅  Real-time district stress alerts   (Drought · Flood · Heatwave)
✅  Interactive CLI risk heat map       (30 districts × 3 states)
✅  Multi-year trend analysis           (2018 – 2023, CLI vs PMFBY)
✅  Stress driver decomposition         (VCI + SAR + LST stacked chart)
✅  VCI dekadal profile                 (18 dekads Jun–Nov)
✅  Crop-type stress profiling          (Cotton · Groundnut · Soybean · Wheat)
✅  Crop phenology calendar             (sowing → harvest → stress window)
✅  PMFBY payout simulator              (CLI gauge + sensitivity curve)
✅  District payout table               (with gradient styling)
✅  Fully configurable sidebar          (state · year · crop · threshold)
```

---

## Tech Stack

| Library | Version | Role |
|---|---|---|
| `streamlit` | ≥ 1.25.0 | Web framework, all UI components |
| `matplotlib` | ≥ 3.7.0 | All charts — heatmap, gauge, trend, scatter |
| `numpy` | ≥ 1.24.0 | Numerical arrays, synthetic data generation |
| `pandas` | ≥ 2.0.0 | DataFrame operations, filtering, styling |
| `seaborn` | ≥ 0.12.0 | Imported, available for extension |

---

## Project Structure

```
AgriRisk-Sat/
│
├── dashboard_fixed.py              ← 🚀 Main dashboard file (run this)
│
├── gee_scripts/
│   ├── module1_gujarat_weekly.js   ← Farm parcel delineation (Gujarat)
│   ├── module1_maharashtra_weekly.js
│   ├── module1_mp_weekly.js
│   ├── module2_weekly.js           ← Crop type & phenology mapping
│   └── module3_stress_detection.js ← Drought + flood + heat detection
│
├── python_pipeline/
│   ├── module4_crop_loss_index.py  ← CLI computation & PMFBY validation
│   ├── module4_cli_results.csv     ← Output: district CLI scores
│   └── module4_summary.json        ← Validation statistics
│
├── docs/
│   └── AgriRiskSat_Dashboard_Documentation.docx
│
├── requirements.txt
└── README.md                       ← You are here
```

---

## Installation

### 1. Clone or download the project

```bash
git clone https://github.com/your-username/AgriRisk-Sat.git
cd AgriRisk-Sat
```

### 2. Create a virtual environment (recommended)

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install streamlit matplotlib numpy pandas seaborn
```

### 4. (Optional) Install Watchdog for better performance on macOS

```bash
xcode-select --install
pip install watchdog
```

---

## Running the Dashboard

```bash
streamlit run dashboard_fixed.py
```

The terminal will show:

```
  You can now view your Streamlit app in your browser.

  Local URL:   http://localhost:8501
  Network URL: http://10.x.x.x:8501
```

Open `http://localhost:8501` in your browser. The dashboard loads instantly.

To run on a different port:

```bash
streamlit run dashboard_fixed.py --server.port 8502
```

---

## Dashboard Tabs

### 🗺️ Tab 1 — CLI Map
| Element | Description |
|---|---|
| District CLI Heatmap | `imshow` grid — rows = states, columns = districts sorted by CLI. Green → Red scale. |
| Risk Category Bar Chart | Horizontal bars showing count of districts in each severity band |
| Top 5 Risk Districts | Table of highest-CLI districts with crop and state |

### 📈 Tab 2 — Trend Analysis
| Element | Description |
|---|---|
| CLI vs PMFBY Trend | Dual-axis line chart (2018–2023) — CLI left axis, claims right axis |
| Stress Decomposition | Stacked area chart splitting CLI into drought, flood, and heat contributions |
| VCI Dekadal Profile | 18-dekad VCI time series with drought threshold (VCI=35) shading |

### 🌾 Tab 3 — Crop Comparison
| Element | Description |
|---|---|
| Stress by Crop Type | Grouped bar chart — drought, flood, heat per crop |
| CLI vs Drought Scatter | Scatter plot coloured by crop, with CLI alert threshold line |
| Phenology Calendar | Sowing → vegetative → anthesis → harvest → stress window per crop |

### 💰 Tab 4 — Payout Simulator
| Element | Description |
|---|---|
| CLI Gauge | Semicircular arc gauge with needle showing district CLI severity |
| Payout Metrics | CLI score, payout %, payout/ha, total payout in ₹ crore |
| Sensitivity Curve | Payout vs CLI chart with current value and trigger threshold marked |
| Full Payout Table | All districts with triggered flag, payout/ha, total payout — gradient styled |

---

## Data Model

The dashboard uses a **1,080-row synthetic dataset** (30 districts × 6 years × 6 observations) that replicates realistic PMFBY distributions. In production this is replaced by `module4_cli_results.csv`.

### District DataFrame Columns

| Column | Type | Range | Description |
|---|---|---|---|
| `state` | string | Gujarat / Maharashtra / MP | State name |
| `district` | string | 30 districts | District name |
| `year` | int | 2018 – 2023 | Kharif season year |
| `crop` | string | Cotton / Groundnut / Soybean / Wheat | Dominant crop |
| `CLI` | float | 0 – 100 | Crop Loss Index |
| `vci_deficit` | float | 0 – 100% | Drought stress proxy |
| `flood_days` | float | 0 – 40+ | SAR flood inundation days |
| `heat_stress_days` | int | 0 – 20+ | Days LST > 35°C during anthesis |
| `pmfby_claims_per_ha` | float | 0 – 3000 ₹/ha | Historical insurance claims |
| `insured_area_ha` | float | 5,000 – 80,000 ha | Total insured area |
| `rainfall_anomaly_mm` | float | −200 to +200 mm | CHIRPS rainfall anomaly |
| `soil_moisture_pct` | float | 8 – 45% | SMAP root-zone moisture |
| `lst_max_c` | float | 20 – 55°C | Landsat 9 max LST |

---

## CLI Formula

```
CLI = 0.45 × VCI_deficit_norm + 0.35 × Flood_days_norm + 0.20 × Heat_stress_norm
```

Where:
- `VCI_deficit_norm = vci_deficit / 100`
- `Flood_days_norm  = min(flood_days / 40, 1.0)`
- `Heat_stress_norm = min(heat_stress_days / 20, 1.0)`

### Severity Classes

| CLI | Category | Colour |
|---|---|---|
| 0 – 20 | Low | 🟢 `#1a9850` |
| 20 – 40 | Moderate | 🟡 `#91cf60` |
| 40 – 60 | High | 🟠 `#fee08b` |
| 60 – 80 | Severe | 🔴 `#fc8d59` |
| 80 – 100 | Extreme | ⛔ `#d73027` |

### Payout Formula

```
If CLI > Trigger:
    Payout = min((CLI - Trigger) / (100 - Trigger), 1.0) × Sum_Insured
Else:
    Payout = 0
```

Default: Trigger = 25, Sum Insured = ₹3,500/ha (configurable in sidebar)

---

## Sidebar Controls

| Control | Widget | Default | Effect |
|---|---|---|---|
| State | `selectbox` | All States | Filter districts to one state |
| Kharif Season Year | `slider` | 2023 | Filter to one season (2018–2023) |
| Crop Type | `multiselect` | All 4 | Filter by dominant crop |
| CLI Alert Threshold | `slider` | 40 | High-risk cutoff across all charts |
| Sum Insured (₹/ha) | `number_input` | 3500 | Maximum PMFBY payout per hectare |
| Trigger Threshold (CLI) | `number_input` | 25 | CLI above which payout activates |

---

## Bug Fixes Applied

This file (`dashboard_fixed.py`) resolves 3 bugs from the original `module5_dashboard.py`:

### Bug 1 — `TypeError: fill_between() got multiple values for argument 'where'`
**Line:** 488 in original  
**Cause:** `ax.fill_between(x, y1, y2, where=[True]*30)` — matplotlib treated `y2` as the `where` parameter because `y2` is the 4th positional argument in the function signature. Passing `where=` as a keyword then conflicted.  
**Fix:** Replaced with `ax.fill()` using explicit polygon vertices:

```python
# ❌ Original — crashes
ax.fill_between(np.cos(t)*0.9, np.sin(t)*0.9,
                np.cos(t)*1.1, np.sin(t)*1.1,
                where=[True]*30, color=clr)

# ✅ Fixed — ring polygon approach
outer_x = np.cos(t) * 1.0;  inner_x = np.cos(t[::-1]) * 0.65
outer_y = np.sin(t) * 1.0;  inner_y = np.sin(t[::-1]) * 0.65
xs = np.concatenate([outer_x, inner_x])
ys = np.concatenate([outer_y, inner_y])
ax8.fill(xs, ys, color=clr, alpha=0.90)
```

### Bug 2 — `DeprecationWarning: use_column_width`
**Cause:** `st.image(..., use_column_width=True)` — deprecated in Streamlit ≥1.20.  
**Fix:** Replaced `st.image()` with `st.markdown("## 🛰️ AgriRisk-Sat")`.

### Bug 3 — VCI `fill_between` missing `interpolate=True`
**Cause:** Without `interpolate=True`, the drought shading had jagged edges at threshold crossing points.  
**Fix:**
```python
ax5.fill_between(dekads, vci_profile, 35,
                 where=(vci_profile < 35),
                 alpha=0.3, color='#FF6B6B',
                 label='Drought stress',
                 interpolate=True)   # ← added
```

---

## Production Integration

### Connect to real GEE pipeline outputs

Replace `load_district_data()` with:

```python
@st.cache_data
def load_district_data():
    return pd.read_csv("python_pipeline/module4_cli_results.csv")
```

### Enable live alert refresh

```python
@st.cache_data(ttl=43200)   # re-fetch every 12 hours (Sentinel-1 cycle)
def get_current_alerts():
    return pd.read_json("current_alerts.json")
```

### Deploy to Streamlit Cloud

1. Push project to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select repo → set main file to `dashboard_fixed.py`
4. Click **Deploy** — public URL generated instantly

### SMS alerts via Twilio

```python
from twilio.rest import Client
client = Client(account_sid, auth_token)
for _, alert in alerts_df[alerts_df['severity'] == 'Extreme'].iterrows():
    client.messages.create(
        body=f"ALERT: {alert['stress']} in {alert['district']} — CLI critical",
        from_="+1XXXXXXXXXX",
        to=field_officer_numbers[alert['district']]
    )
```

---

## Full Project Modules

| Module | File | Description |
|---|---|---|
| M1 — Parcel Delineation | `module1_*_weekly.js` | SNIC segmentation + 26-week NDVI stack + k-means |
| M2 — Crop Mapping | `module2_weekly.js` | Random Forest on weekly feature stack |
| M3 — Stress Detection | `module3_stress_detection.js` | VCI drought + SAR flood + LST heatwave |
| M4 — CLI Computation | `module4_crop_loss_index.py` | Nelder-Mead weight optimisation + PMFBY validation |
| M5 — Dashboard | `dashboard_fixed.py` | This Streamlit app |

---

## Datasets Used

| Dataset | Resolution | Source | Used For |
|---|---|---|---|
| Sentinel-2 MSI | 10m / 5-day | ESA Copernicus / GEE | NDVI, EVI, crop mapping |
| Sentinel-1 SAR | 10m / 12-day | ESA Copernicus / GEE | Flood inundation |
| Landsat 8/9 | 30m / 16-day | USGS / GEE | Land Surface Temperature |
| MODIS MOD13A2 | 1km / 16-day | NASA / GEE | VCI, regional drought |
| CHIRPS Pentad | 5km / 5-day | UCSB / GEE | Rainfall anomaly |
| SMAP L3 | 10km / daily | NASA / GEE | Soil moisture deficit |
| ERA5-Land | 9km / hourly | ECMWF CDS | Temperature, ET₀ |
| Bhuvan LULC | 30m | ISRO Bhuvan | Farm boundaries |
| IMD Gridded | 25km / daily | IMD (open) | Climate normals |

**Processing platform:** Google Earth Engine (free academic tier) + Python 3.12

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: streamlit` | Not installed | `pip install streamlit` |
| `ModuleNotFoundError: matplotlib` | Not installed | `pip install matplotlib` |
| Dashboard shows no data | Empty filtered DataFrame | Check sidebar filters — deselecting all crops empties data |
| No districts in Tab 4 dropdown | `filtered` is empty | Adjust state / year / crop in sidebar |
| Port 8501 already in use | Another Streamlit running | `streamlit run dashboard_fixed.py --server.port 8502` |
| Charts have white background | Dark theme set only on chart area | Normal — `#0a0a1a` is set per-figure not globally |
| `st.stop()` exits app in Tab 4 | District list is empty | Change sidebar filters to include more data |

---

## Glossary

| Term | Meaning |
|---|---|
| **CLI** | Crop Loss Index — composite 0–100 risk score (drought + flood + heat) |
| **VCI** | Vegetation Condition Index — MODIS NDVI normalized against 10-year baseline |
| **NDVI** | Normalized Difference Vegetation Index — optical greenness measure from Sentinel-2 |
| **SAR** | Synthetic Aperture Radar — cloud-penetrating microwave imaging (Sentinel-1) |
| **LST** | Land Surface Temperature — thermal infrared from Landsat 9 |
| **PMFBY** | Pradhan Mantri Fasal Bima Yojana — India's national crop insurance scheme |
| **Kharif** | Summer crop season (Jun–Nov) — cotton, soybean, groundnut, rice |
| **Rabi** | Winter crop season (Nov–Apr) — wheat, mustard, chickpea |
| **Dekad** | 10-day period; 18 dekads cover the full Kharif season |
| **GEE** | Google Earth Engine — cloud platform for satellite data processing |
| **SNIC** | Simple Non-Iterative Clustering — GEE segmentation for farm boundary detection |
| **GJ** | Gujarat (state code used in script print statements) |
| **MH** | Maharashtra (state code) |
| **MP** | Madhya Pradesh (state code) |

---

## License

For academic and research use. Satellite data from ESA Copernicus, NASA EarthData, ECMWF, UCSB CHIRPS, and ISRO Bhuvan — all free for non-commercial use.

---

*Built with ESA Copernicus · NASA EarthData · ECMWF ERA5 · UCSB CHIRPS · ISRO Bhuvan · Google Earth Engine*
