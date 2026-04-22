# Data preprocessing and cleaning module
import pandas as pd
import numpy as np
import logging
from typing import Tuple, Dict

from config import Config
from utils.helpers import Timer

logger = logging.getLogger(__name__)

class TradeDataPreprocessor:
    def __init__(self):
        self.product_categories = Config.PRODUCT_CATEGORIES
        self.min_trade_value = Config.MIN_TRADE_VALUE
        
    def load_and_clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Load and clean trade data
        
        Args:
            df: Raw trade data DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        with Timer("Data cleaning and preprocessing"):
            df_clean = df.copy()
            
            # Basic cleaning
            initial_count = len(df_clean)
            
            # Remove duplicates
            df_clean = df_clean.drop_duplicates()
            
            # Handle missing values
            df_clean = df_clean.dropna(subset=['primaryValue', 'import_value'])
            
            # Filter by minimum trade value
            df_clean = df_clean[
                (df_clean['primaryValue'] >= self.min_trade_value) & 
                (df_clean['import_value'] >= self.min_trade_value)
            ]
            
            # Add product category information
            df_clean['product_category'] = df_clean['cmdCode'].map(self.product_categories)
            df_clean['product_category'] = df_clean['product_category'].fillna('Other')
            
            # Calculate key metrics
            df_clean = self._calculate_trade_metrics(df_clean)
            
            # Log cleaning results
            final_count = len(df_clean)
            logger.info(f"Data cleaning: {initial_count} -> {final_count} records "
                       f"({((initial_count - final_count) / initial_count * 100):.1f}% removed)")
            
            return df_clean
    
    def _calculate_trade_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate trade discrepancy metrics
        
        Args:
            df: Cleaned trade data
            
        Returns:
            DataFrame with calculated metrics
        """
        df = df.copy()
        
        # Basic trade metrics
        df['trade_imbalance'] = df['primaryValue'] - df['import_value']
        df['discrepancy_ratio'] = df['primaryValue'] / df['import_value']
        
        # Absolute discrepancy
        df['absolute_discrepancy'] = np.abs(df['trade_imbalance'])
        
        # Log-based metrics for better distribution
        df['log_discrepancy'] = np.log1p(np.abs(df['discrepancy_ratio'] - 1))
        
        # Trade volume (average of export and import)
        df['trade_volume'] = (df['primaryValue'] + df['import_value']) / 2
        
        # Flag for large discrepancies
        df['large_discrepancy'] = (
            (df['discrepancy_ratio'] > 2.0) | 
            (df['discrepancy_ratio'] < 0.5)
        )
        
        return df
    
    def create_trade_pairs(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create mirrored trade pairs for analysis
        
        Args:
            df: Cleaned trade data
            
        Returns:
            DataFrame with trade pairs
        """
        with Timer("Creating trade pairs"):
            # Ensure we have consistent column names
            required_cols = ['year', 'reporter', 'partner', 'cmdCode', 
                           'primaryValue', 'import_value', 'product_category']
            
            if not all(col in df.columns for col in required_cols):
                raise ValueError(f"Missing required columns. Expected: {required_cols}")
            
            # Create trade pair identifier
            df['trade_pair'] = df['reporter'] + '_' + df['partner']
            df['product_pair'] = df['trade_pair'] + '_' + df['cmdCode']
            
            return df
    
    def aggregate_by_dimensions(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Aggregate data by different dimensions for analysis
        
        Args:
            df: Processed trade data
            
        Returns:
            Dictionary of aggregated DataFrames
        """
        aggregations = {}
        
        # By country pair and year
        aggregations['country_year'] = df.groupby(['reporter', 'partner', 'year']).agg({
            'primaryValue': 'sum',
            'import_value': 'sum',
            'discrepancy_ratio': 'mean',
            'absolute_discrepancy': 'sum',
            'trade_volume': 'sum'
        }).reset_index()
        
        # By product category and year
        aggregations['product_year'] = df.groupby(['product_category', 'year']).agg({
            'primaryValue': 'sum',
            'import_value': 'sum',
            'discrepancy_ratio': 'mean',
            'absolute_discrepancy': 'sum',
            'large_discrepancy': 'sum'
        }).reset_index()
        
        # By country and product
        aggregations['country_product'] = df.groupby(['reporter', 'product_category']).agg({
            'primaryValue': 'sum',
            'import_value': 'sum',
            'discrepancy_ratio': 'mean',
            'absolute_discrepancy': 'sum'
        }).reset_index()
        
        logger.info("Created aggregated datasets for analysis")
        return aggregations
    
    def prepare_analysis_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare final dataset for anomaly detection
        
        Args:
            df: Cleaned trade data
            
        Returns:
            Analysis-ready DataFrame
        """
        with Timer("Preparing analysis dataset"):
            # Apply all preprocessing steps
            df_clean = self.load_and_clean_data(df)
            df_pairs = self.create_trade_pairs(df_clean)
            
            # Add additional features
            df_pairs['log_trade_volume'] = np.log1p(df_pairs['trade_volume'])
            df_pairs['discrepancy_magnitude'] = np.abs(np.log(df_pairs['discrepancy_ratio']))
            
            return df_pairs