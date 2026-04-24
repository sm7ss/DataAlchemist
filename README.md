# 🚧 Data Alchemist [WIP]

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.53%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.5%2B-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Polars](https://img.shields.io/badge/Polars-1.37%2B-orange?style=for-the-badge&logo=polars&logoColor=white)](https://pola.rs)
![NumPy](https://img.shields.io/badge/NumPy-1.24%2B-013243?style=for-the-badge&logo=numpy&logoColor=white)
[![Plotly](https://img.shields.io/badge/Plotly-6.5%2B-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?style=for-the-badge&logo=pandas&logoColor=white)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.12%2B-E92063?style=for-the-badge&logo=pydantic&logoColor=white)](https://docs.pydantic.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](https://opensource.org/licenses/MIT)

> ⚠️ **PROJECT IN ACTIVE DEVELOPMENT**
> This reposiotio documents the design and architecture of an interactive platform that democratizes machine learning; loading your data, selecting your target, and the platform.

**Data Alchemist** is an interactive platform that democratizes machine learning. 
Upload your data, select your target, and the platform:
- Automatically analyzes available memory
- Decide the optimal strategy (eager/lazy/streaming)
- Guides you in pre-processing and model selection
- Train and evaluate in real time
- Export your model and processed data

✅ Ideal for **data scientists**, **analysts**, and **anyone** who wants to experiment with ML without worrying about infrastructure.

---

## 📍 Project Status

| Module               | Status           | What it does                                                                 |
|----------------------|------------------|------------------------------------------------------------------------------|
| **EDA**              | ✅ Completed     | General analysis, nulls, distributions, outliers, correlations, categorical  |
| **Cleaning**         | 🚧 In development| Applying cleaning suggestions                                                |
| **Preprocessing**    | 🚧 In development| Transformations, scaling, encoding                                           |
| **Modeling**         | 🚧 In development| Algorithm selection, hyperparameter tuning                                   |
| **Training**         | 🚧 In development| Metrics, learning curves, comparisons                                        |
| **Export**           | 🚧 In development| Trained model + processed data (Parquet)                                     |
| **Visual Dashboard** | 📝 Planned       | Interface with sliders and interactive main panel                            |

> 🐥 **You can already run EDA from the terminal and get reports in JSON + TXT.**

---

## ✨ Current Features (EDA)

### 📊 General Analysis
- Dataset dimensions (rows × columns)
- Available columns and their data types
- Descriptive statistics for numeric columns
- Unique value count for categorical columns

### 🔍 Null Analysis
- Total nulls per column and per row
- Null percentage
- Suggested action: `keep`, `analyse`, or `delete`

### 📊 Distribution (numeric)
- Range, mean, median, IQR
- Tail shape (positive/negative/balanced)
- Data concentration level
- **ML Suggestions**: transformer (`log1p`, `sqrt`, `square`) and scaler (`minMaxScaler`, `robustScaler`, `standarScaler`)

### 🚨 Outliers (numeric)
- IQR, number and percentage of outliers
- **ML Suggestions**:
  - Scaler (`robustScaler`, `standarScaler`, `minMaxScaler`)
  - Filtering (`trim`, `capping`)
  - Imputation (`median`)
  - Flag (True/False)
  - Transformation (`log1p`, `sqrt`)

### 🔗 Correlations (numeric)
- Numeric correlation matrix
- High correlation detection (configurable threshold)
- Recommendation note (`remove`, `join`, or `filter`)

### 🏷️ Categorical Domain
- Total unique values per column
- Top values with percentages
- Detected rare values
- **ML Suggestions**:
  - `ordinalEncoder` (few categories)
  - `targetEncoder` (many categories / high cardinality)
  - `oneHotEncoder` (grouped rare values)
  - Null handling for categorical columns

---

## ⚙️ YAML Configuration

All EDA behavior is **fully configurable** without touching the code.

### [config.yml](config/config.yml) (main)

```yaml
path: 
  data: 'users_behavior.csv'
  overhead_percent: 1.8
  sample_data_percent: 0.1 

eda: 
  general_information: True
  null_values: True
  null_values_percent_column: 0.65
  null_values_percent_row: 0.40
  basic_analysis_data: 
    distribution: 
      columns: 
      enable: True
    outliers: 
      columns:
      enable: True
      method: # If no method is provided, the value will be 'iqr'
    correlation: 
      columns: 
      enable: True
    category_dominance: 
      columns: 
      enable: True
      top_n: # If no top_n is provided, the value will be 2
      rare_threshold_percent: # If no threshold is given, the value will be 0.01
```

### [config_analysis_values.yml](config/config_analysis_values.yml) (ML decisions)

```yaml 
distribution_decision_maker: 
  tail_length: 100
  scaler_concentration: 0.3

outlier_decision_maker: 
  scaler: 
    robust_scaler_percent: 5.0
    standard_scaler_percent: 1.0
  filter: 
    none: 10.0
    trim: 2.0
  # ... more configurations
```

> 🐥 You can adjust thresholds, methods, and suggestions according to your criteria.

---

## 🖥️ Current Usage (terminal)

```bash 
# Run EDA with your config
python main.py --config config.yml
```

### 📦 Generated Outputs

| File	             | Format |	Content                                                   |
|--------------------|--------|-----------------------------------------------------------|
| JSON_analysis.json | JSON	  | Structured data with all analyses                         |
| TXT_report.txt	 | TXT	  | Human-readable report with emojis and friendly formatting |

### 📄 Example Output (TXT)

```text
========================================================================================
                                    DATA ALCHEMIST  
                             🐥 ANALYSIS REPORT (TEXT MODE)
========================================================================================
📅 Date: 2026-04-22
📁 Dataset: users_behavior.csv
📊 Shape: 3214 rows | 5 columns
========================================================================================
GENERAL INFO
----------------------------------------------------------------------------------------
📝 Available Columns: calls, minutes, messages, mb_used, is_ultra
...

🚨 calls
    - IQR: 42.0
    - Total of Outliers: 62
    - Percent: 1.929
    ML Suggestions: 
       - Scaler: minMaxScaler
       - Filter: trim
       - Impute: median
...

✅ High correlations identified for model consideration
⚠️ Priority suggestions: Join, filter, remove or group calls, minutes
...
```

---

## 🧱 Project Structure

```text 
📂 data_alchemist/
├── 📂 config 
│   └── config_analysis_values.yml    # ML configuration
│   └── config.yml                    # Main configuration
├── 📂 data                           # Datasets
├── 📂 eda_analysis                   # Reports by date
├── 📂 src/
│   ├── 📂 eda/
│   │   ├── eda_general_info.py       # Dimensions, types, statistics
│   │   ├── eda_null_val.py           # Null analysis
│   │   ├── eda_analysis_data.py      # Distribution, outliers, correlations, categorical
│   │   └── pipeline_eda.py           # Pipeline orchestrator
│   ├── 📂 io/
│   │   └── folder_file_manager.py    # Output management (JSON/TXT)
│   ├── 📂 strategies/
│   │   └── strategies.py                 # Enums for validation strategies
│   │   └── pre_processing_strategies.py  # Enums for feature engineering strategies
│   ├── 📂 validation/
|   |   ├── 📂 validation_analysis_values/
│   │   |   ├── validation.py                  # ML config validation
│   │   └── eda_validation.py                  # General config validation
│   │   └── read_validation.py                 # Validation reader
│   │   └── validation.py                      # Validation orchestrator
│   └── get_frame.py                           # Data loading (eager)
├── .gitignore
├── LICENSE
├── README-ESP.md
├── README.md
├── main.py
└── requirements.txt
```

--- 

## 🛠️ Technologies Used

| **Library**  | **Version** |	**Purpose**                       |
|--------------|-------------|------------------------------------|
| **Python**   | 3.10.18	 | Base language                      |
| **Polars**   | 1.39.3	     | Fast and efficient data processing |
| **Pydantic** | 2.12.5	     | Configuration validation           |
| **PyYAML**   | 6.0.3	     | YAML file parsing                  |
| **tomli**	   | 2.4.1	     | TOML support (alternative)         |
| **pathlib**  | built-in    | Path management                    | 
| **psutil**   | -	         | Resource monitoring (future)       |
| **datetime** | built-in	 | Timestamps in reports              |

--- 

## 🚀 Future Vision (dashboard)

```text
┌─────────────────────────────────────────────────────────────┐
│  🧙‍♂️ DATA ALCHEMIST                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. DATA LOADING (Polars)                                   │
│     └── pl.read_csv() → type detection, memory              │
│                                                             │
│  2. EDA & CLEANING (Polars)                                 │
│     └── nulls, distributions, outliers (your framework)     │
│                                                             │
│  3. PREPROCESSING (Polars → numpy)                          │
│     └── .to_numpy() / .to_pandas() for Scikit-learn         │
│                                                             │
│  4. MODELING (Scikit-learn)                                 │
│     └── train_test_split, models, metrics                   │
│                                                             │
│  5. VISUALIZATION (Plotly)                                  │
│     └── results, curves, matrices                           │
│                                                             │
│  6. EXPORT (Polars)                                         │
│     └── results to Parquet/CSV                              │
└─────────────────────────────────────────────────────────────┘
```

### Planned Features:

    - Side slider to navigate between modules
    - Automatic mode detection: eager | lazy | streaming
    - One-click application of suggestions
    - Basic model training (regression/classification)
    - Export to Parquet and trained model
    - Real-time resource monitoring (100% local)

---

## 🤝 How to Contribute

Fork the project
Create your branch (git checkout -b feature/new-feature)
Commit your changes (git commit -m 'Add new feature')
Push to the branch (git push origin feature/new-feature)
Open a Pull Request

> 💡🐥 Ideas for the interface? Usability suggestions for non-programmers? Open to feedback!

--- 

## 📄 License

This project is licensed under the MIT License
You are free to use, modify, and share it

--- 

## 📬 Contact

🐥 **Data Alchemist** 
Questions or suggestions? Open an issue or contact me directly.



---



