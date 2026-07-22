"""
helpers.py — Utility Functions
==============================
Pure Python data manipulation utilities for the Superstore analysis.
Provides group-by, aggregation, and statistical helpers without NumPy/Pandas.

Author: Yao Jiahan
Date: 2026-07-21
"""

import csv
import statistics
import math
from collections import defaultdict
from typing import Any


def load_csv(filepath: str) -> tuple[list[str], list[dict]]:
    """Load CSV file and return (headers, rows as list of dicts)."""
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        rows = [row for row in reader]
    return headers, rows


def safe_float(value: Any) -> float:
    """Convert value to float, return 0.0 on failure."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def safe_int(value: Any) -> int:
    """Convert value to int, return 0 on failure."""
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return 0


def group_by(rows: list[dict], key: str) -> dict[str, list[dict]]:
    """Group rows by a key column. Returns {key_value: [rows]}."""
    groups = defaultdict(list)
    for row in rows:
        groups[row.get(key, 'Unknown')].append(row)
    return dict(groups)


def sum_by(rows: list[dict], group_key: str, value_key: str) -> dict[str, float]:
    """Sum a numeric column grouped by a categorical column."""
    result = defaultdict(float)
    for row in rows:
        result[row.get(group_key, 'Unknown')] += safe_float(row.get(value_key, 0))
    return dict(result)


def avg_by(rows: list[dict], group_key: str, value_key: str) -> dict[str, float]:
    """Average a numeric column grouped by a categorical column."""
    sums = defaultdict(float)
    counts = defaultdict(int)
    for row in rows:
        key = row.get(group_key, 'Unknown')
        sums[key] += safe_float(row.get(value_key, 0))
        counts[key] += 1
    return {k: sums[k] / counts[k] for k in sums}


def count_by(rows: list[dict], key: str) -> dict[str, int]:
    """Count rows grouped by a categorical column."""
    result = defaultdict(int)
    for row in rows:
        result[row.get(key, 'Unknown')] += 1
    return dict(result)


def filter_rows(rows: list[dict], **conditions) -> list[dict]:
    """Filter rows by column conditions. e.g., filter_rows(rows, Region='West')."""
    result = []
    for row in rows:
        match = True
        for key, value in conditions.items():
            if str(row.get(key, '')) != str(value):
                match = False
                break
        if match:
            result.append(row)
    return result


def describe_numeric(rows: list[dict], column: str) -> dict:
    """Compute descriptive statistics for a numeric column."""
    values = [safe_float(row.get(column, 0)) for row in rows]
    values.sort()
    n = len(values)
    if n == 0:
        return {'count': 0, 'mean': 0, 'median': 0, 'std': 0,
                'min': 0, 'max': 0, 'sum': 0, 'q1': 0, 'q3': 0}

    mean_val = statistics.mean(values)
    median_val = statistics.median(values)
    stdev = statistics.stdev(values) if n > 1 else 0.0

    q1_idx = n // 4
    q3_idx = (3 * n) // 4

    return {
        'count': n,
        'mean': round(mean_val, 2),
        'median': round(median_val, 2),
        'std': round(stdev, 2),
        'min': round(values[0], 2),
        'max': round(values[-1], 2),
        'sum': round(sum(values), 2),
        'q1': round(values[q1_idx], 2),
        'q3': round(values[q3_idx], 2),
    }


def top_n(rows: list[dict], group_key: str, value_key: str,
          n: int = 10, ascending: bool = False) -> list[tuple[str, float]]:
    """Get top/bottom N items by aggregated sum."""
    sums = sum_by(rows, group_key, value_key)
    sorted_items = sorted(sums.items(), key=lambda x: x[1], reverse=not ascending)
    return sorted_items[:n]


def pct_of_total(part: float, whole: float) -> float:
    """Calculate percentage of total, return 0 if whole is zero."""
    if whole == 0:
        return 0.0
    return round(part / whole * 100, 1)


def unique_values(rows: list[dict], column: str) -> set:
    """Get unique values in a column."""
    return {str(row.get(column, '')) for row in rows}


def multi_group_by(rows: list[dict], keys: list[str],
                   value_key: str, agg: str = 'sum') -> dict:
    """Group by multiple keys and aggregate a value column."""
    result = defaultdict(float)
    counts = defaultdict(int)
    for row in rows:
        composite_key = tuple(row.get(k, 'Unknown') for k in keys)
        val = safe_float(row.get(value_key, 0))
        result[composite_key] += val
        counts[composite_key] += 1
    if agg == 'avg':
        result = {k: result[k] / counts[k] for k in result}
    return dict(result)


def check_missing(rows: list[dict], column: str) -> tuple[int, float]:
    """Count missing/empty values in a column. Returns (count, pct)."""
    total = len(rows)
    missing = 0
    for row in rows:
        val = row.get(column, None)
        if val is None or val == '' or (isinstance(val, str) and not val.strip()):
            missing += 1
    return missing, pct_of_total(missing, total)


def check_negative(rows: list[dict], column: str) -> tuple[int, float]:
    """Count negative values in a numeric column. Returns (count, pct)."""
    total = len(rows)
    neg = sum(1 for row in rows if safe_float(row.get(column, 0)) < 0)
    return neg, pct_of_total(neg, total)
