# 🌍 Global Black Market Economy Estimation

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)

## 📊 Project Overview
This advanced data analysis project uncovers potential unreported or illicit trade flows between countries by analyzing statistical asymmetries in bilateral trade data from UN Comtrade.

## 🚀 Key Features
- **🔍 Data Collection**: UN Comtrade API integration with sample data generation
- **📈 Anomaly Detection**: Multiple statistical methods (Z-score, MAD, IQR)
- **📊 Visualization**: Comprehensive charts, heatmaps, and interactive dashboards  
- **📋 Reporting**: Detailed Excel and JSON reports with executive summaries
- **🏗️ Architecture**: Modular, scalable Python design

## 🛠️ Quick Start

### Installation
```bash
git clone https://github.com/Kabelo-ops-code/black-market-analysis.git
cd black-market-analysis
pip install -r requirements.txt

**### Basic Usage**
python main.py
📁 Project Structure
black_market_analysis/
│
├── main.py                 # Main execution script
├── config.py              # Configuration and settings
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── LICENSE               # MIT License
├── .gitignore           # Git ignore rules
│
├── src/                  # Source code modules
│   ├── __init__.py
│   ├── data_collection.py      # UN Comtrade API integration
│   ├── data_preprocessing.py   # Data cleaning and feature engineering
│   ├── anomaly_detection.py    # Statistical anomaly detection
│   ├── visualization.py        # Charts and dashboards
│   └── reporting.py           # Report generation
│
├── utils/                # Utility functions
│   ├── __init__.py
│   └── helpers.py        # Helper functions and logging
│
├── data/                 # Data storage
│   ├── raw/             # Raw data from APIs
│   └── processed/       # Cleaned and processed data
│
└── outputs/             # Generated outputs
    ├── reports/         # Excel and JSON reports
    └── charts/          # Visualization images


