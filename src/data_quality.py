"""
data_quality.py — Data Quality Assessment
=========================================
Performs comprehensive data quality checks:
- Missing values
- Duplicate rows
- Negative values (sales/profit/quantity)
- Outlier detection (IQR method)
- Data type validation
- Completeness report

Author: Yao Jiahan
Date: 2026-07-21
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import (
    safe_float, safe_int, describe_numeric,
    check_missing, check_negative, unique_values
)
from collections import defaultdict


class DataQualityReport:
    """Generates a comprehensive data quality assessment."""

    def __init__(self, data):
        self.data = data
        self.rows = data.rows
        self.headers = data.headers
        self.report = {}

    def run_all_checks(self) -> dict:
        """Execute all quality checks and return a structured report."""
        print("\n" + "=" * 60)
        print("  DATA QUALITY REPORT — Superstore Dataset")
        print("=" * 60)

        self.report['basic_info'] = self._check_basic_info()
        self.report['missing_values'] = self._check_missing_values()
        self.report['duplicates'] = self._check_duplicates()
        self.report['negative_values'] = self._check_negative_values()
        self.report['outliers'] = self._check_outliers()
        self.report['unique_values'] = self._check_unique_values()

        self._print_report()
        return self.report

    def _check_basic_info(self) -> dict:
        """Basic dataset info."""
        info = {
            'total_rows': len(self.rows),
            'total_columns': len(self.headers),
            'columns': self.headers,
        }
        print(f"\n[1] Basic Info")
        print(f"    Rows: {info['total_rows']:,}")
        print(f"    Columns: {info['total_columns']}")
        return info

    def _check_missing_values(self) -> dict:
        """Check for missing/empty values in each column."""
        print(f"\n[2] Missing Values Check")
        missing = {}
        all_clean = True
        for col in self.headers:
            count, pct = check_missing(self.rows, col)
            missing[col] = {'count': count, 'pct': pct}
            if count > 0:
                print(f"    ⚠ {col}: {count} missing ({pct}%)")
                all_clean = False

        if all_clean:
            print("    ✅ No missing values found")
        return missing

    def _check_duplicates(self) -> dict:
        """Detect duplicate rows."""
        print(f"\n[3] Duplicate Check")
        seen = set()
        duplicates = 0
        for row in self.rows:
            # Create a tuple of all values for comparison
            row_tuple = tuple(str(row.get(h, '')) for h in self.headers)
            if row_tuple in seen:
                duplicates += 1
            else:
                seen.add(row_tuple)

        result = {
            'duplicate_count': duplicates,
            'unique_rows': len(seen),
            'duplicate_pct': round(duplicates / len(self.rows) * 100, 2) if self.rows else 0,
        }
        if duplicates == 0:
            print("    ✅ No duplicate rows found")
        else:
            print(f"    ⚠ {duplicates} duplicate rows ({result['duplicate_pct']}%)")
        return result

    def _check_negative_values(self) -> dict:
        """Check for negative values in numeric columns."""
        print(f"\n[4] Negative Values Check")
        neg = {}
        for col in ['Sales', 'Quantity', 'Discount', 'Profit']:
            count, pct = check_negative(self.rows, col)
            neg[col] = {'count': count, 'pct': pct}
            if col == 'Profit':
                print(f"    📉 {col}: {count} negative ({pct}%) — expected (losses)")
            elif count > 0:
                print(f"    ❌ {col}: {count} negative ({pct}%) — UNEXPECTED!")
            else:
                print(f"    ✅ {col}: No negative values")
        return neg

    def _check_outliers(self) -> dict:
        """Detect outliers using IQR method for Sales and Profit."""
        print(f"\n[5] Outlier Detection (IQR Method)")

        outliers = {}
        for col in ['Sales', 'Profit']:
            values = [safe_float(row.get(col, 0)) for row in self.rows]
            values.sort()
            n = len(values)
            q1_val = values[n // 4]
            q3_val = values[(3 * n) // 4]
            iqr = q3_val - q1_val
            lower = q1_val - 1.5 * iqr
            upper = q3_val + 1.5 * iqr

            outlier_count = sum(1 for v in values if v < lower or v > upper)
            pct = round(outlier_count / n * 100, 2) if n > 0 else 0

            outliers[col] = {
                'q1': round(q1_val, 2),
                'q3': round(q3_val, 2),
                'iqr': round(iqr, 2),
                'lower_bound': round(lower, 2),
                'upper_bound': round(upper, 2),
                'outlier_count': outlier_count,
                'outlier_pct': pct,
            }
            print(f"    {col}: {outlier_count} outliers ({pct}%) "
                  f"[IQR={iqr:.0f}, bounds=({lower:.0f}, {upper:.0f})]")

        return outliers

    def _check_unique_values(self) -> dict:
        """Count unique values in categorical columns."""
        print(f"\n[6] Unique Value Counts")
        uniques = {}
        cat_cols = ['Ship Mode', 'Segment', 'Country', 'Region',
                    'Category', 'Sub-Category', 'State', 'City']
        for col in cat_cols:
            vals = unique_values(self.rows, col)
            uniques[col] = len(vals)
            print(f"    {col}: {len(vals)} unique values")

        return uniques

    def _print_report(self):
        """Print a summary conclusion."""
        print(f"\n{'=' * 60}")
        print("  OVERALL ASSESSMENT")
        print(f"{'=' * 60}")

        issues = []
        # Check for issues
        for col, info in self.report.get('missing_values', {}).items():
            if info['count'] > 0:
                issues.append(f"Missing values in '{col}'")

        dup = self.report.get('duplicates', {})
        if dup.get('duplicate_count', 0) > 0:
            issues.append(f"Duplicate rows detected")

        for col, info in self.report.get('negative_values', {}).items():
            if col != 'Profit' and info['count'] > 0:
                issues.append(f"Negative values in '{col}'")

        if issues:
            print(f"  ⚠ Issues found: {len(issues)}")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print("  ✅ Data quality is GOOD — ready for analysis")
        print(f"{'=' * 60}\n")
