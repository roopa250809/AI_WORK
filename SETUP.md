# WHOOP Insights - Setup Guide

Complete step-by-step instructions to get the app running on your machine.

## Prerequisites

- **Python 3.11+** installed on your system
  - Check: `python --version` or `python3 --version`
- **uv** package manager (we'll install this)
- **Anthropic API key** (get from https://console.anthropic.com)
- **WHOOP account** with data to export

## Installation Steps

### 1. Install uv (if not already installed)

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (with winget):**
```bash
winget install astral-sh.uv
```

**Windows (with pip):**
```bash
pip install uv
```

**Verify installation:**
```bash
uv --version
```

### 2. Clone or Download the Project

```bash
# Option A: Clone from git
git clone <repository-url>
cd whoop-insights

# Option B: Download manually
# Extract the whoop-insights folder and navigate to it
cd whoop-insights
```

### 3. Set Up Virtual Environment & Install Dependencies

```bash
# This creates a .venv folder and installs all dependencies
uv sync
```

The first run may take a few minutes. This will install:
- streamlit (UI framework)
- pandas & numpy (data processing)
- plotly (charts)
- anthropic (Claude API)
- python-dotenv (environment variables)

### 4. Configure Anthropic API Key

**Option A: Using .env file (Recommended)**

Create a `.env` file in the project root:

```bash
# Create the file
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
```

Replace `your-api-key-here` with your actual API key from Anthropic.

**Option B: Environment variable**

```bash
# macOS/Linux
export ANTHROPIC_API_KEY=your-api-key-here

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="your-api-key-here"

# Windows (Command Prompt)
set ANTHROPIC_API_KEY=your-api-key-here
```

### 5. Run the App

```bash
uv run streamlit run app.py
```

The app will:
- Open automatically in your browser (usually `http://localhost:8501`)
- Or display a URL you can copy to your browser

### 6. Start Using the App

1. **Load Sample Data**: Click "Use Sample Data (Demo)" to test features
2. **Export WHOOP Data**: See "Exporting WHOOP Data" section below
3. **Upload Your Data**: Use sidebar to upload sleep.csv and workouts.csv
4. **Explore Dashboard**: View your health metrics and trends
5. **Chat with Claude**: Ask questions about your data

## Exporting WHOOP Data

### From WHOOP Mobile App

1. Open WHOOP app
2. Go to **Settings** → **Data Export** (or **Profile** → **Settings**)
3. Select **Export as Excel**
4. Choose date range (or select all)
5. Files will be downloaded:
   - `sleep.csv`
   - `workouts.csv`

### From WHOOP Web Dashboard

1. Visit https://www.whoop.com/
2. Log in to your account
3. Go to **Settings** → **Data** or **Export**
4. Download your data as Excel

## First Time Use

### Quick Test with Sample Data

1. Run the app: `uv run streamlit run app.py`
2. In the sidebar, check **"Use Sample Data (Demo)"`
3. View the dashboard immediately
4. Try asking Claude a question in the "Chat with Claude" tab

### With Your Own Data

1. Export WHOOP data (see above)
2. Run the app: `uv run streamlit run app.py`
3. In sidebar, click **"Sleep Data (CSV)"** and select your `sleep.csv`
4. Click **"Workout Data (CSV)"** and select your `workouts.csv`
5. Click **"📂 Load Data"**
6. Wait for validation messages
7. Once loaded, explore the dashboard

## Troubleshooting

### "ModuleNotFoundError" or import errors

```bash
# Reinstall dependencies
uv sync --refresh
```

### "ANTHROPIC_API_KEY not found"

Check that:
1. `.env` file exists in project root
2. `.env` contains: `ANTHROPIC_API_KEY=sk-ant-...`
3. API key is valid (from https://console.anthropic.com)
4. Restart the app after adding/changing the key

### "No module named streamlit"

```bash
# Reinstall all dependencies
uv sync
```

### Port 8501 already in use

```bash
# Use a different port
uv run streamlit run app.py --server.port 8502
```

### Date parsing errors

See `DATA_FORMAT.md` for supported date formats. If your Excel dates look wrong:
1. Open in Excel
2. Format the date column as "Date" format
3. Save and try again

### Charts not appearing

- Make sure you've uploaded both sleep and workout files
- Check that the date range filter includes your data
- Try refreshing the browser or clicking "Rerun" button

### Claude gives generic answers

1. Verify API key is valid
2. Check your internet connection
3. Try a more specific question
4. Check that data is properly loaded in the sidebar

## File Structure

```
whoop-insights/
├── app.py                 # Main Streamlit app (run this)
├── pyproject.toml        # Dependencies configuration
├── .env                  # API key (create this)
├── README.md             # Full documentation
├── DATA_FORMAT.md        # Data format guide
├── SETUP.md              # This file
├── .gitignore            # Git ignore rules
├── .venv/                # Virtual environment (auto-created by uv)
└── src/                  # Source code modules
    ├── __init__.py
    ├── data_loader.py    # Load Excel files
    ├── metrics.py        # Calculate health metrics
    ├── charts.py         # Generate charts
    ├── llm.py            # Claude integration
    └── utils.py          # Helper functions
```

## Running Commands with uv

All Python commands should use `uv run`:

```bash
# Run the app
uv run streamlit run app.py

# Run a Python script
uv run python script.py

# Install more packages
uv add new-package

# Run in shell
uv run python
```

## Updating Dependencies

If you want to add more packages:

```bash
# Add a package
uv add package-name

# Update all packages
uv sync --upgrade

# Add dev dependency
uv add --dev package-name
```

## Tips & Best Practices

1. **Always use `uv run`** - Don't activate venv manually
2. **Keep .env secure** - Don't commit it to git (see .gitignore)
3. **Export full history** - Export all available WHOOP data for best insights
4. **Regular exports** - Weekly exports capture trends better
5. **Use date filter** - Focus on specific weeks/months for detailed analysis
6. **Try sample data first** - Test features before uploading your data

## Getting Help

### Documentation
- See `README.md` for full app documentation
- See `DATA_FORMAT.md` for WHOOP data format details

### Common Issues
- Check troubleshooting section above
- Review error messages shown in Streamlit
- Check that all files are in place (`app.py`, `src/` folder)

### API Issues
- Verify API key at https://console.anthropic.com
- Check that key starts with `sk-ant-`
- Ensure you have API credits available

### Data Issues
- See `DATA_FORMAT.md` for column name mapping
- Try renaming columns in Excel to match expected names
- Test with sample data first

## Updating the App

To get the latest version:

```bash
# Update from git
git pull origin main

# Reinstall dependencies
uv sync
```

## Stopping the App

Press `Ctrl+C` in the terminal where Streamlit is running.

To clean up:
```bash
# Remove virtual environment
rm -rf .venv

# Next time, just run: uv sync
```

## Next Steps

1. ✅ Complete this setup
2. 📊 Export your WHOOP data
3. 🚀 Run the app
4. 📈 Upload your data
5. 🤖 Chat with Claude
6. 📚 Check README.md for advanced features

---

**You're all set!** Run `uv run streamlit run app.py` to get started.
