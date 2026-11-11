# Manufacturing Downtime & Root Cause Intelligence

An industrial sensor data analytics project that investigates compressor performance and documented air-leak events using Python, SQL, and Power BI.

## Project Overview

Industrial equipment generates large amounts of sensor data. Analysing this data can help identify unusual operating patterns and support equipment investigation.

This project analyses the MetroPT-3 Air Compressor dataset to understand sensor behaviour during documented air-leak periods.

The project combines data preprocessing, exploratory data analysis, SQL-based investigation, rule-based sensor analysis, chronological validation, and interactive Power BI dashboards.

## Objectives

- Process and validate large-scale industrial sensor data.
- Investigate sensor behaviour across normal and documented air-leak periods.
- Analyse pressure, temperature, and motor current measurements.
- Perform structured analysis using SQL.
- Develop a rule-based sensor investigation method.
- Evaluate the investigation method using chronological validation.
- Present findings through interactive Power BI dashboards.

## Dataset

**Dataset:** MetroPT-3 Air Compressor Dataset  
**Source:** UCI Machine Learning Repository  
**Equipment:** Air Production Unit (APU) compressor installed in a metro train.

The dataset contains 1,516,948 sensor observations collected between February and September 2020.

### Important Variables

| Variable | Description |
|---|---|
| TP2 | Compressor pressure measurement |
| TP3 | Pressure measurement |
| H1 | Pressure-related sensor measurement |
| Reservoirs | Air reservoir pressure |
| Oil_temperature | Compressor oil temperature |
| Motor_current | Electrical current drawn by the motor |
| DV_eletric | Electrical valve state |
| COMP | Compressor state indicator |
| Towers | Tower operating-state indicator |
| LPS | Low-pressure switch signal |
| MPG | Compressor-related operating indicator |

The dataset includes four documented air-leak periods, which are used as event categories for retrospective analysis.

**Note:** The documented event periods are time-window labels, not independently verified fault labels for every individual observation.

## Technology Stack

- **Python:** Data processing and analysis
- **Pandas & NumPy:** Data manipulation and numerical analysis
- **Matplotlib & Seaborn:** Data visualisation
- **SQL:** Structured data analysis
- **SQLite:** Database storage
- **Power BI:** Interactive dashboard development
- **VS Code:** Development environment

## Project Workflow

### 1. Data Inspection and Cleaning

- Inspected the original dataset.
- Converted timestamps into datetime format.
- Checked missing values and invalid timestamps.
- Validated record ordering.
- Created labelled data for the documented air-leak periods.

**Result:** 1,516,948 observations processed, with zero missing values and zero invalid timestamps.

### 2. Exploratory Data Analysis

Analysed sensor behaviour across normal and documented air-leak periods.

Key variables included:
- TP2 and TP3 pressure.
- Reservoir pressure.
- Oil temperature.
- Motor current.

Visualisations were created to compare sensor patterns across event categories.

### 3. SQL Analysis

Stored the processed dataset in SQLite and performed queries to investigate:

- Total sensor records.
- Event-category distribution.
- Date ranges.
- Sensor averages by event category.
- Operating-state comparisons.

### 4. Operating-State Analysis

Compared sensor readings under the same `DV_eletric = 1` operating state to reduce differences caused by this particular operating-state indicator.

The analysis showed higher average oil temperatures and lower pressure readings during certain documented air-leak periods compared with normal operation.

### 5. Rule-Based Sensor Investigation

Developed a threshold-based investigation method using three sensor conditions:

- TP3 below its reference threshold.
- Reservoir pressure below its reference threshold.
- Oil temperature above its reference threshold.

A combined alert was generated when both the pressure condition and temperature condition were satisfied.

This was a manually designed investigation rule rather than a trained machine learning model.

### 6. Chronological Validation

Used historical normal operating records before June 2020 to calculate sensor thresholds and evaluated the rules on a later period.

The validation focused on Air_Leak_3 and Air_Leak_4.

### 7. Power BI Dashboard

Developed a two-page interactive dashboard.

**Page 1 – Event Overview**
- Total sensor records.
- Documented failure-window records.
- Documented air-leak events.
- Event distribution.
- Average oil temperature.
- Average motor current.
- Average pressure.

**Page 2 – Sensor Analysis**
- TP2 trends.
- Reservoir pressure trends.
- Motor current trends.
- Oil temperature trends.
- Event-category slicer.

## Key Results

### Dataset Summary

| Metric | Result |
|---|---:|
| Total observations | 1,516,948 |
| Documented air-leak periods | 4 |
| Event-window observations | 29,954 |
| Normal-labelled observations | 1,486,994 |

### Chronological Validation Results

| Category | Records | Combined Alerts | Alert Rate |
|---|---:|---:|---:|
| Normal | 100,600 | 440 | 0.437% |
| Air_Leak_3 | 17,315 | 7,337 | 42.374% |
| Air_Leak_4 | 1,579 | 755 | 47.815% |

The combined pressure and temperature alert condition occurred more frequently during the two documented air-leak periods than during normal observations in the validation period.

These results indicate potentially useful sensor patterns for retrospective investigation. They should not be interpreted as predictive model accuracy or proof of real-time fault detection.

## Repository Structure

```text
Manufacturing-Downtime-Intelligence/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── src/
│   ├── inspect_data.py
│   ├── clean_data.py
│   ├── validate_data.py
│   ├── label_failures.py
│   ├── analyze_failures.py
│   ├── state_matched_analysis.py
│   ├── sensor_rule_investigation.py
│   └── chronological_validation.py
│
├── sql/
│   └── analysis_queries.sql
│
├── powerbi/
│   ├── Manufacturing_Downtime_Dashboard.pbix
│   └── data/
│
├── reports/
│
├── requirements.txt
├── .gitignore
└── README.md
```

## How to Run the Project

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Manufacturing-Downtime-Intelligence
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Download the dataset

Download the MetroPT-3 Air Compressor dataset from the UCI Machine Learning Repository.

Place the original CSV file at:

```text
data/raw/MetroPT3(AirCompressor).csv
```

### 6. Run the analysis scripts

Run the Python scripts from the project root directory in the appropriate workflow order.

The scripts in `src/` cover data inspection, cleaning, validation, event labelling, analysis, database creation, sensor investigation, and chronological validation.

The Power BI dashboard can be opened using Power BI Desktop.

## Project Limitations

- The dataset represents one compressor unit, not multiple independent manufacturing machines.
- Event labels are based on documented time windows.
- The dataset does not provide repair timestamps or production output.
- MTTR, MTBF, and OEE cannot be reliably calculated from the available data.
- The rule-based method is intended for retrospective investigation, not established real-time prediction.
- Chronological validation is limited to two documented air-leak periods and is not a fully independent predictive benchmark.

## Future Scope

- Evaluate the methodology on additional industrial datasets.
- Incorporate confirmed maintenance and fault records.
- Explore independently validated machine learning models.
- Develop real-time sensor monitoring.
- Integrate alerts with maintenance management systems.
- Incorporate production and repair data for maintenance KPI calculations.

## Conclusion

This project demonstrates how industrial sensor data can be transformed into meaningful analytical insights using Python, SQL, and Power BI.

It combines data cleaning, sensor comparison, operating-state analysis, rule-based investigation, chronological validation, and dashboard development to explore compressor behaviour during documented air-leak periods.

The project provides a foundation for further work in industrial analytics and predictive maintenance.

---

**Developed using:** Python | SQL | SQLite | Power BI