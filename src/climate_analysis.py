from __future__ import annotations

import argparse
import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = {"country", "year", "temperature_c", "rainfall_mm"}
ALIASES = {
    "temperature": "temperature_c",
    "avg_temperature": "temperature_c",
    "avg_temperature_c": "temperature_c",
    "temp_c": "temperature_c",
    "rainfall": "rainfall_mm",
    "precipitation_mm": "rainfall_mm",
    "precipitation": "rainfall_mm",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze African temperature and rainfall trends from a CSV file."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input CSV file.",
    )
    parser.add_argument(
        "--processed-dir",
        default="data/processed",
        help="Directory for generated summary CSV files.",
    )
    parser.add_argument(
        "--figures-dir",
        default="outputs/figures",
        help="Directory for generated charts.",
    )
    return parser.parse_args()


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map input columns to standard internal names."""
    renamed = {column: ALIASES.get(column.strip().lower(), column.strip().lower()) for column in df.columns}
    return df.rename(columns=renamed)


def validate_columns(df: pd.DataFrame) -> None:
    """Ensure required columns are present in the DataFrame."""
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(
            f"Missing required columns: {missing_text}. "
            "Expected at least country, year, temperature_c, and rainfall_mm."
        )


def load_and_clean_data(input_path: Path) -> pd.DataFrame:
    """Load CSV and perform type conversion/cleaning."""
    df = pd.read_csv(input_path)
    df = normalize_columns(df)
    validate_columns(df)

    numeric_columns = ["year", "temperature_c", "rainfall_mm"]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["country"] = df["country"].astype(str).str.strip()
    if "region" in df.columns:
        df["region"] = df["region"].astype(str).str.strip()

    df = df.dropna(subset=["country", "year", "temperature_c", "rainfall_mm"])
    df = df[df["country"] != ""]
    df["year"] = df["year"].astype(int)
    return df.sort_values(["country", "year"]).reset_index(drop=True)


def calculate_slope(x: np.ndarray, y: np.ndarray) -> float:
    """Compute linear regression slope; return 0.0 if data is insufficient."""
    if len(x) > 1 and np.var(x) > 0:
        return float(np.polyfit(x, y, 1)[0])
    return 0.0


def compute_country_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Compute per-country averages and multi-year trends."""
    summaries: list[dict[str, float | int | str]] = []

    for country, group in df.groupby("country", sort=True):
        years = group["year"].to_numpy()
        temp = group["temperature_c"].to_numpy()
        rainfall = group["rainfall_mm"].to_numpy()

        temp_slope = calculate_slope(years, temp)
        rainfall_slope = calculate_slope(years, rainfall)

        summary = {
            "country": country,
            "records": int(len(group)),
            "start_year": int(group["year"].min()),
            "end_year": int(group["year"].max()),
            "avg_temperature_c": round(float(group["temperature_c"].mean()), 2),
            "avg_rainfall_mm": round(float(group["rainfall_mm"].mean()), 2),
            "temperature_trend_per_year": round(float(temp_slope), 4),
            "rainfall_trend_per_year": round(float(rainfall_slope), 4),
        }

        if "region" in group.columns:
            region_modes = group["region"].mode()
            summary["region"] = region_modes.iat[0] if not region_modes.empty else "Unknown"

        summaries.append(summary)

    columns = [
        "country",
        "region",
        "records",
        "start_year",
        "end_year",
        "avg_temperature_c",
        "avg_rainfall_mm",
        "temperature_trend_per_year",
        "rainfall_trend_per_year",
    ]
    summary_df = pd.DataFrame(summaries)
    return summary_df.reindex(columns=[column for column in columns if column in summary_df.columns])


