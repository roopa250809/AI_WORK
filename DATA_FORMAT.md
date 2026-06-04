# WHOOP Data Format Guide

This document explains how to export WHOOP data to CSV format and what columns the app expects.

## Exporting from WHOOP App

1. Open the WHOOP app
2. Go to **Settings** → **Data Export**
3. Export as **CSV** format
4. You'll get two files:
   - `sleep.csv` - Contains all sleep data
   - `workouts.csv` - Contains all workout data

## Expected Data Structure

### Sleep Data (sleep.csv)

Required columns:
- **Date** - Date of the sleep (any format)

Optional columns:
- Sleep duration (minutes)
- Sleep quality score
- Deep sleep duration
- Light sleep duration
- REM sleep duration
- Resting heart rate
- Heart rate variability (HRV)

Example structure:
```
Date          | Duration (Minutes) | Quality Score | Deep Sleep | Light Sleep | REM Sleep
2024-01-01    | 450                | 75            | 80         | 200         | 170
2024-01-02    | 420                | 68            | 70         | 195         | 155
```

### Workout Data (workouts.csv)

Required columns:
- **Date** - Date of the workout

Optional columns:
- Workout start time
- Workout end time
- Duration (minutes)
- Activity type
- Intensity/Strain score
- Calories burned
- Average heart rate
- Maximum heart rate

Example structure:
```
Date       | Duration (Minutes) | Activity   | Intensity | Calories | Avg HR | Max HR
2024-01-01 | 60                 | Running    | 70        | 500      | 140    | 180
2024-01-02 | 45                 | Cycling    | 65        | 350      | 130    | 170
```

## Column Name Flexibility

The app automatically detects common WHOOP column names:

### Sleep Column Variants
- Duration: `duration_min`, `duration_minutes`, `Duration (Minutes)`, `Duration`
- Quality: `quality`, `score`, `Sleep Quality`, `Quality Score`
- Deep Sleep: `deep_sleep`, `deep_sleep_min`, `Deep Sleep (Minutes)`
- Light Sleep: `light_sleep`, `light_sleep_min`, `Light Sleep (Minutes)`
- REM Sleep: `rem_sleep`, `rem_sleep_min`, `REM Sleep (Minutes)`

### Workout Column Variants
- Duration: `duration_min`, `duration_minutes`, `Duration (Minutes)`, `Duration`
- Activity: `activity`, `activity_type`, `Activity Type`, `Sport`
- Intensity: `intensity`, `strain`, `Intensity`, `Strain Score`
- Calories: `calories`, `calories_burned`, `Calories Burned`
- Avg HR: `avg_hr`, `average_heart_rate`, `Avg HR`, `Average Heart Rate`
- Max HR: `max_hr`, `maximum_heart_rate`, `Max HR`

## If Columns Don't Match

If your WHOOP export has different column names:

**Option 1: Rename in Excel**
1. Open the Excel file
2. Rename columns to match the expected names (see above)
3. Save and upload

**Option 2: Update Column Mappings**
Edit `src/data_loader.py` and add your column names to:
- `SLEEP_COLUMNS` dictionary
- `WORKOUT_COLUMNS` dictionary

Example:
```python
SLEEP_COLUMNS = {
    'date': ['date', 'sleep_date', 'Date', 'Sleep Date', 'YOUR_DATE_COLUMN'],
    ...
}
```

## Data Validation

The app performs these checks:
- ✅ Date column exists and is valid
- ✅ All dates can be parsed
- ✅ Numeric columns are properly typed
- ✅ No required columns are missing
- ✅ Data is sorted by date

Invalid rows are removed with a warning message shown in the UI.

## Missing Data

The app handles missing values gracefully:
- Empty cells are ignored in calculations
- Charts skip missing data points
- Metrics exclude NA values
- Averages are computed from available data

## Date Formats Supported

The app accepts dates in these formats:
- `2024-01-15`
- `01/15/2024`
- `2024-01-15 10:30:00`
- `01/15/2024 10:30:00`
- Any format pandas can parse

## Common Issues

### "No date column found"
- Ensure your Excel file has a date column
- Check that it's named something like "Date", "date", or "sleep_date"
- Try renaming to "Date" if using a custom name

### Dates showing as "Invalid"
- Excel might be storing dates as numbers
- Right-click column → Format Cells → Date
- Re-export from WHOOP

### Missing optional metrics
- Not all WHOOP exports include every metric
- The app will skip missing columns
- Only available metrics will show in charts

## Sample Data Structure

Here's a minimal example to test:

**sleep.csv**
```
date       | duration_min | sleep_quality
2024-06-01 | 450          | 75
2024-06-02 | 420          | 68
2024-06-03 | 480          | 82
```

**workouts.csv**
```
date       | duration_min | activity_type | workout_intensity
2024-06-01 | 60           | Running       | 70
2024-06-02 | 45           | Cycling       | 65
2024-06-03 | 30           | Yoga          | 40
```
