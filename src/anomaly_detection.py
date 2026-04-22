# Anomaly detection module for trade discrepancies
import pandas as pd
import numpy as np
from scipy import stats
import logging
from typing import Tuple, Dict

from config import Config
from utils.helpers import Timer

logger = logging.getLogger(__name__)

class AnomalyDetector:
    def __init__(self):
        self.zscore_threshold = Config.ZSCORE_THRESHOLD
        self.mad_threshold = Config.MAD_THRESHOLD
        
    def detect_trade_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect anomalies in trade data using multiple methods
        
        Args:
            df: Preprocessed trade data
            
        Returns:
            DataFrame with anomaly flags and scores
        """
        with Timer("Anomaly detection"):
            df_anomalies = df.copy()
            
            # Apply multiple anomaly detection methods
            df_anomalies = self._zscore_detection(df_anomalies)
            df_anomalies = self._mad_detection(df_anomalies)
            df_anomalies = self._iqr_detection(df_anomalies)
            
            # Combine detection methods
            df_anomalies = self._combine_anomaly_scores(df_anomalies)
            
            # Calculate severity scores
            df_anomalies = self._calculate_severity_scores(df_anomalies)
            
            # Classify anomaly types
            df_anomalies = self._classify_anomaly_types(df_anomalies)
            
            anomaly_count = df_anomalies['is_anomaly'].sum()
            logger.info(f"Detected {anomaly_count} anomalies ({anomaly_count/len(df_anomalies)*100:.1f}%)")
            
            return df_anomalies
    
    def _zscore_detection(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect anomalies using Z-score method"""
        df = df.copy()
        
        # Z-score for discrepancy ratio
        zscore = np.abs(stats.zscore(df['discrepancy_ratio'], nan_policy='omit'))
        df['zscore_anomaly'] = zscore > self.zscore_threshold
        
        # Z-score for absolute discrepancy
        zscore_abs = np.abs(stats.zscore(np.log1p(df['absolute_discrepancy']), nan_policy='omit'))
        df['zscore_abs_anomaly'] = zscore_abs > self.zscore_threshold
        
        return df
    
    def _mad_detection(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect anomalies using Median Absolute Deviation"""
        df = df.copy()
        
        # MAD for discrepancy ratio
        median = df['discrepancy_ratio'].median()
        mad = stats.median_abs_deviation(df['discrepancy_ratio'], nan_policy='omit')
        
        if mad > 0:
            modified_zscore = 0.6745 * (df['discrepancy_ratio'] - median) / mad
            df['mad_anomaly'] = np.abs(modified_zscore) > self.mad_threshold
        else:
            df['mad_anomaly'] = False
        
        return df
    
    def _iqr_detection(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect anomalies using Interquartile Range method"""
        df = df.copy()
        
        Q1 = df['discrepancy_ratio'].quantile(0.25)
        Q3 = df['discrepancy_ratio'].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        df['iqr_anomaly'] = (df['discrepancy_ratio'] < lower_bound) | (df['discrepancy_ratio'] > upper_bound)
        
        return df
    
    def _combine_anomaly_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Combine multiple anomaly detection methods"""
        df = df.copy()
        
        # Combined anomaly flag (any method detects anomaly)
        df['is_anomaly'] = (
            df['zscore_anomaly'] | 
            df['mad_anomaly'] | 
            df['iqr_anomaly']
        )
        
        # Confidence score based on number of methods that detected anomaly
        method_count = df[['zscore_anomaly', 'mad_anomaly', 'iqr_anomaly']].sum(axis=1)
        df['detection_confidence'] = method_count / 3
        
        return df
    
    def _calculate_severity_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate severity scores for anomalies"""
        df = df.copy()
        
        # Normalize discrepancy magnitude (0-1 scale)
        discrepancy_norm = df['discrepancy_magnitude'] / df['discrepancy_magnitude'].max()
        
        # Normalize trade volume (log scale)
        volume_norm = df['log_trade_volume'] / df['log_trade_volume'].max()
        
        # Combined severity score (weighted)
        df['severity_score'] = (
            discrepancy_norm * 0.6 + 
            volume_norm * 0.3 +
            df['detection_confidence'] * 0.1
        ) * 100
        
        # Adjust for non-anomalies
        df.loc[~df['is_anomaly'], 'severity_score'] = 0
        
        return df
    
    def _classify_anomaly_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Classify types of trade anomalies"""
        df = df.copy()
        
        df['anomaly_type'] = 'Normal'
        
        # Only classify actual anomalies
        anomaly_mask = df['is_anomaly']
        
        # Classify based on discrepancy direction and magnitude
        df.loc[anomaly_mask, 'anomaly_type'] = np.where(
            df.loc[anomaly_mask, 'discrepancy_ratio'] > 1,
            'Over-reported Exports',
            'Over-reported Imports'
        )
        
        # Further classification by severity
        severe_mask = anomaly_mask & (df['severity_score'] > 70)
        df.loc[severe_mask, 'anomaly_type'] = 'Severe ' + df.loc[severe_mask, 'anomaly_type']
        
        return df
    
    def get_anomaly_summary(self, df: pd.DataFrame) -> Dict:
        """Generate summary statistics for anomalies"""
        anomaly_df = df[df['is_anomaly']]
        
        if len(anomaly_df) == 0:
            return {}
        
        summary = {
            'total_anomalies': len(anomaly_df),
            'anomaly_percentage': (len(anomaly_df) / len(df)) * 100,
            'total_trade_volume_anomalies': anomaly_df['trade_volume'].sum(),
            'estimated_black_market_value': anomaly_df['absolute_discrepancy'].sum(),
            'anomaly_types': anomaly_df['anomaly_type'].value_counts().to_dict(),
            'top_anomalous_countries': anomaly_df.groupby('reporter')['severity_score'].sum().nlargest(5).to_dict(),
            'most_suspicious_products': anomaly_df.groupby('product_category')['severity_score'].mean().nlargest(5).to_dict()
        }
        
        return summary