def compute_yearly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate data by year for continental analysis."""
    summary = (
        df.groupby("year", as_index=False)
        .agg(
            mean_temperature_c=("temperature_c", "mean"),
            mean_rainfall_mm=("rainfall_mm", "mean"),
            country_count=("country", "nunique"),
        )
        .sort_values("year")
    )
    summary["mean_temperature_c"] = summary["mean_temperature_c"].round(2)
    summary["mean_rainfall_mm"] = summary["mean_rainfall_mm"].round(2)
    return summary


def save_plot(
    yearly_summary: pd.DataFrame,
    y_column: str,
    title: str,
    y_label: str,
    output_path: Path,
    add_trendline: bool = True,
) -> None:
    """Generate and export a time-series plot."""
    plt.figure(figsize=(10, 5))
    plt.plot(
        yearly_summary["year"],
        yearly_summary[y_column],
        marker="o",
        linewidth=1.5,
        color="#1f77b4",
        label="Annual Mean",
    )

    if add_trendline and len(yearly_summary) > 1:
        z = np.polyfit(yearly_summary["year"], yearly_summary[y_column], 1)
        p = np.poly1d(z)
        plt.plot(
            yearly_summary["year"],
            p(yearly_summary["year"]),
            "r--",
            alpha=0.8,
            label=f"Trend ({z[0]:.4f}/yr)",
        )
        plt.legend()

    plt.title(title)
    plt.xlabel("Year")
    plt.ylabel(y_label)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    logger.info(f"Saved plot: {output_path}")
    plt.close()


def generate_html_report(
    country_summary: pd.DataFrame,
    yearly_summary: pd.DataFrame,
    output_path: Path,
) -> None:
    """Export a summary dashboard as HTML."""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Climate Analysis Dashboard</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px; line-height: 1.6; color: #333; background-color: #f8f9fa; }}
            .container {{ max-width: 1100px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1, h2 {{ color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
            .charts {{ display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 40px; }}
            .chart {{ flex: 1; min-width: 450px; text-align: center; }}
            img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; font-size: 0.9em; }}
            th {{ background-color: #1f77b4; color: white; text-align: left; padding: 12px; }}
            td {{ padding: 12px; border-bottom: 1px solid #eee; }}
            tr:hover {{ background-color: #f5f5f5; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>African Climate Trend Analysis</h1>
            <h2>Continental Trends</h2>
            <div class="charts">
                <div class="chart"><h3>Temperature Trend</h3><img src="figures/temperature_trend.png"></div>
                <div class="chart"><h3>Rainfall Trend</h3><img src="figures/rainfall_trend.png"></div>
            </div>
            <h2>Country-Level Summary</h2>
            {country_summary.to_html(index=False, classes='table')}
            <h2>Last 10 Years Aggregate</h2>
            {yearly_summary.tail(10).to_html(index=False, classes='table')}
        </div>
    </body>
    </html>
    """
    output_path.write_text(html_content)
    logger.info(f"Generated HTML report: {output_path}")


def ensure_directories(*paths: Path) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    processed_dir = Path(args.processed_dir)
    figures_dir = Path(args.figures_dir)

    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return

    ensure_directories(processed_dir, figures_dir)

    try:
        df = load_and_clean_data(input_path)
        
        if df.empty:
            logger.warning(f"No valid data found in {input_path} after cleaning. No files generated.")
            return

        country_summary = compute_country_trends(df)
        yearly_summary = compute_yearly_summary(df)

        country_csv = processed_dir / "country_trend_summary.csv"
        yearly_csv = processed_dir / "yearly_climate_summary.csv"
        
        country_summary.to_csv(country_csv, index=False)
        yearly_summary.to_csv(yearly_csv, index=False)

        # Generate and save plots
        save_plot(
            yearly_summary,
            y_column="mean_temperature_c",
            title="Average Temperature Trend Across Recorded Years",
            y_label="Temperature (C)",
            output_path=figures_dir / "temperature_trend.png",
        )
        save_plot(
            yearly_summary,
            y_column="mean_rainfall_mm",
            title="Average Rainfall Trend Across Recorded Years",
            y_label="Rainfall (mm)",
            output_path=figures_dir / "rainfall_trend.png",
        )

        generate_html_report(
            country_summary=country_summary,
            yearly_summary=yearly_summary,
            output_path=figures_dir.parent / "summary_report.html"
        )

        logger.info(f"Pipeline finished. Outputs in {processed_dir} and {figures_dir}")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")


if __name__ == "__main__":
    main()
