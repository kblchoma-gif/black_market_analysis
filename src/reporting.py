# Reporting module for generating analysis reports
import pandas as pd
import numpy as np
import os
from datetime import datetime
from typing import Dict
import logging

from config import Config
from utils.helpers import format_currency, save_json, Timer

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self):
        self.reports_dir = Config.REPORTS_DIR
        self.analysis_date = Config.ANALYSIS_DATE
        
    def generate_comprehensive_report(self, df: pd.DataFrame, anomaly_summary: Dict) -> Dict:
        """
        Generate comprehensive analysis report
        
        Args:
            df: Full analysis DataFrame
            anomaly_summary: Summary statistics from anomaly detection
            
        Returns:
            Dictionary containing complete report
        """
        with Timer("Generating comprehensive report"):
            report = {
                'metadata': self._generate_metadata(),
                'executive_summary': self._generate_executive_summary(df, anomaly_summary),
                'methodology': self._generate_methodology(),
                'detailed_findings': self._generate_detailed_findings(df, anomaly_summary),
                'recommendations': self._generate_recommendations(anomaly_summary),
                'raw_metrics': self._calculate_raw_metrics(df, anomaly_summary)
            }
            
            # Save report
            self._save_report(report, df)
            
            return report
    
    def _generate_metadata(self) -> Dict:
        """Generate report metadata"""
        return {
            'project_name': Config.PROJECT_NAME,
            'version': Config.VERSION,
            'analysis_date': self.analysis_date,
            'data_sources': ['UN Comtrade Database'],
            'analysis_period': f"{Config.DEFAULT_YEAR_RANGE[0]}-{Config.DEFAULT_YEAR_RANGE[1]}",
            'countries_analyzed': len(Config.COUNTRIES)
        }
    
    def _generate_executive_summary(self, df: pd.DataFrame, anomaly_summary: Dict) -> Dict:
        """Generate executive summary"""
        total_trade_volume = df['trade_volume'].sum()
        estimated_black_market = anomaly_summary.get('estimated_black_market_value', 0)
        anomaly_percentage = anomaly_summary.get('anomaly_percentage', 0)
        
        return {
            'total_trade_analyzed': format_currency(total_trade_volume),
            'estimated_black_market_activity': format_currency(estimated_black_market),
            'anomaly_detection_rate': f"{anomaly_percentage:.2f}%",
            'key_insights': [
                f"Detected {anomaly_summary.get('total_anomalies', 0):,} anomalous trade relationships",
                f"Estimated ${estimated_black_market:,.0f} in potential unreported trade",
                f"Top anomalous countries identified for further investigation",
                f"Certain product categories show higher susceptibility to discrepancies"
            ],
            'risk_assessment': self._assess_risk_level(anomaly_summary)
        }
    
    def _generate_methodology(self) -> Dict:
        """Generate methodology section"""
        return {
            'data_sources': [
                'UN Comtrade bilateral trade data',
                'Mirrored export-import declarations',
                'Standardized product classification (HS codes)'
            ],
            'anomaly_detection_methods': [
                'Z-score statistical analysis',
                'Median Absolute Deviation (MAD)',
                'Interquartile Range (IQR) method',
                'Multi-method consensus approach'
            ],
            'severity_scoring': [
                'Trade discrepancy magnitude (60% weight)',
                'Trade volume significance (30% weight)',
                'Detection confidence (10% weight)'
            ],
            'thresholds_used': {
                'zscore_threshold': Config.ZSCORE_THRESHOLD,
                'mad_threshold': Config.MAD_THRESHOLD,
                'minimum_trade_value': Config.MIN_TRADE_VALUE
            }
        }
    
    def _generate_detailed_findings(self, df: pd.DataFrame, anomaly_summary: Dict) -> Dict:
        """Generate detailed findings section"""
        anomaly_df = df[df['is_anomaly']]
        
        # Top country pairs by severity
        top_country_pairs = anomaly_df.groupby(['reporter', 'partner']).agg({
            'severity_score': 'sum',
            'absolute_discrepancy': 'sum',
            'trade_volume': 'sum'
        }).nlargest(10, 'severity_score').reset_index()
        
        # Most suspicious products
        suspicious_products = anomaly_df.groupby('product_category').agg({
            'severity_score': 'mean',
            'is_anomaly': 'count',
            'absolute_discrepancy': 'sum'
        }).nlargest(5, 'severity_score').reset_index()
        
        # Temporal trends
        yearly_trends = df.groupby('year').agg({
            'is_anomaly': 'mean',
            'severity_score': 'mean',
            'trade_volume': 'sum'
        }).reset_index()
        
        return {
            'top_anomalous_relationships': [
                {
                    'countries': f"{row['reporter']} - {row['partner']}",
                    'total_severity': round(row['severity_score'], 2),
                    'estimated_discrepancy': format_currency(row['absolute_discrepancy']),
                    'trade_volume': format_currency(row['trade_volume'])
                }
                for _, row in top_country_pairs.iterrows()
            ],
            'high_risk_products': [
                {
                    'product_category': row['product_category'],
                    'average_severity': round(row['severity_score'], 2),
                    'anomaly_count': int(row['is_anomaly']),
                    'total_discrepancy': format_currency(row['absolute_discrepancy'])
                }
                for _, row in suspicious_products.iterrows()
            ],
            'temporal_analysis': {
                'yearly_anomaly_rates': {
                    str(row['year']): f"{row['is_anomaly'] * 100:.2f}%"
                    for _, row in yearly_trends.iterrows()
                },
                'trend_analysis': self._analyze_trends(yearly_trends)
            }
        }
    
    def _generate_recommendations(self, anomaly_summary: Dict) -> Dict:
        """Generate recommendations based on findings"""
        total_anomalies = anomaly_summary.get('total_anomalies', 0)
        black_market_estimate = anomaly_summary.get('estimated_black_market_value', 0)
        
        recommendations = {
            'immediate_actions': [
                "Investigate top 10 most anomalous country pairs",
                "Conduct audit of high-risk product categories",
                "Verify customs declarations for identified anomalies"
            ],
            'medium_term_strategies': [
                "Implement automated trade discrepancy monitoring",
                "Enhance data sharing agreements between trading partners",
                "Develop risk-based customs inspection protocols"
            ],
            'long_term_improvements': [
                "Standardize trade reporting methodologies internationally",
                "Implement blockchain technology for trade verification",
                "Enhance international cooperation on trade data transparency"
            ]
        }
        
        # Add urgency based on findings
        if black_market_estimate > 1e9:  # Over $1B
            recommendations['urgency'] = "HIGH - Significant economic impact detected"
        elif black_market_estimate > 1e8:  # Over $100M
            recommendations['urgency'] = "MEDIUM - Substantial anomalies requiring attention"
        else:
            recommendations['urgency'] = "LOW - Monitor and investigate selectively"
        
        return recommendations
    
    def _calculate_raw_metrics(self, df: pd.DataFrame, anomaly_summary: Dict) -> Dict:
        """Calculate raw metrics for technical analysis"""
        anomaly_df = df[df['is_anomaly']]
        
        return {
            'dataset_statistics': {
                'total_records': len(df),
                'anomalous_records': len(anomaly_df),
                'data_completeness': f"{(1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100:.1f}%",
                'countries_covered': df['reporter'].nunique(),
                'products_analyzed': df['cmdCode'].nunique()
            },
            'statistical_metrics': {
                'mean_discrepancy_ratio': float(df['discrepancy_ratio'].mean()),
                'median_discrepancy_ratio': float(df['discrepancy_ratio'].median()),
                'std_discrepancy_ratio': float(df['discrepancy_ratio'].std()),
                'max_severity_score': float(df['severity_score'].max()),
                'mean_severity_anomalies': float(anomaly_df['severity_score'].mean())
            },
            'economic_impact': {
                'total_trade_volume_analyzed': float(df['trade_volume'].sum()),
                'anomaly_trade_volume': float(anomaly_df['trade_volume'].sum()),
                'potential_black_market_value': float(anomaly_df['absolute_discrepancy'].sum()),
                'percentage_of_trade_anomalous': f"{(anomaly_df['trade_volume'].sum() / df['trade_volume'].sum()) * 100:.2f}%"
            }
        }
    
    def _assess_risk_level(self, anomaly_summary: Dict) -> str:
        """Assess overall risk level based on findings"""
        black_market_estimate = anomaly_summary.get('estimated_black_market_value', 0)
        anomaly_rate = anomaly_summary.get('anomaly_percentage', 0)
        
        if black_market_estimate > 5e9 or anomaly_rate > 10:
            return "VERY HIGH RISK - Immediate investigation required"
        elif black_market_estimate > 1e9 or anomaly_rate > 5:
            return "HIGH RISK - Priority investigation needed"
        elif black_market_estimate > 1e8 or anomaly_rate > 2:
            return "MEDIUM RISK - Monitoring and analysis recommended"
        else:
            return "LOW RISK - Routine monitoring sufficient"
    
    def _analyze_trends(self, yearly_trends: pd.DataFrame) -> Dict:
        """Analyze temporal trends in anomalies"""
        if len(yearly_trends) < 2:
            return {"trend": "Insufficient data for trend analysis"}
        
        anomaly_trend = yearly_trends['is_anomaly'].values
        years = yearly_trends['year'].values
        
        # Simple trend calculation
        if len(anomaly_trend) > 1:
            trend_slope = (anomaly_trend[-1] - anomaly_trend[0]) / (years[-1] - years[0])
            trend_direction = "increasing" if trend_slope > 0 else "decreasing"
            
            return {
                "trend_direction": trend_direction,
                "trend_magnitude": f"{abs(trend_slope * 100):.3f}% per year",
                "latest_anomaly_rate": f"{anomaly_trend[-1] * 100:.2f}%"
            }
        
        return {"trend": "Stable", "latest_anomaly_rate": f"{anomaly_trend[0] * 100:.2f}%"}
    
    def _save_report(self, report: Dict, df: pd.DataFrame):
        """Save complete report to files"""
        # Save JSON report
        json_file = os.path.join(self.reports_dir, f'trade_anomaly_report_{self.analysis_date}.json')
        save_json(report, json_file)
        
        # Save Excel report with detailed data
        excel_file = os.path.join(self.reports_dir, f'detailed_analysis_{self.analysis_date}.xlsx')
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = []
            for section, content in report.items():
                if section != 'raw_metrics':
                    summary_data.append({'Section': section, 'Content': str(content)[:500] + '...'})
            
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Report_Summary', index=False)
            
            # Anomalies sheet
            anomalies_df = df[df['is_anomaly']].sort_values('severity_score', ascending=False)
            anomalies_df.to_excel(writer, sheet_name='Detailed_Anomalies', index=False)
            
            # Aggregated statistics
            country_stats = df.groupby('reporter').agg({
                'severity_score': 'sum',
                'is_anomaly': 'sum',
                'trade_volume': 'sum',
                'absolute_discrepancy': 'sum'
            }).reset_index()
            country_stats.to_excel(writer, sheet_name='Country_Statistics', index=False)
            
            # Product statistics
            product_stats = df.groupby('product_category').agg({
                'severity_score': 'mean',
                'is_anomaly': 'sum',
                'trade_volume': 'sum'
            }).reset_index()
            product_stats.to_excel(writer, sheet_name='Product_Statistics', index=False)
        
        logger.info(f"Comprehensive report saved to {json_file}")
        logger.info(f"Detailed data exported to {excel_file}")
        
        # Print executive summary
        self._print_executive_summary(report['executive_summary'])
    
    def _print_executive_summary(self, executive_summary: Dict):
        """Print executive summary to console"""
        print("\n" + "="*80)
        print("📊 EXECUTIVE SUMMARY - Global Black Market Economy Estimation")
        print("="*80)
        
        for key, value in executive_summary.items():
            if key == 'key_insights':
                print(f"\n🔍 Key Insights:")
                for insight in value:
                    print(f"   • {insight}")
            elif key == 'risk_assessment':
                print(f"\n⚠️  Risk Assessment: {value}")
            else:
                print(f"📈 {key.replace('_', ' ').title()}: {value}")
        
        print("="*80)