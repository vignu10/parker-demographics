# parker-demographics project structure

parked_car_demographics/
│
├── data/ # Raw and intermediate CSVs (Colab mount point)
│ └── raw_data.csv
│
├── notebooks/ # Colab notebooks for exploration/testing
│ └── exploratory_analysis.ipynb
│
├── scripts/ # PySpark data processing scripts
│ ├── **init**.py
│ ├── ingest_data.py # Load raw CSV or ClickHouse into PySpark
│ ├── clean_data.py # Clean & normalize text, timestamps
│ ├── enrich_data.py # Add car value, luxury tier, income
│ ├── feature_engineering.py # Generate car_make_model, slot type, etc.
│ ├── aggregate_data.py # Aggregate by location
│ └── write_to_clickhouse.py # Write processed data back
│
├── models/ # Clustering model and utils
│ ├── **init**.py
│ ├── train_model.py # Train KMeans model
│ ├── predict_clusters.py # Predict and assign clusters
│ └── utils.py # Scaling, PCA, etc.
│
├── api/ # Flask API
│ ├── **init**.py
│ ├── app.py # Flask entry point
│ ├── routes.py # /predict, /status, etc.
│ └── utils.py # Model loading, input validation
│
├── configs/ # Configurations
│ ├── clickhouse_config.json # JDBC connection info
│ └── vehicle_api_config.json # Keys and URLs for car value API
│
├── requirements.txt # Python + Spark + Flask dependencies
├── run_pipeline.py # Orchestrates full pipeline (can run in Colab)
├── README.md # Project explanation and setup
└── .env # Secrets (optional: API keys, DB creds)
