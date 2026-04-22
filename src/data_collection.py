# Data collection module for UN Comtrade API
import requests
import pandas as pd
import numpy as np
import os
import time
from typing import List, Dict, Optional
import logging

from config import Config
from utils.helpers import save_json, Timer

logger = logging.getLogger(__name__)

class ComtradeDataCollector:
    def __init__(self):
        self.base_url = Config.UN_COMTRADE_BASE_URL
        self.data_dir = Config.RAW_DATA_DIR
        self.countries = Config.COUNTRIES
        
    def get_trade_data(self, reporter_code: int, partner_code: str = "world", 
                      year: int = 2022, trade_flow: str = "all") -> Optional[Dict]:
        """
        Fetch bilateral trade data from UN Comtrade API
        
        Args:
            reporter_code: Reporter country code
            partner_code: Partner country code or "world"
            year: Year of data
            trade_flow: Type of trade flow ("export", "import", "all")
        
        Returns:
            Dictionary containing trade data or None if failed
        """
        url = f"{self.base_url}C/A/{Config.ANALYSIS_DATE[:4]}/{trade_flow}/{year}/ALL/{reporter_code}"
        
        params = {}
        if partner_code != "world":
            params['partnerCode'] = partner_code
        
        try:
            with Timer(f"Fetching data for reporter {reporter_code}, partner {partner_code}"):
                response = requests.get(url, params=params, timeout=Config.TIMEOUT)
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get('data', [])
                else:
                    logger.warning(f"API returned status {response.status_code} for {reporter_code}")
                    return None
                    
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {reporter_code}: {e}")
            return None
    
    def collect_country_data(self, years: List[int] = None) -> pd.DataFrame:
        """
        Collect trade data for all configured countries and years
        
        Args:
            years: List of years to collect data for
            
        Returns:
            DataFrame containing collected trade data
        """
        if years is None:
            years = list(range(Config.DEFAULT_YEAR_RANGE[0], Config.DEFAULT_YEAR_RANGE[1] + 1))
        
        all_data = []
        
        for year in years:
            for reporter_code in self.countries.values():
                # Get data for all partners
                data = self.get_trade_data(reporter_code, "world", year)
                
                if data:
                    # Add year information
                    for record in data:
                        record['year'] = year
                    all_data.extend(data)
                    
                # Respect API rate limits
                time.sleep(0.5)
            
            logger.info(f"Collected data for year {year}: {len(all_data)} records so far")
        
        return pd.DataFrame(all_data)
    
    def generate_sample_data(self) -> pd.DataFrame:
        """
        Generate sample trade data for demonstration purposes
        In production, this would be replaced with actual API calls
        """
        logger.info("Generating sample trade data for demonstration")
        
        np.random.seed(42)
        countries = list(self.countries.keys())
        products = list(Config.PRODUCT_CATEGORIES.keys())[:8]  # Use first 8 products
        
        data = []
        for year in range(Config.DEFAULT_YEAR_RANGE[0], Config.DEFAULT_YEAR_RANGE[1] + 1):
            for reporter in countries:
                for partner in countries:
                    if reporter != partner and np.random.random() > 0.7:  # 30% density
                        for product in products:
                            # Simulate realistic trade flows
                            base_value = np.random.lognormal(12, 1.5)
                            export_value = max(base_value, Config.MIN_TRADE_VALUE)
                            
                            # Create import value with some natural variation
                            variation = np.random.normal(1.0, 0.2)
                            import_value = max(export_value * variation, Config.MIN_TRADE_VALUE)
                            
                            # Introduce anomalies (5% of records)
                            if np.random.random() < 0.05:
                                anomaly_factor = np.random.uniform(1.8, 4.0)
                                if np.random.random() < 0.5:
                                    export_value *= anomaly_factor
                                else:
                                    import_value *= anomaly_factor
                            
                            data.append({
                                'year': year,
                                'reporterCode': self.countries[reporter],
                                'partnerCode': self.countries[partner],
                                'reporter': reporter,
                                'partner': partner,
                                'cmdCode': product,
                                'primaryValue': export_value,
                                'import_value': import_value,  # Simulated mirror data
                                'tradeFlow': 'Export',
                                'refYear': year
                            })
        
        df = pd.DataFrame(data)
        logger.info(f"Generated sample data with {len(df)} records")
        
        # Save sample data
        sample_file = os.path.join(self.data_dir, 'sample_trade_data.csv')
        df.to_csv(sample_file, index=False)
        logger.info(f"Sample data saved to {sample_file}")
        
        return df
    
    def save_data(self, df: pd.DataFrame, filename: str) -> str:
        """
        Save trade data to file
        
        Args:
            df: DataFrame to save
            filename: Output filename
            
        Returns:
            Path to saved file
        """
        filepath = os.path.join(self.data_dir, filename)
        
        if filename.endswith('.csv'):
            df.to_csv(filepath, index=False)
        elif filename.endswith('.json'):
            save_json(df.to_dict('records'), filepath)
        else:
            df.to_parquet(filepath, index=False)
            
        logger.info(f"Data saved to {filepath}")
        return filepath