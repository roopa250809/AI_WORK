"""Quick smoke test for the WHOOP dashboard modules."""
import sys
sys.path.insert(0, '.')

from src.data_loader import WHOOPDataLoader, validate_data
from src.metrics import WorkoutMetrics
from src.charts import (
    chart_duration_by_day, chart_calories_over_time, chart_strain_over_time,
    chart_activity_distribution, chart_avg_duration_by_activity,
    chart_total_calories_by_activity, chart_avg_hr_trend, chart_max_hr_trend,
    chart_hr_zone_distribution, chart_duration_vs_calories,
    chart_strain_vs_calories, chart_strain_vs_avg_hr,
    chart_weekly_workout_count, chart_weekly_duration, chart_weekly_calories,
    chart_monthly_summary,
)

print("=== Loading data ===")
df, msgs = WHOOPDataLoader.load_workout_data('sample_workouts.csv')
print(f"Rows: {len(df)}")
print(f"Columns: {list(df.columns)}")
print(f"Messages: {msgs}")

print("\n=== KPI Summary ===")
kpi = WorkoutMetrics.kpi_summary(df)
for k, v in kpi.items():
    print(f"  {k}: {v}")

print("\n=== Personal Records ===")
records = WorkoutMetrics.personal_records(df)
for k, v in records.items():
    print(f"  {k}: {v}")

print("\n=== Weekly Training Load ===")
print(f"  Avg weekly: {WorkoutMetrics.avg_weekly_training_load(df)}")
print(f"  Avg monthly: {WorkoutMetrics.avg_monthly_training_load(df)}")

print("\n=== Insights ===")
for insight in WorkoutMetrics.generate_insights(df):
    print(f"  {insight}")

print("\n=== Charts (smoke test) ===")
charts = [
    ("duration_by_day", chart_duration_by_day(df)),
    ("calories_over_time", chart_calories_over_time(df)),
    ("strain_over_time", chart_strain_over_time(df)),
    ("activity_distribution", chart_activity_distribution(df)),
    ("avg_duration_by_activity", chart_avg_duration_by_activity(df)),
    ("total_calories_by_activity", chart_total_calories_by_activity(df)),
    ("avg_hr_trend", chart_avg_hr_trend(df)),
    ("max_hr_trend", chart_max_hr_trend(df)),
    ("hr_zone_distribution", chart_hr_zone_distribution(df)),
    ("duration_vs_calories", chart_duration_vs_calories(df)),
    ("strain_vs_calories", chart_strain_vs_calories(df)),
    ("strain_vs_avg_hr", chart_strain_vs_avg_hr(df)),
    ("weekly_workout_count", chart_weekly_workout_count(df)),
    ("weekly_duration", chart_weekly_duration(df)),
    ("weekly_calories", chart_weekly_calories(df)),
    ("monthly_summary", chart_monthly_summary(df)),
]
for name, fig in charts:
    traces = len(fig.data)
    print(f"  ✅ {name}: {traces} trace(s)")

print("\n=== Validate data ===")
ok, errors = validate_data(None, df)
print(f"  Valid: {ok}, Errors: {errors}")

print("\n✅ All tests passed!")
