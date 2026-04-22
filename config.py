# Configuration settings for the project
import os
from datetime import datetime

class Config:
    # Project settings
    PROJECT_NAME = "Global Black Market Economy Estimation"
    VERSION = "1.0.0"
    ANALYSIS_DATE = datetime.now().strftime('%Y-%m-%d')
    
    # API Settings
    UN_COMTRADE_BASE_URL = "https://comtradeapi.un.org/data/v1/get/"
    MAX_RETRIES = 3
    TIMEOUT = 30
    
    # Data directories
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
    PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
    OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')
    REPORTS_DIR = os.path.join(OUTPUT_DIR, 'reports')
    CHARTS_DIR = os.path.join(OUTPUT_DIR, 'charts')
    
    # Analysis parameters
    DEFAULT_YEAR_RANGE = (2018, 2023)
    ZSCORE_THRESHOLD = 2.5
    MAD_THRESHOLD = 3.0
    MIN_TRADE_VALUE = 1000  # Minimum trade value to consider
    
    # Country codes for analysis
    COUNTRIES = {
        'USA': 842, 'CHN': 156, 'DEU': 276, 'FRA': 250, 'GBR': 826,
        'IND': 356, 'JPN': 392, 'CAN': 124, 'MEX': 484, 'BRA': 76,
        'RUS': 643, 'ITA': 380, 'KOR': 410, 'AUS': 36, 'ZAF': 710,
        'NLD': 528, 'ESP': 724, 'CHE': 756, 'SWE': 752, 'NOR': 578
    }
    
    # Product categories mapping
    PRODUCT_CATEGORIES = {
        '01': 'Animal Products', '02': 'Vegetable Products',
        '03': 'Fats & Oils', '04': 'Food Products',
        '05': 'Mineral Products', '06': 'Chemical Products',
        '07': 'Plastics/Rubbers', '08': 'Animal Hides',
        '09': 'Wood Products', '10': 'Paper Products',
        '11': 'Textiles', '12': 'Footwear/Headgear',
        '13': 'Stone/Glass', '14': 'Precious Stones',
        '15': 'Metals', '16': 'Machinery/Electrical'
    }
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories"""
        directories = [
            cls.RAW_DATA_DIR, cls.PROCESSED_DATA_DIR,
            cls.REPORTS_DIR, cls.CHARTS_DIR
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

# Initialize directories
Config.create_directories()