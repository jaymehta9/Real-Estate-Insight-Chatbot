import json
import os
from pathlib import Path

import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "sample_data.xlsx"

df = pd.read_excel(DATA_PATH)

client = None
api_key = os.environ.get("OPENAI_API_KEY")
if api_key:
    client = OpenAI(api_key=api_key)


def build_chart_and_table(localities):
    filtered = df[df["final location"].isin(localities)].copy()

    yearly = (
        filtered.groupby(["final location", "year"])
        .agg(
            avg_price=("avg_price - igr", "mean"),
            avg_demand=("total_sold - igr", "mean"),
        )
        .reset_index()
        .sort_values(["final location", "year"])
    )

    chart = []
    for loc in localities:
        loc_data = yearly[yearly["final location"] == loc]
        chart.append(
            {
                "location": loc,
                "points": [
                    {
                        "year": int(row["year"]),
                        "price": float(row["avg_price"]),
                        "demand": float(row["avg_demand"]),
                    }
                    for _, row in loc_data.iterrows()
                ],
            }
        )

    table_rows = filtered.to_dict(orient="records")

    return chart, table_rows


def build_rule_based_summary(localities, chart):
    parts = []
    for series in chart:
        loc = series["location"]
        pts = series["points"]
        if not pts:
            continue
        start = pts[0]
        end = pts[-1]
        price_change = ((end["price"] - start["price"]) / start["price"]) * 100 if start["price"] else 0
        demand_change = (
            ((end["demand"] - start["demand"]) / start["demand"]) * 100
            if start["demand"]
            else 0
        )
        parts.append(
            f"{loc} shows an average price of ~{end['price']:.0f} in {end['year']} "
            f"with an approximate price change of {price_change:.1f}% and "
            f"demand change of {demand_change:.1f}% over the selected years."
        )

    if not parts:
        return "No matching data was found for the requested localities."

    return " ".join(parts)


def build_llm_summary(query, localities, chart, table_rows):
    if client is None:
        return None

    try:
        years = sorted({p["year"] for series in chart for p in series["points"]})
        prompt = f"""
You are an analyst for the Pune real estate market.

User query:
{query}

Localities:
{", ".join(localities)}

Years covered:
{", ".join(str(y) for y in years)}

You are given structured data about price and demand trends for these localities.
Write a concise, professional summary (max 5–7 sentences) covering:

- Overall price trend for each locality
- Relative demand between the localities
- Any notable changes over the years
- A short, practical insight a buyer or investor might care about

Avoid bullet points. Respond in plain English.
"""

        resp = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            max_output_tokens=300,
        )

        text = resp.output[0].content[0].text
        return text.strip()
    except Exception:
        return None


@csrf_exempt
def query_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        body = json.loads(request.body.decode("utf-8"))
        query = (body.get("query") or "").strip()
        if not query:
            return JsonResponse({"error": "Query is required"}, status=400)

        keywords = [
            "Ambegaon Budruk",
            "Aundh",
            "Wakad",
            "Akurdi",
        ]
        localities = [loc for loc in keywords if loc.lower() in query.lower()]
        if not localities:
            localities = ["Ambegaon Budruk"]

        chart, table_rows = build_chart_and_table(localities)

        summary = build_llm_summary(query, localities, chart, table_rows)
        if summary is None:
            summary = build_rule_based_summary(localities, chart)

        payload = {
            "query": query,
            "areas": localities,
            "summary": summary,
            "chart": chart,
            "table": table_rows,
        }
        return JsonResponse(payload)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
