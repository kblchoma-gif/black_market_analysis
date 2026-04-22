# Visualization module for trade anomaly analysis
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
from typing import Dict, List

from config import Config
from utils.helpers import Timer

plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class TradeVisualizer:
    def __init__(self):
        self.fig_size = (12, 8)
        self.charts_dir = Config.CHARTS_DIR
        
    def create_comprehensive_visualizations(self, df: pd.DataFrame, anomaly_summary: Dict):
        """Create all visualizations for the analysis"""
        with Timer("Creating comprehensive visualizations"):
            self.create_discrepancy_heatmap(df)
            self.create_product_analysis(df)  # New dedicated product analysis
            self.create_anomaly_timeseries(df)
            self.create_anomaly_distribution(df)
            self.create_severity_analysis(df)
            self.create_summary_dashboard(df, anomaly_summary)
    
    def create_discrepancy_heatmap(self, df: pd.DataFrame):
        """Create heatmap of trade discrepancies"""
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 8))
        
        # 1. Country-country discrepancy matrix
        country_matrix = df.pivot_table(
            index='reporter', columns='partner', 
            values='discrepancy_ratio', aggfunc='mean'
        )
        
        sns.heatmap(country_matrix, ax=ax1, cmap='RdBu_r', center=1.0,
                   cbar_kws={'label': 'Export/Import Ratio'})
        ax1.set_title('Trade Discrepancy Matrix\n(Country Pairs)', fontsize=12, fontweight='bold')
        ax1.tick_params(axis='x', rotation=45)
        ax1.tick_params(axis='y', rotation=0)
        
        # 2. Product category heatmap
        product_matrix = df.pivot_table(
            index='reporter', columns='product_category', 
            values='discrepancy_ratio', aggfunc='mean'
        )
        
        sns.heatmap(product_matrix, ax=ax2, cmap='RdBu_r', center=1.0,
                   cbar_kws={'label': 'Export/Import Ratio'})
        ax2.set_title('Trade Discrepancies by Product Category', fontsize=12, fontweight='bold')
        ax2.tick_params(axis='x', rotation=45, labelsize=9)
        ax2.tick_params(axis='y', rotation=0, labelsize=9)
        
        # 3. Anomaly severity by country
        severity_by_country = df.groupby('reporter').agg({
            'severity_score': 'sum',
            'is_anomaly': 'sum'
        }).nlargest(15, 'severity_score')
        
        severity_by_country['severity_score'].plot(kind='bar', ax=ax3, color='coral', alpha=0.8)
        ax3.set_title('Top 15 Countries by Anomaly Severity Score', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Total Severity Score')
        ax3.tick_params(axis='x', rotation=45)
        ax3.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for i, (country, score) in enumerate(severity_by_country['severity_score'].items()):
            ax3.text(i, score + 5, f'{score:.0f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.charts_dir, 'trade_discrepancy_analysis.png'), 
                   dpi=300, bbox_inches='tight')
        plt.show()

    def create_product_analysis(self, df: pd.DataFrame):
        """Create dedicated product category analysis with better layout"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
        
        # 1. Anomaly prevalence by product (horizontal)
        anomaly_by_product = df.groupby('product_category').agg({
            'is_anomaly': 'mean',
            'severity_score': 'mean',
            'trade_volume': 'sum'
        }).sort_values('is_anomaly', ascending=True)
        
        y_pos = range(len(anomaly_by_product))
        colors = plt.cm.Blues(np.linspace(0.4, 0.8, len(anomaly_by_product)))
        
        bars = ax1.barh(y_pos, anomaly_by_product['is_anomaly'], color=colors, alpha=0.8)
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(anomaly_by_product.index, fontsize=11)
        ax1.set_xlabel('Proportion of Anomalous Records', fontsize=12)
        ax1.set_title('Anomaly Prevalence by Product Category', fontsize=14, fontweight='bold')
        
        # Add value annotations
        for i, (idx, row) in enumerate(anomaly_by_product.iterrows()):
            ax1.text(row['is_anomaly'] + 0.005, i, f'{row["is_anomaly"]:.3f}', 
                    ha='left', va='center', fontsize=10, fontweight='bold')
        
        ax1.grid(True, alpha=0.3, axis='x')
        
        # 2. Severity by product category
        severity_by_product = df.groupby('product_category').agg({
            'severity_score': 'mean',
            'is_anomaly': 'sum'
        }).sort_values('severity_score', ascending=True)
        
        y_pos2 = range(len(severity_by_product))
        colors2 = plt.cm.Reds(np.linspace(0.4, 0.8, len(severity_by_product)))
        
        bars2 = ax2.barh(y_pos2, severity_by_product['severity_score'], color=colors2, alpha=0.8)
        ax2.set_yticks(y_pos2)
        ax2.set_yticklabels(severity_by_product.index, fontsize=11)
        ax2.set_xlabel('Average Severity Score', fontsize=12)
        ax2.set_title('Average Anomaly Severity by Product Category', fontsize=14, fontweight='bold')
        
        # Add value annotations
        for i, (idx, row) in enumerate(severity_by_product.iterrows()):
            ax2.text(row['severity_score'] + 0.5, i, f'{row["severity_score"]:.1f}', 
                    ha='left', va='center', fontsize=10, fontweight='bold')
            # Add count of anomalies
            ax2.text(1, i, f'({row["is_anomaly"]} anomalies)', 
                    ha='left', va='center', fontsize=9, color='gray')
        
        ax2.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.charts_dir, 'product_category_analysis.png'), 
                   dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_anomaly_timeseries(self, df: pd.DataFrame):
        """Create time series analysis of anomalies"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Overall anomaly trends
        yearly_trends = df.groupby('year').agg({
            'is_anomaly': 'mean',
            'severity_score': 'mean',
            'trade_volume': 'sum'
        }).reset_index()
        
        ax1.plot(yearly_trends['year'], yearly_trends['is_anomaly'] * 100, 
                marker='o', linewidth=2, label='Anomaly Rate')
        ax1.set_title('Annual Anomaly Detection Rate', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Anomaly Rate (%)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # 2. Severity trends
        ax2.plot(yearly_trends['year'], yearly_trends['severity_score'], 
                marker='s', linewidth=2, color='red', label='Average Severity')
        ax2.set_title('Average Anomaly Severity Over Time', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Severity Score')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # 3. Top countries time series
        top_countries = df.groupby('reporter')['severity_score'].sum().nlargest(5).index
        for country in top_countries:
            country_data = df[df['reporter'] == country].groupby('year')['severity_score'].sum()
            ax3.plot(country_data.index, country_data.values, marker='^', linewidth=2, label=country)
        
        ax3.set_title('Severity Trends for Top Anomalous Countries', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Total Severity Score')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Discrepancy ratio distribution over time
        sns.boxplot(data=df, x='year', y='discrepancy_ratio', ax=ax4)
        ax4.axhline(y=1.0, color='red', linestyle='--', alpha=0.7)
        ax4.set_title('Distribution of Trade Discrepancies Over Time', fontsize=12, fontweight='bold')
        ax4.set_ylabel('Export/Import Ratio')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.charts_dir, 'anomaly_timeseries_analysis.png'), 
                   dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_anomaly_distribution(self, df: pd.DataFrame):
        """Create distribution analysis of anomalies"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Discrepancy ratio distribution
        sns.histplot(data=df, x='discrepancy_ratio', hue='is_anomaly', 
                    ax=ax1, bins=50, alpha=0.7)
        ax1.set_xlim(0, 5)
        ax1.set_xlabel('Export/Import Ratio')
        ax1.set_title('Distribution of Trade Discrepancies', fontsize=12, fontweight='bold')
        ax1.axvline(x=1.0, color='red', linestyle='--', alpha=0.7)
        
        # 2. Anomaly types breakdown
        anomaly_data = df[df['is_anomaly']]
        if not anomaly_data.empty:
            anomaly_types = anomaly_data['anomaly_type'].value_counts()
            ax2.pie(anomaly_types.values, labels=anomaly_types.index, autopct='%1.1f%%', 
                   startangle=90, textprops={'fontsize': 10})
            ax2.set_title('Distribution of Anomaly Types', fontsize=12, fontweight='bold')
        
        # 3. Severity vs trade volume
        sns.scatterplot(data=df[df['is_anomaly']], x='log_trade_volume', 
                       y='severity_score', hue='anomaly_type', ax=ax3, s=60, alpha=0.7)
        ax3.set_title('Anomaly Severity vs Trade Volume', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Log Trade Volume')
        ax3.set_ylabel('Severity Score')
        ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 4. Product category analysis - Updated with horizontal bars
        if not anomaly_data.empty:
            product_analysis = anomaly_data.groupby('product_category').agg({
                'severity_score': 'mean',
                'is_anomaly': 'count'
            }).nlargest(10, 'is_anomaly').sort_values('is_anomaly', ascending=True)
            
            y_pos = range(len(product_analysis))
            colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(product_analysis)))
            
            bars = ax4.barh(y_pos, product_analysis['is_anomaly'], color=colors, alpha=0.8)
            ax4.set_yticks(y_pos)
            ax4.set_yticklabels(product_analysis.index, fontsize=10)
            ax4.set_xlabel('Number of Anomalies')
            ax4.set_title('Top 10 Product Categories by Anomaly Count', fontsize=12, fontweight='bold')
            
            # Add value labels
            for i, (idx, row) in enumerate(product_analysis.iterrows()):
                ax4.text(row['is_anomaly'] + 0.5, i, f'{int(row["is_anomaly"])}', 
                        ha='left', va='center', fontsize=9, fontweight='bold')
            
            ax4.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.charts_dir, 'anomaly_distribution_analysis.png'), 
                   dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_severity_analysis(self, df: pd.DataFrame):
        """Create severity-focused visualizations"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # 1. Severity score distribution
        sns.histplot(data=df[df['is_anomaly']], x='severity_score', 
                    ax=ax1, bins=20, kde=True, color='skyblue')
        ax1.set_xlabel('Severity Score')
        ax1.set_ylabel('Count')
        ax1.set_title('Distribution of Anomaly Severity Scores', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # 2. Top anomalous trade relationships
        top_relationships = df[df['is_anomaly']].groupby(['reporter', 'partner']).agg({
            'severity_score': 'sum',
            'absolute_discrepancy': 'sum'
        }).nlargest(10, 'severity_score').reset_index()
        
        if not top_relationships.empty:
            # Sort for better visualization
            top_relationships = top_relationships.sort_values('severity_score', ascending=True)
            
            y_pos = range(len(top_relationships))
            colors = plt.cm.plasma(np.linspace(0.2, 0.8, len(top_relationships)))
            
            bars = ax2.barh(y_pos, top_relationships['severity_score'], color=colors, alpha=0.8)
            ax2.set_yticks(y_pos)
            ax2.set_yticklabels([f"{row['reporter']}-{row['partner']}" 
                               for _, row in top_relationships.iterrows()], fontsize=10)
            ax2.set_xlabel('Total Severity Score')
            ax2.set_title('Top 10 Most Anomalous Trade Relationships', fontsize=12, fontweight='bold')
            
            # Add value labels
            for i, (_, row) in enumerate(top_relationships.iterrows()):
                ax2.text(row['severity_score'] + 1, i, f'{row["severity_score"]:.0f}', 
                        ha='left', va='center', fontsize=9, fontweight='bold')
            
            ax2.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.charts_dir, 'severity_analysis.png'), 
                   dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_summary_dashboard(self, df: pd.DataFrame, anomaly_summary: Dict):
        """Create a summary dashboard with key metrics"""
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        axes = axes.flatten()
        
        # Key metrics
        total_trade = df['trade_volume'].sum()
        total_anomalies = anomaly_summary.get('total_anomalies', 0)
        black_market_estimate = anomaly_summary.get('estimated_black_market_value', 0)
        anomaly_percentage = anomaly_summary.get('anomaly_percentage', 0)
        
        # 1. Summary metrics
        metrics_text = f"""
        Project Summary
        
        Total Trade Records: {len(df):,}
        Anomalous Records: {total_anomalies:,}
        Anomaly Rate: {anomaly_percentage:.1f}%
        
        Total Trade Volume: ${total_trade:,.0f}
        Estimated Black Market: ${black_market_estimate:,.0f}
        """
        
        axes[0].text(0.1, 0.9, metrics_text, transform=axes[0].transAxes, 
                    fontsize=12, verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.5))
        axes[0].set_title('Key Project Metrics', fontsize=14, fontweight='bold')
        axes[0].axis('off')
        
        # 2. Anomaly types
        if 'anomaly_types' in anomaly_summary:
            anomaly_types = anomaly_summary['anomaly_types']
            wedges, texts, autotexts = axes[1].pie(anomaly_types.values(), 
                                                  labels=anomaly_types.keys(), 
                                                  autopct='%1.1f%%',
                                                  startangle=90)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            axes[1].set_title('Anomaly Type Distribution', fontsize=12, fontweight='bold')
        
        # 3. Top countries - Horizontal bars
        if 'top_anomalous_countries' in anomaly_summary:
            top_countries = anomaly_summary['top_anomalous_countries']
            countries = list(top_countries.keys())[:5]
            scores = list(top_countries.values())[:5]
            
            # Sort for better visualization
            sorted_indices = np.argsort(scores)
            countries = [countries[i] for i in sorted_indices]
            scores = [scores[i] for i in sorted_indices]
            
            y_pos = range(len(countries))
            axes[2].barh(y_pos, scores, color='lightcoral', alpha=0.8)
            axes[2].set_yticks(y_pos)
            axes[2].set_yticklabels(countries, fontsize=10)
            axes[2].set_xlabel('Total Severity Score')
            axes[2].set_title('Top 5 Anomalous Countries', fontsize=12, fontweight='bold')
            axes[2].grid(True, alpha=0.3, axis='x')
            
            # Add value labels
            for i, score in enumerate(scores):
                axes[2].text(score + 1, i, f'{score:.0f}', 
                           ha='left', va='center', fontsize=9, fontweight='bold')
        
        # 4. Top products - Horizontal bars
        if 'most_suspicious_products' in anomaly_summary:
            top_products = anomaly_summary['most_suspicious_products']
            products = list(top_products.keys())[:5]
            scores = list(top_products.values())[:5]
            
            # Sort for better visualization
            sorted_indices = np.argsort(scores)
            products = [products[i] for i in sorted_indices]
            scores = [scores[i] for i in sorted_indices]
            
            y_pos = range(len(products))
            axes[3].barh(y_pos, scores, color='lightblue', alpha=0.8)
            axes[3].set_yticks(y_pos)
            axes[3].set_yticklabels(products, fontsize=10)
            axes[3].set_xlabel('Average Severity Score')
            axes[3].set_title('Top 5 Suspicious Products', fontsize=12, fontweight='bold')
            axes[3].grid(True, alpha=0.3, axis='x')
            
            # Add value labels
            for i, score in enumerate(scores):
                axes[3].text(score + 0.5, i, f'{score:.1f}', 
                           ha='left', va='center', fontsize=9, fontweight='bold')
        
        # 5. Time trend
        yearly_trend = df.groupby('year')['is_anomaly'].mean() * 100
        axes[4].plot(yearly_trend.index, yearly_trend.values, marker='o', 
                    linewidth=2, color='green', markersize=6)
        axes[4].set_title('Anomaly Rate Over Time', fontsize=12, fontweight='bold')
        axes[4].set_ylabel('Anomaly Rate (%)')
        axes[4].set_xlabel('Year')
        axes[4].grid(True, alpha=0.3)
        
        # Add trend line
        if len(yearly_trend) > 1:
            z = np.polyfit(yearly_trend.index, yearly_trend.values, 1)
            p = np.poly1d(z)
            axes[4].plot(yearly_trend.index, p(yearly_trend.index), "r--", alpha=0.7, 
                        label=f'Trend: {z[0]:.2f}%/year')
            axes[4].legend()
        
        # 6. Severity distribution
        severity_data = df[df['is_anomaly']]['severity_score']
        if len(severity_data) > 0:
            axes[5].hist(severity_data, bins=20, alpha=0.7, color='orange', 
                        edgecolor='black', linewidth=0.5)
            axes[5].set_title('Anomaly Severity Distribution', fontsize=12, fontweight='bold')
            axes[5].set_xlabel('Severity Score')
            axes[5].set_ylabel('Count')
            axes[5].grid(True, alpha=0.3)
            
            # Add statistics
            mean_severity = severity_data.mean()
            axes[5].axvline(mean_severity, color='red', linestyle='--', 
                           label=f'Mean: {mean_severity:.1f}')
            axes[5].legend()
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.charts_dir, 'summary_dashboard.png'), 
                   dpi=300, bbox_inches='tight')
        plt.show()

    def create_interactive_product_analysis(self, df: pd.DataFrame):
        """Create interactive product analysis using Plotly (optional)"""
        try:
            import plotly.express as px
            
            anomaly_by_product = df.groupby('product_category').agg({
                'is_anomaly': ['mean', 'sum', 'count'],
                'severity_score': 'mean',
                'trade_volume': 'sum'
            }).round(4)
            
            # Flatten column names
            anomaly_by_product.columns = ['anomaly_rate', 'anomaly_count', 'total_records', 
                                         'avg_severity', 'total_volume']
            
            anomaly_by_product = anomaly_by_product.sort_values('anomaly_rate', ascending=True)
            
            # Create interactive bar chart
            fig = px.bar(
                anomaly_by_product,
                x='anomaly_rate',
                y=anomaly_by_product.index,
                orientation='h',
                title='Anomaly Prevalence by Product Category (Interactive)',
                labels={'anomaly_rate': 'Proportion of Anomalies', 'index': 'Product Category'},
                hover_data={
                    'anomaly_rate': ':.3f',
                    'anomaly_count': True,
                    'total_records': True,
                    'avg_severity': ':.2f',
                    'total_volume': ':,.0f'
                },
                color='anomaly_rate',
                color_continuous_scale='Blues'
            )
            
            fig.update_layout(
                height=600,
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'},
                font=dict(size=12)
            )
            
            # Save interactive plot
            fig.write_html(os.path.join(self.charts_dir, 'interactive_product_analysis.html'))
            
            # Also create static version
            fig.write_image(os.path.join(self.charts_dir, 'interactive_product_analysis.png'))
            
            return fig
            
        except ImportError:
            print("Plotly not available for interactive charts. Install with: pip install plotly")
            return None