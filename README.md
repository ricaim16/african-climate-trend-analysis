# African Climate Trend Analysis

This repository contains my interim project work for **B9W0: African Climate Trend Analysis**. It is designed to analyze long-term climate patterns across African countries using tabular climate data.

## Project Goal

The goal of this project is to:

- study temperature and rainfall trends across African countries
- compare changes over time
- generate summary tables and charts that support climate trend interpretation

## Repository Structure

```text
african-climate-analysis/
├── data/
│   ├── raw/                # Place your original dataset here
│   └── processed/          # Generated summary files
├── outputs/
│   └── figures/            # Generated charts
├── reports/
│   └── interim_summary.md  # Short write-up template
├── src/
│   └── climate_analysis.py # Main analysis script
├── .gitignore
├── README.md
└── requirements.txt
```

## Expected Dataset Format

Add your dataset to `data/raw/` as a CSV file. The script expects these columns:

- `country`
- `year`
- `temperature_c`
- `rainfall_mm`

Optional column:

- `region`

Example:

```csv
country,year,temperature_c,rainfall_mm,region
Kenya,2000,23.1,845.0,East Africa
Kenya,2001,23.4,821.2,East Africa
Ghana,2000,27.8,1182.5,West Africa
```

An example file is already included at `data/raw/example_climate_data.csv` so you can test the project immediately. Replace it or add your real dataset before final submission.

## Setup

1. Create or activate your virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run The Analysis

### Simple Project Command

If you want a short command similar to `npm run dev`, use:

```bash
make run
```

That will use the default example dataset.

You can also pass your own file:

```bash
make run INPUT=data/raw/your_file_name.csv
```

### Direct Python Command

If your file is named `african_climate_data.csv`:

```bash
python src/climate_analysis.py --input data/raw/african_climate_data.csv
```

You can also pass any other CSV path:

```bash
python src/climate_analysis.py --input data/raw/your_file_name.csv
```

To test the repository right away with the included example:

```bash
python src/climate_analysis.py --input data/raw/example_climate_data.csv
```

## Output Files

After running the script, the project will generate:

- `data/processed/country_trend_summary.csv`
- `data/processed/yearly_climate_summary.csv`
- `outputs/figures/temperature_trend.png`
- `outputs/figures/rainfall_trend.png`

## Testing

To run the automated test suite and verify the analysis logic:

```bash
pytest src/test_climate_analysis.py
```

## Original Contribution

This repository includes:

- a reproducible Python analysis workflow
- data cleaning and validation steps
- automated summary generation
- climate trend visualizations
- documentation for interpretation and submission

## Before You Submit

Make sure you:

1. add your real dataset to `data/raw/`
2. run the analysis script successfully
3. update `reports/interim_summary.md` with your findings
4. push the repository to GitHub
5. submit the GitHub repository link

## Suggested Git Commands

```bash
git add .
git commit -m "Add African climate trend analysis interim project"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```
