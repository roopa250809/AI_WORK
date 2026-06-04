# Quick Start Guide — CSV Data Analyzer

Get the app running in under 2 minutes.

---

## 1️⃣ Install Dependencies

```bash
# Install uv (if not already installed)
pip install uv

# Sync the project environment
python -m uv sync
```

## 2️⃣ Run the App

```bash
python -m uv run streamlit run app.py
```

Your browser will open automatically at `http://localhost:8501`.

---

## 3️⃣ Load Data

### Option A — Try the Sample Data (instant)
- In the sidebar, check **"Use sample data (WHOOP workouts demo)"**
- The dashboard loads immediately with 226 rows of workout data

### Option B — Upload Your Own CSV
- Click **"Upload a CSV file"** in the sidebar
- Any CSV file works — sales data, survey results, sensor readings, etc.

---

## 4️⃣ Explore the 5 Tabs

| Tab | What you can do |
|-----|----------------|
| 📂 **Upload** | Preview rows, see column types, null counts, unique values |
| 🔍 **Explore** | Summary stats, missing-value chart, filter & sort rows, download filtered CSV |
| 📈 **Visualize** | Bar, line, scatter, histogram, pie charts — pick axes, aggregation, color |
| 💡 **Insights** | Top-N values, correlation matrix heatmap, auto-generated NL insights |
| 🧹 **Clean** | Drop nulls, fill nulls (mean/median/mode/custom), remove duplicates, cast dtypes, download cleaned CSV |

---

## Common Commands

```bash
# Run the app
python -m uv run streamlit run app.py

# Run on a different port
python -m uv run streamlit run app.py --server.port 8502

# Add a new package
python -m uv add <package-name>

# Update all packages
python -m uv sync --upgrade
```

---

## Project Structure

```
whoop-insights/
├── app.py                  # Main Streamlit app (5 tabs)
├── pyproject.toml          # uv project config & dependencies
├── sample_workouts.csv     # Sample data for demo
└── src/
    ├── csv_analyzer.py     # Core data logic (load, stats, clean, insights)
    └── viz_builder.py      # Plotly chart builders (bar, line, scatter, etc.)
```

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web UI framework |
| `pandas` | Data processing |
| `plotly` | Interactive charts |
| `numpy` | Numerical operations |
| `scipy` | OLS trendlines in scatter plots |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Run `python -m uv sync --refresh` |
| Port 8501 in use | Use `--server.port 8502` flag |
| CSV won't parse | Ensure file is UTF-8 encoded; try re-saving from Excel |
| Charts look empty | Check that the selected columns have non-null numeric data |
