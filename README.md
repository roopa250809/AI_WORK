# WHOOP Insights - Personal Health Analytics Dashboard

A production-ready Streamlit application for analyzing WHOOP health data with Claude AI insights.

## Features

- 📁 **Data Upload**: Import sleep and workout Excel files from WHOOP
- 📊 **Interactive Dashboards**: View trends, distributions, and correlations
- 💤 **Sleep Analytics**: Track duration, quality, stage composition, and consistency
- 🏃 **Workout Tracking**: Monitor intensity, duration, and activity types
- 🔗 **Correlation Analysis**: Understand sleep-workout relationships
- 🤖 **Claude AI Chat**: Ask natural-language questions about your health data
- 📈 **Flexible Date Ranges**: Filter and analyze specific time periods
- 🎨 **Modern UI**: Clean, responsive dashboard with custom styling

## Requirements

- Python 3.11+
- uv (for dependency management)
- WHOOP CSV exports (sleep.csv and workouts.csv)
- Anthropic API key

## Quick Start

### 1. Install uv

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows (with winget)
winget install astral-sh.uv

# Or download from https://github.com/astral-sh/uv/releases
```

### 2. Clone and Setup

```bash
cd whoop-insights
uv sync
```

This creates a virtual environment and installs all dependencies.

### 3. Configure API Key

Create a `.env` file in the project root:

```bash
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
```

Or set it as an environment variable:

```bash
export ANTHROPIC_API_KEY=your-api-key-here
```

### 4. Run the App

```bash
uv run streamlit run app.py
```

The app will open at `http://localhost:8501`

## Project Structure

```
whoop-insights/
├── app.py                    # Main Streamlit application
├── src/
│   ├── __init__.py
│   ├── data_loader.py        # WHOOP Excel file loading & validation
│   ├── metrics.py            # Health metrics computation
│   ├── charts.py             # Plotly chart generation
│   ├── llm.py                # Claude API integration
│   └── utils.py              # Helper utilities
├── pyproject.toml            # uv project configuration
├── .env                      # Environment variables (API keys)
└── README.md                 # This file
```

## Usage

### Uploading Data

1. Click **Upload WHOOP Data** in the sidebar
2. Select your `sleep.csv` file
3. Select your `workouts.csv` file
4. Click **Load Data**

The app automatically:
- Detects column names (flexible to various WHOOP formats)
- Validates data integrity
- Removes invalid rows
- Normalizes formats

### Viewing Dashboard

The dashboard displays:
- **Key Metrics**: Average sleep, quality, consistency, workout count
- **Sleep Trends**: Duration over time with rolling averages
- **Workout Analysis**: Intensity, duration, and activity breakdown
- **Sleep Composition**: Breakdown of deep, light, and REM sleep
- **Correlations**: Sleep vs workout relationships
- **Recovery Insights**: Time between workouts and sleep

### Using Claude Chat

1. Navigate to the **Chat with Claude** tab
2. Ask questions like:
   - "How did my sleep affect workout intensity last week?"
   - "Show trends in my recovery"
   - "What days had poor sleep before heavy workouts?"
3. Claude analyzes your data and provides insights

### Date Filtering

Use the date range selector in the sidebar to analyze specific periods.

## WHOOP Column Mappings

The app auto-detects these columns (case-insensitive):

### Sleep Data
| Standard Name | Possible WHOOP Names |
|---|---|
| date | date, sleep_date, Date, Sleep Date |
| start_time | start_time, sleep_start, Start Time |
| end_time | end_time, sleep_end, End Time |
| duration_min | duration_minutes, Duration (Minutes) |
| sleep_quality | quality, score, Sleep Quality |
| deep_sleep_min | deep_sleep, Deep Sleep (Minutes) |
| light_sleep_min | light_sleep, Light Sleep (Minutes) |
| rem_sleep_min | rem_sleep, REM Sleep (Minutes) |
| respiratory_rate | respiratory_rate, HR |
| hrv | hrv, Heart Rate Variability |
| resting_hr | resting_hr, Resting HR |

