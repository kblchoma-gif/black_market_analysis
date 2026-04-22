# Main execution script for Global Black Market Economy Estimation
import logging
from utils.helpers import setup_logging, Timer
from src.data_collection import ComtradeDataCollector
from src.data_preprocessing import TradeDataPreprocessor
from src.anomaly_detection import AnomalyDetector
from src.visualization import TradeVisualizer
from src.reporting import ReportGenerator

def main():
    """Main execution function"""
    # Setup logging
    logger = setup_logging()
    
    print("🚀 Global Black Market Economy Estimation Project")
    print("=" * 60)
    
    try:
        # 1. Data Collection
        print("\n📊 STEP 1: Data Collection")
        with Timer("Data collection"):
            collector = ComtradeDataCollector()
            # In production, use: raw_data = collector.collect_country_data()
            raw_data = collector.generate_sample_data()
            print(f"   Collected {len(raw_data)} trade records")
        
        # 2. Data Preprocessing
        print("\n🔧 STEP 2: Data Preprocessing")
        with Timer("Data preprocessing"):
            preprocessor = TradeDataPreprocessor()
            processed_data = preprocessor.prepare_analysis_dataset(raw_data)
            print(f"   Processed {len(processed_data)} records for analysis")
        
        # 3. Anomaly Detection
        print("\n🔍 STEP 3: Anomaly Detection")
        with Timer("Anomaly detection"):
            detector = AnomalyDetector()
            final_data = detector.detect_trade_anomalies(processed_data)
            anomaly_summary = detector.get_anomaly_summary(final_data)
            print(f"   Detected {anomaly_summary.get('total_anomalies', 0)} anomalies")
        
        # 4. Visualization
        print("\n📈 STEP 4: Visualization")
        with Timer("Visualization"):
            visualizer = TradeVisualizer()
            visualizer.create_comprehensive_visualizations(final_data, anomaly_summary)
            print("   Created comprehensive visualizations")
        
        # 5. Reporting
        print("\n📄 STEP 5: Reporting")
        with Timer("Report generation"):
            reporter = ReportGenerator()
            comprehensive_report = reporter.generate_comprehensive_report(final_data, anomaly_summary)
            print("   Generated comprehensive analysis report")
        
        # Project completion
        print("\n" + "=" * 60)
        print("✅ PROJECT COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        # Final summary
        total_anomalies = anomaly_summary.get('total_anomalies', 0)
        black_market_estimate = anomaly_summary.get('estimated_black_market_value', 0)
        
        print(f"\n📋 FINAL RESULTS:")
        print(f"   • Total records analyzed: {len(final_data):,}")
        print(f"   • Anomalies detected: {total_anomalies:,}")
        print(f"   • Anomaly rate: {anomaly_summary.get('anomaly_percentage', 0):.2f}%")
        print(f"   • Estimated black market value: ${black_market_estimate:,.0f}")
        print(f"   • Top anomalous country: {list(anomaly_summary.get('top_anomalous_countries', {}).keys())[:1]}")
        
        print(f"\n📁 OUTPUT FILES:")
        print(f"   • Analysis reports: outputs/reports/")
        print(f"   • Visualization charts: outputs/charts/")
        print(f"   • Log file: trade_analysis.log")
        
        print(f"\n💡 NEXT STEPS:")
        print(f"   • Review the generated Excel report for detailed findings")
        print(f"   • Examine visualization charts for patterns and insights")
        print(f"   • Investigate top anomalous relationships identified")
        
    except Exception as e:
        logger.error(f"Project execution failed: {e}")
        print(f"❌ Project failed with error: {e}")
        raise

if __name__ == "__main__":
    main()