# InsightX: Leadership Analytics

This project, **InsightX: Leadership Analytics**, is designed to provide analytics and insights into leadership metrics. The application is built using Python 3.10+, Streamlit, and Pandas, and aims to deliver an interactive user experience for analyzing leadership data.

## Project Structure

The project is organized into the following directories and files:

```
insightx-leadership-analytics
├── src
│   ├── __init__.py
│   ├── app.py
│   ├── components
│   │   ├── __init__.py
│   │   ├── charts.py
│   │   ├── filters.py
│   │   └── sidebar.py
│   ├── pages
│   │   ├── __init__.py
│   │   ├── dashboard.py
│   │   ├── analytics.py
│   │   └── reports.py
│   ├── services
│   │   ├── __init__.py
│   │   └── data_service.py
│   ├── utils
│   │   ├── __init__.py
│   │   └── helpers.py
│   └── models
│       ├── __init__.py
│       └── schemas.py
├── data
│   └── .gitkeep
├── tests
│   ├── __init__.py
│   └── test_app.py
├── .streamlit
│   └── config.toml
├── requirements.txt
├── pyproject.toml
├── .gitignore
└── README.md
```

## Installation

To set up the project, clone the repository and install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Recommended: Use the Launcher Script

```bash
# Activate virtual environment first
.venv\Scripts\activate   # Windows
source .venv/bin/activate   # Linux/Mac

# Run the launcher (handles Python path automatically)
python run_app.py
```

### Alternative: Direct Streamlit Command

```bash
cd insightx-leadership-analytics
streamlit run src/app.py
```

### Verify Setup

```bash
python check_imports.py
```

This will verify all imports and CSS fixes are in place.

This will start the Streamlit server and open the application in your default web browser.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Acknowledgments

- Streamlit for providing an excellent framework for building interactive web applications.
- Pandas for data manipulation and analysis.

This README serves as a starting point for understanding and contributing to the InsightX: Leadership Analytics project.