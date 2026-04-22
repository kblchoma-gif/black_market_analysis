# Utility functions and helpers
import pandas as pd
import numpy as np
import logging
from datetime import datetime
import json

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('trade_analysis.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def save_json(data, filepath):
    """Save data to JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def load_json(filepath):
    """Load data from JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def format_currency(value):
    """Format value as currency"""
    if abs(value) >= 1e9:
        return f"${value/1e9:.2f}B"
    elif abs(value) >= 1e6:
        return f"${value/1e6:.2f}M"
    elif abs(value) >= 1e3:
        return f"${value/1e3:.2f}K"
    else:
        return f"${value:.2f}"

def calculate_percentage_change(old_val, new_val):
    """Calculate percentage change"""
    if old_val == 0:
        return float('inf')
    return ((new_val - old_val) / old_val) * 100

class Timer:
    """Simple timer context manager"""
    def __init__(self, operation_name=""):
        self.operation_name = operation_name
    
    def __enter__(self):
        self.start = datetime.now()
        print(f"🕒 Starting {self.operation_name}...")
        return self
    
    def __exit__(self, *args):
        self.end = datetime.now()
        self.duration = self.end - self.start
        print(f"✅ {self.operation_name} completed in {self.duration.total_seconds():.2f} seconds")