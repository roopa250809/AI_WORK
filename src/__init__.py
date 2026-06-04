"""WHOOP Insights - Fitness Analytics Dashboard"""

__version__ = "0.2.0"

# Re-export key classes so Streamlit can always find them
# regardless of bytecode cache state.

from src.data_loader import WHOOPDataLoader, validate_data
