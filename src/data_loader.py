import pandas as pd
import numpy as np
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Project root is one level up from src/
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

def load_csv_with_null_handling(filepath):
    r"""Load CSV with \N handled as NULL"""
    return pd.read_csv(filepath, na_values=['\\N', 'N/A', ''])

def load_races():
    """Load and parse races.csv"""
    df = load_csv_with_null_handling(os.path.join(DATA_DIR, 'races.csv'))
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['year'].astype(int)
    return df

def load_results():
    """Load and parse results.csv"""
    df = load_csv_with_null_handling(os.path.join(DATA_DIR, 'results.csv'))
    df['position'] = pd.to_numeric(df['position'], errors='coerce')
    df['milliseconds'] = pd.to_numeric(df['milliseconds'], errors='coerce')
    return df

def load_drivers():
    """Load and parse drivers.csv"""
    df = load_csv_with_null_handling(os.path.join(DATA_DIR, 'drivers.csv'))
    df['dob'] = pd.to_datetime(df['dob'])
    return df

def load_constructors():
    """Load and parse constructors.csv"""
    return load_csv_with_null_handling(os.path.join(DATA_DIR, 'constructors.csv'))

def load_qualifying():
    """Load and parse qualifying.csv"""
    df = load_csv_with_null_handling(os.path.join(DATA_DIR, 'qualifying.csv'))
    df['position'] = pd.to_numeric(df['position'], errors='coerce')
    return df

def load_driver_standings():
    """Load and parse driver_standings.csv"""
    df = load_csv_with_null_handling(os.path.join(DATA_DIR, 'driver_standings.csv'))
    df['position'] = pd.to_numeric(df['position'], errors='coerce')
    df['points'] = pd.to_numeric(df['points'], errors='coerce')
    return df

def load_constructor_standings():
    """Load and parse constructor_standings.csv"""
    df = load_csv_with_null_handling(os.path.join(DATA_DIR, 'constructor_standings.csv'))
    df['position'] = pd.to_numeric(df['position'], errors='coerce')
    df['points'] = pd.to_numeric(df['points'], errors='coerce')
    return df

def load_weather():
    """Load and parse weather.csv"""
    return load_csv_with_null_handling(os.path.join(DATA_DIR, 'weather.csv'))

def load_circuits():
    """Load and parse circuits.csv"""
    return load_csv_with_null_handling(os.path.join(DATA_DIR, 'circuits.csv'))