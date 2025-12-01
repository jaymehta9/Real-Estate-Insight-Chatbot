from pathlib import Path
import os
import math

import pandas as pd
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "sample_data.xlsx"

AREA_COL = "final location"
YEAR_COL = "year"
PRICE_COL = "flat - weighted average rate"
DEMAND_COL = "total_sales - igr"

_df_cache = None
_client = None


def load_data():
    global _df_cache
    if _df_cache is None:
        df = pd.read_excel(DATA_PATH)
        df.columns = [str(c).strip() for c in df.columns]
        _df_cache = df
    return _df_cache


def extract_areas_from_query(query, areas):
    text = query.lower()
    selected = []
    for a in areas:
        name = str(a)
        if name.lower() in text:
            selected.append(name)
    if selected:
        return list(dict.fromkeys(selected))
    words = [w for w in text.replace(",", " ").split() if len(w) > 2]
    for w in words:
        for a in areas:
            name = str(a)
            if w in name.lower():
                selected.append(name)
    if selected:
        return list(dict.fromkeys(selected))
    return []


def _build_basic_stats_text(df, areas):
    lines = []
    for area in areas:
        area_df = df[df[AREA_COL] == area]
        if area_df.empty:
            continue
        if YEAR_COL not in area_df.columns or PRICE_COL not in area_df.columns:
            continue
        grouped = (
            area_df.groupby(YEAR_COL)
            .agg(
                price=(PRICE_COL, "mean"),
                demand=(DEMAND_COL, "mean")
                if DEMAND_COL in area_df.columns
                else (PRICE_COL, "mean"),
            )
            .reset_index()
        )
        for _, row in grouped.sort_values(YEAR_COL).iterrows():
            year = row[YEAR_COL]
            price = row["price"]
            demand = row.get("demand")
            if pd.isna(year) or pd.isna(price):
                continue
            line = f"{area} in {int(year)}: average price {round(float(price), 2)}"
            if demand is not None and not pd.isna(demand):
                line += f", average demand {round(float(demand), 2)}"
            lines.append(line)
    return "\n".join(lines)


def _get_client():
    global _client
    if _client is not None:
        return _client
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    _client = OpenAI(api_key=api_key)
    return _client


def build_llm_summary(query, areas, df):
    client = _get_client()
    if client is None:
        return None
    stats_text = _build_basic_stats_text(df, areas)
    if not stats_text:
        return None
    prompt = (
        "You are a senior real-estate data analyst. "
        "Write a concise, professional summary (3–5 sentences) based only on the structured data below. "
        "Explain price trends over time, mention demand only if present, and compare the localities if more than one is provided.\n\n"
        f"User query: {query}\n\n"
        "Data:\n"
        f"{stats_text}"
    )
    try:
        response = client.responses.create(
            model="gpt-5.1-mini",
            input=prompt,
        )
        return response.output_text
    except Exception:
        return None


def build_rule_summary(area, frame):
    if frame is None or frame.empty:
        return f"Data for {area} is limited in the dataset."
    if PRICE_COL not in frame.columns or YEAR_COL not in frame.columns:
        return f"Data for {area} is limited in the dataset."
    prices = frame[PRICE_COL].dropna()
    years = sorted(frame[YEAR_COL].dropna().unique())
    demands = frame[DEMAND_COL].dropna() if DEMAND_COL in frame.columns else []
    if not len(prices) or not len(years):
        return f"Data for {area} is limited in the dataset."
    avg_price = round(prices.mean(), 2)
    first_year = years[0]
    last_year = years[-1]
    first_price = frame[frame[YEAR_COL] == first_year][PRICE_COL].mean()
    last_price = frame[frame[YEAR_COL] == last_year][PRICE_COL].mean()
    if pd.notna(first_price) and pd.notna(last_price) and first_price != 0:
        growth = round((last_price - first_price) / first_price * 100, 2)
    else:
        growth = 0
    if len(demands):
        avg_demand = round(demands.mean(), 2)
    else:
        avg_demand = 0
    if growth > 5:
        trend = "upward"
    elif growth < -5:
        trend = "downward"
    else:
        trend = "stable"
    return (
        f"{area} shows a {trend} price trend from {first_year} to {last_year} "
        f"with an average price of {avg_price} and approximate growth of {growth} percent. "
        f"Average demand in this period is {avg_demand}."
    )


def build_chart_data(df, areas):
    series = []
    for area in areas:
        area_df = df[df[AREA_COL] == area]
        if area_df.empty:
            continue
        if YEAR_COL not in area_df.columns or PRICE_COL not in area_df.columns:
            continue
        grouped = (
            area_df.groupby(YEAR_COL)
            .agg(
                price=(PRICE_COL, "mean"),
                demand=(DEMAND_COL, "mean")
                if DEMAND_COL in area_df.columns
                else (PRICE_COL, "mean"),
            )
            .reset_index()
        )
        points = []
        for _, row in grouped.sort_values(YEAR_COL).iterrows():
            year = row[YEAR_COL]
            price = row["price"]
            demand = row.get("demand")
            points.append(
                {
                    "year": int(year) if not pd.isna(year) else None,
                    "price": float(price) if not pd.isna(price) else None,
                    "demand": float(demand)
                    if demand is not None and not pd.isna(demand)
                    else None,
                }
            )
        series.append({"name": area, "points": points})
    return series
