"""
Configuration and example data structures for WHOOP exports.
This file documents expected data formats and can be used as reference.
"""

# Example Sleep Data Structure
EXAMPLE_SLEEP_DATA = {
    'columns': [
        'Date',
        'Start Time',
        'End Time',
        'Duration (minutes)',
        'Sleep Quality (percentage)',
        'Deep Sleep (minutes)',
        'Light Sleep (minutes)',
        'REM Sleep (minutes)',
        'Respiratory Rate',
        'Resting Heart Rate',
        'Heart Rate Variability',
    ],
    'sample_rows': [
        {
            'Date': '2024-06-01',
            'Start Time': '23:15',
            'End Time': '07:30',
            'Duration (minutes)': 495,
            'Sleep Quality (percentage)': 78,
            'Deep Sleep (minutes)': 95,
            'Light Sleep (minutes)': 215,
            'REM Sleep (minutes)': 185,
            'Respiratory Rate': 15.2,
            'Resting Heart Rate': 58,
            'Heart Rate Variability': 52,
        },
        {
            'Date': '2024-06-02',
            'Start Time': '23:45',
            'End Time': '07:15',
            'Duration (minutes)': 450,
            'Sleep Quality (percentage)': 72,
            'Deep Sleep (minutes)': 80,
            'Light Sleep (minutes)': 200,
            'REM Sleep (minutes)': 170,
            'Respiratory Rate': 15.5,
            'Resting Heart Rate': 61,
            'Heart Rate Variability': 48,
        },
    ]
}

# Example Workout Data Structure
EXAMPLE_WORKOUT_DATA = {
    'columns': [
        'Date',
        'Start Time',
        'End Time',
        'Duration (minutes)',
        'Activity Type',
        'Intensity Score',
        'Calories Burned',
        'Average Heart Rate',
        'Maximum Heart Rate',
    ],
    'sample_rows': [
        {
            'Date': '2024-06-01',
            'Start Time': '07:00',
            'End Time': '08:00',
            'Duration (minutes)': 60,
            'Activity Type': 'Running',
            'Intensity Score': 75,
            'Calories Burned': 520,
            'Average Heart Rate': 155,
            'Maximum Heart Rate': 185,
        },
        {
            'Date': '2024-06-02',
            'Start Time': '17:30',
            'End Time': '18:30',
            'Duration (minutes)': 60,
            'Activity Type': 'Strength Training',
            'Intensity Score': 68,
            'Calories Burned': 480,
            'Average Heart Rate': 130,
            'Maximum Heart Rate': 165,
        },
    ]
}

# Common WHOOP Activity Types
WHOOP_ACTIVITY_TYPES = [
    'Running',
    'Cycling',
    'Strength Training',
    'Rowing',
    'Swimming',
    'Yoga',
    'Tennis',
    'Basketball',
    'Soccer',
    'Football',
    'Baseball',
    'Pilates',
    'Functional Fitness',
    'HIIT',
    'Rock Climbing',
    'Hiking',
    'Walking',
    'Skiing',
    'Snowboarding',
    'Surfing',
    'CrossFit',
    'Boxing',
    'MMA',
    'Gymnastics',
    'Ballet',
    'Golf',
    'American Football',
    'Badminton',
    'Handball',
    'Ice Hockey',
    'Skating',
    'Squash',
    'Taekwondo',
    'Volleyball',
    'Weightlifting',
]

# Typical WHOOP Data Ranges and Thresholds
WHOOP_RANGES = {
    'sleep': {
        'min_duration_hours': 4,
        'max_duration_hours': 10,
        'good_duration_hours': 7.5,
        'quality_good_threshold': 70,
        'quality_excellent_threshold': 85,
    },
    'workout': {
        'min_intensity': 0,
        'max_intensity': 100,
        'low_intensity_threshold': 30,
        'moderate_intensity_threshold': 60,
        'high_intensity_threshold': 80,
        'min_duration_minutes': 15,
        'max_duration_minutes': 240,
    },
    'recovery': {
        'hours_post_workout_to_sleep': 8,
        'min_hours': 6,
        'max_hours': 24,
    },
    'heart_rate': {
        'resting_good': (55, 70),
        'resting_excellent': (40, 60),
        'max_estimate_formula': '220 - age',
    }
}

