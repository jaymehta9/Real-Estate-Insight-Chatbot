import json
import math

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .utils import (
    load_data,
    extract_areas_from_query,
    build_chart_data,
    build_llm_summary,
    build_rule_summary,
    AREA_COL,
    YEAR_COL,
)


def _clean_value(v):
    if v is None:
        return None
    if isinstance(v, float):
        if math.isnan(v) or math.isinf(v):
            return None
    try:
        if hasattr(v, "item"):
            v = v.item()
    except Exception:
        pass
    return v


@csrf_exempt
def query_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        payload = {}

    query = payload.get("query", "")
    if not query:
        return JsonResponse({"error": "Query is required"}, status=400)

    df = load_data()

    if AREA_COL not in df.columns or YEAR_COL not in df.columns:
        return JsonResponse(
            {"error": "Dataset does not have required columns"}, status=500
        )

    areas_in_data = df[AREA_COL].dropna().unique()
    selected_areas = extract_areas_from_query(query, areas_in_data)

    if not selected_areas:
        return JsonResponse(
            {"error": "No matching localities found in dataset"}, status=404
        )

    filtered = df[df[AREA_COL].isin(selected_areas)]

    llm_summary = build_llm_summary(query, selected_areas, filtered)
    if llm_summary:
        summary_text = llm_summary
    else:
        parts = []
        for area in selected_areas:
            area_df = filtered[filtered[AREA_COL] == area]
            parts.append(build_rule_summary(area, area_df))
        summary_text = " ".join(parts)

    chart = build_chart_data(filtered, selected_areas)

    table = []
    for _, row in filtered.iterrows():
        raw = row.to_dict()
        clean_row = {k: _clean_value(v) for k, v in raw.items()}
        table.append(clean_row)

    response = {
        "query": query,
        "areas": list(selected_areas),
        "summary": summary_text,
        "chart": chart,
        "table": table,
    }
    return JsonResponse(response)