### Workout Data
| Standard Name | Possible WHOOP Names |
|---|---|
| date | date, workout_date, Date |
| start_time | start_time, workout_start, Start Time |
| end_time | end_time, workout_end, End Time |
| duration_min | duration_minutes, Duration (Minutes) |
| activity_type | activity, activity_type, Sport |
| workout_intensity | intensity, strain, Intensity |
| calories_burned | calories, Calories Burned |
| avg_heart_rate | avg_hr, Avg HR |
| max_heart_rate | max_hr, Max HR |

**If your columns don't match**, rename them in Excel before uploading or update the mappings in `src/data_loader.py`.

## Sample Data

Click **Use Sample Data (Demo)** in the sidebar to test the app with generated sample data.

## Health Metrics Explained

- **Sleep Duration**: Total hours of sleep per night
- **Sleep Quality**: WHOOP's sleep quality score (0-100)
- **Sleep Consistency**: Measure of sleep duration variance (0-100)
- **Workout Frequency**: Average workouts per day
- **Workout Intensity**: Average intensity score (0-100)
- **Sleep-Workout Correlation**: How sleep relates to workout frequency (-1 to 1)
- **Recovery Time**: Hours between workout end and next sleep start

## API Integration

The app uses:
- **Anthropic Claude 3.5 Sonnet**: For intelligent health insights
- **Messages API**: Stateful conversation with metrics context
- **Streaming**: Optional (not used by default for simplicity)

Claude receives only:
- Your processed metrics (not raw data)
- Your specific question
- Recent trends and patterns

No raw WHOOP data is sent to Claude.

## Error Handling

The app gracefully handles:
- Missing or invalid dates
- Empty columns
- Mismatched column names
- Invalid numeric values
- Empty uploads
- API connection issues

Errors are displayed as friendly messages in the UI.

## Performance Notes

- Uses Streamlit's `@st.cache_data` for expensive computations
- Handles datasets with 1000+ records smoothly
- Responsive UI with instant chart updates
- Efficient date filtering

## Development

### Install Dev Dependencies

```bash
uv sync --all-extras
```

### Run Linting

```bash
uv run black src app.py
uv run ruff check src app.py
```

### Type Checking

```bash
uv run mypy src app.py
```

## Extending the App

### Adding New Metrics

1. Add calculation to `src/metrics.py` in `HealthMetricsCalculator`
2. Call it in `get_summary_metrics()`
3. Use in `app.py` dashboard or Claude prompts

### Adding New Charts

1. Create function in `src/charts.py`
2. Return Plotly figure
3. Render in dashboard tabs

### Customizing Claude Prompts

Edit `system_prompt` in `src/llm.py` to change AI behavior.

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
- Ensure `.env` file exists in project root
- Or set environment variable: `export ANTHROPIC_API_KEY=your-key`
- Restart the app after changing

### "No date column found"
- Check that your Excel files have a date column
- Try renaming to "Date" or "date"
- See Column Mappings section above

### Charts don't update
- Try clicking "Rerun" in Streamlit
- Or refresh the browser
- Check that data is loaded in sidebar

### Claude gives generic answers
- Make sure API key is valid
- Check internet connection
- Try asking more specific questions

## License

MIT

## Credits

Built with:
- [Streamlit](https://streamlit.io/) - Dashboard framework
- [Plotly](https://plotly.com/) - Interactive charts
- [Pandas](https://pandas.pydata.org/) - Data processing
- [NumPy](https://numpy.org/) - Numerical computing
- [Anthropic Claude](https://www.anthropic.com/) - AI insights
- [uv](https://astral.sh/uv/) - Python package manager

## Support

For issues with:
- **WHOOP data format**: Check the column mappings above
- **Claude responses**: Ensure API key and internet connection
- **App performance**: Reduce date range or dataset size
- **Features**: See extending the app section above