# Health Metric Interpretations
METRIC_INTERPRETATIONS = {
    'sleep_consistency_score': {
        'excellent': (85, 100),
        'good': (70, 84),
        'fair': (50, 69),
        'poor': (0, 49),
    },
    'sleep_quality': {
        'excellent': (85, 100),
        'good': (70, 84),
        'fair': (50, 69),
        'poor': (0, 49),
    },
    'workout_intensity': {
        'light': (0, 30),
        'moderate': (30, 60),
        'intense': (60, 80),
        'very_intense': (80, 100),
    },
    'workout_frequency': {
        'none': 0,
        'low': (0, 2),
        'moderate': (2, 5),
        'high': (5, 7),
        'very_high': (7, 20),
    },
}

# Column Name Variations (for flexible importing)
COLUMN_VARIATIONS = {
    'date': [
        'date',
        'sleep_date',
        'workout_date',
        'Date',
        'Sleep Date',
        'Workout Date',
        'DATE',
        'SLEEP_DATE',
        'WORKOUT_DATE',
    ],
    'sleep_duration': [
        'duration',
        'duration_min',
        'duration_minutes',
        'sleep_duration',
        'Duration',
        'Duration (min)',
        'Duration (minutes)',
        'Sleep Duration',
        'DURATION',
        'DURATION_MIN',
        'DURATION_MINUTES',
    ],
    'sleep_quality': [
        'quality',
        'score',
        'quality_score',
        'sleep_quality',
        'Quality',
        'Quality Score',
        'Sleep Quality',
        'Quality (%)',
        'Quality (percentage)',
        'QUALITY',
        'QUALITY_SCORE',
        'SLEEP_QUALITY',
    ],
    'activity_type': [
        'activity',
        'activity_type',
        'sport',
        'type',
        'Activity',
        'Activity Type',
        'Sport',
        'Type',
        'ACTIVITY',
        'ACTIVITY_TYPE',
        'SPORT',
    ],
    'intensity': [
        'intensity',
        'strain',
        'intensity_score',
        'strain_score',
        'Intensity',
        'Strain',
        'Intensity Score',
        'Strain Score',
        'INTENSITY',
        'STRAIN',
    ],
}

# Recommended Thresholds for Insights
RECOMMENDED_THRESHOLDS = {
    'sleep': {
        'minimum_hours': 7,
        'optimal_hours': 7.5,
        'target_hours': 8,
        'consistency_score_target': 80,
    },
    'workout': {
        'workouts_per_week': 3.5,
        'minutes_per_week': 300,  # 5 hours
        'intensity_variety': True,
    },
    'recovery': {
        'hours_between_intense_workouts': 48,
        'hours_post_workout_to_sleep': 8,
    },
}

# Default Chart Colors
CHART_COLORS = {
    'primary': '#3498DB',      # Blue
    'secondary': '#E74C3C',    # Red
    'success': '#2ECC71',      # Green
    'warning': '#F39C12',      # Orange
    'danger': '#E67E22',       # Dark Orange
    'info': '#9B59B6',         # Purple
    'light': '#ECF0F1',        # Light Gray
    'dark': '#2C3E50',         # Dark Blue
    'sleep': '#5DADE2',        # Light Blue
    'workout': '#58D68D',      # Light Green
    'recovery': '#F5B041',     # Yellow-Orange
}

if __name__ == '__main__':
    print("WHOOP Insights Configuration Reference")
    print("=" * 50)
    print("\nSample Sleep Data:")
    print(EXAMPLE_SLEEP_DATA['columns'])
    print("\nSample Workout Data:")
    print(EXAMPLE_WORKOUT_DATA['columns'])
    print("\nActivity Types:")
    for activity in WHOOP_ACTIVITY_TYPES:
        print(f"  - {activity}")
