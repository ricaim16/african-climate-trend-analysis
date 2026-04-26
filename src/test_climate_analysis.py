import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from src.climate_analysis import load_and_clean_data, compute_country_trends

@pytest.fixture
def sample_data(tmp_path):
    """Creates a temporary CSV file for testing."""
    csv_path = tmp_path / "test_data.csv"
    data = {
        "country": ["Kenya", "Kenya", "Nigeria", "Nigeria"],
        "year": [2000, 2001, 2000, 2001],
        "temperature_c": [20.0, 21.0, 30.0, 30.0],
        "rainfall_mm": [100.0, 110.0, 50.0, 40.0]
    }
    pd.DataFrame(data).to_csv(csv_path, index=False)
    return csv_path

def test_data_cleaning(sample_data):
    """Tests if the data is loaded and typed correctly."""
    df = load_and_clean_data(sample_data)
    assert len(df) == 4
    assert df["year"].dtype == "int64"
    assert "country" in df.columns

def test_trend_calculation(sample_data):
    """Tests if the slope calculation is accurate."""
    df = load_and_clean_data(sample_data)
    trends = compute_country_trends(df)
    
    # Kenya: Temp goes from 20 to 21 over 1 year (slope = 1.0)
    kenya_trend = trends[trends["country"] == "Kenya"].iloc[0]
    assert kenya_trend["temperature_trend_per_year"] == 1.0
    assert kenya_trend["rainfall_trend_per_year"] == 10.0
    
    # Nigeria: Temp is constant (slope = 0.0), Rain decreases (slope = -10.0)
    nigeria_trend = trends[trends["country"] == "Nigeria"].iloc[0]
    assert nigeria_trend["temperature_trend_per_year"] == 0.0
    assert nigeria_trend["rainfall_trend_per_year"] == -10.0

def test_empty_data_handling(tmp_path):
    """Tests behavior with empty inputs."""
    csv_path = tmp_path / "empty.csv"
    pd.DataFrame(columns=["country", "year", "temperature_c", "rainfall_mm"]).to_csv(csv_path, index=False)
    
    # load_and_clean_data might return an empty DF, ensure compute_trends doesn't crash
    df = load_and_clean_data(csv_path)
    trends = compute_country_trends(df)
    assert trends.empty