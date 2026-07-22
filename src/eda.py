"""
eda.py — Exploratory Data Analysis Engine
=========================================
Performs comprehensive EDA using pure Python + Plotly.
Covers all required dimensions:
1. Sales Trend (by category/region)
2. Profit Analysis
3. Regional Analysis
4. Product Analysis (Top 10, Loss-making)
5. Customer Segment Analysis
6. Discount Impact Analysis
7. Profit Margin Analysis
8. Pareto Analysis (80/20 rule)
9. Sub-category Deep Dive
10. Ship Mode Analysis

Each analysis returns structured data + business insight text.

Author: Yao Jiahan
Date: 2026-07-21
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import (
    group_by, sum_by, avg_by, count_by,
    top_n, filter_rows, safe_float, pct_of_total,
    multi_group_by, describe_numeric
)
from collections import defaultdict


class EDAAnalyzer:
    """Executes all EDA analyses on Superstore data."""

    def __init__(self, data):
        self.data = data
        self.rows = data.rows
        self.results = {}

    def run_all(self) -> dict:
        """Execute all EDA analyses."""
        print("\n" + "=" * 60)
        print("  EXPLORATORY DATA ANALYSIS")
        print("=" * 60)

        analyses = [
            ('sales_overview', self.analyze_sales_overview),
            ('profit_analysis', self.analyze_profit),
            ('regional_analysis', self.analyze_region),
            ('category_analysis', self.analyze_category),
            ('subcategory_analysis', self.analyze_subcategory),
            ('segment_analysis', self.analyze_segment),
            ('discount_impact', self.analyze_discount_impact),
            ('top10_products', self.analyze_top10),
            ('loss_makers', self.analyze_loss_makers),
            ('pareto_analysis', self.analyze_pareto),
            ('ship_mode_analysis', self.analyze_ship_mode),
            ('margin_analysis', self.analyze_margin),
        ]

        for name, func in analyses:
            print(f"  → {name}...")
            self.results[name] = func()

        print("=" * 60)
        return self.results

    # ── Sales Overview ─────────────────────────────────────────────────
    def analyze_sales_overview(self) -> dict:
        """Overall sales KPIs and category breakdown."""
        sales = self.data.get_numeric('Sales')
        profit = self.data.get_numeric('Profit')
        quantity = self.data.get_numeric('Quantity')

        total_sales = sum(sales)
        total_profit = sum(profit)
        total_qty = int(sum(quantity))
        total_orders = len(self.rows)

        # Sales by Category
        sales_by_cat = sum_by(self.rows, 'Category', 'Sales')
        profit_by_cat = sum_by(self.rows, 'Category', 'Profit')

        # Sales by Region
        sales_by_region = sum_by(self.rows, 'Region', 'Sales')

        return {
            'total_sales': round(total_sales, 2),
            'total_profit': round(total_profit, 2),
            'total_quantity': total_qty,
            'total_orders': total_orders,
            'avg_order_value': round(total_sales / total_orders, 2) if total_orders else 0,
            'profit_margin': round(total_profit / total_sales * 100, 2) if total_sales else 0,
            'sales_by_category': sales_by_cat,
            'profit_by_category': profit_by_cat,
            'sales_by_region': sales_by_region,
        }

    # ── Profit Analysis ────────────────────────────────────────────────
    def analyze_profit(self) -> dict:
        """Detailed profit analysis: distribution, loss ratio, by dimension."""
        total = len(self.rows)
        profits = self.data.get_numeric('Profit')
        total_profit = sum(profits)

        # Loss ratio
        loss_count = sum(1 for p in profits if p < 0)
        loss_ratio = pct_of_total(loss_count, total)

        # Profit by Region & Category
        profit_by_region_cat = multi_group_by(self.rows,
                                              ['Region', 'Category'], 'Profit', 'sum')

        # Profit distribution stats
        profit_stats = describe_numeric(self.rows, 'Profit')

        return {
            'total_profit': round(total_profit, 2),
            'loss_count': loss_count,
            'loss_ratio': loss_ratio,
            'loss_amount': round(sum(p for p in profits if p < 0), 2),
            'profit_stats': profit_stats,
            'profit_by_region_category': profit_by_region_cat,
        }

    # ── Regional Analysis ──────────────────────────────────────────────
    def analyze_region(self) -> dict:
        """Sales and profit performance by region."""
        sales_by_region = sum_by(self.rows, 'Region', 'Sales')
        profit_by_region = sum_by(self.rows, 'Region', 'Profit')
        orders_by_region = count_by(self.rows, 'Region')

        # Profit margin per region
        margin_by_region = {}
        for region in sales_by_region:
            s = sales_by_region[region]
            p = profit_by_region.get(region, 0)
            margin_by_region[region] = round(p / s * 100, 2) if s else 0

        # Top/Bottom states
        sales_by_state = sum_by(self.rows, 'State', 'Sales')
        profit_by_state = sum_by(self.rows, 'State', 'Profit')

        return {
            'sales_by_region': sales_by_region,
            'profit_by_region': profit_by_region,
            'orders_by_region': orders_by_region,
            'margin_by_region': margin_by_region,
            'sales_by_state': sales_by_state,
            'profit_by_state': profit_by_state,
        }

    # ── Category Analysis ──────────────────────────────────────────────
    def analyze_category(self) -> dict:
        """Category-level performance: sales, profit, margin."""
        sales_by_cat = sum_by(self.rows, 'Category', 'Sales')
        profit_by_cat = sum_by(self.rows, 'Category', 'Profit')
        qty_by_cat = sum_by(self.rows, 'Category', 'Quantity')

        margin_by_cat = {}
        for cat in sales_by_cat:
            s = sales_by_cat[cat]
            p = profit_by_cat.get(cat, 0)
            margin_by_cat[cat] = round(p / s * 100, 2) if s else 0

        return {
            'sales_by_category': sales_by_cat,
            'profit_by_category': profit_by_cat,
            'quantity_by_category': qty_by_cat,
            'margin_by_category': margin_by_cat,
        }

    # ── Sub-Category Analysis ──────────────────────────────────────────
    def analyze_subcategory(self) -> dict:
        """Sub-category performance (17 sub-categories)."""
        sales_by_sub = sum_by(self.rows, 'Sub-Category', 'Sales')
        profit_by_sub = sum_by(self.rows, 'Sub-Category', 'Profit')
        qty_by_sub = sum_by(self.rows, 'Sub-Category', 'Quantity')

        # Margin per sub-category
        margin_by_sub = {}
        for sub in sales_by_sub:
            s = sales_by_sub[sub]
            p = profit_by_sub.get(sub, 0)
            margin_by_sub[sub] = round(p / s * 100, 2) if s else 0

        return {
            'sales_by_subcategory': sales_by_sub,
            'profit_by_subcategory': profit_by_sub,
            'quantity_by_subcategory': qty_by_sub,
            'margin_by_subcategory': margin_by_sub,
        }

    # ── Segment Analysis ───────────────────────────────────────────────
    def analyze_segment(self) -> dict:
        """Customer segment performance: Consumer, Corporate, Home Office."""
        sales_by_seg = sum_by(self.rows, 'Segment', 'Sales')
        profit_by_seg = sum_by(self.rows, 'Segment', 'Profit')
        orders_by_seg = count_by(self.rows, 'Segment')

        # Avg order value per segment
        avg_order = {}
        for seg in sales_by_seg:
            avg_order[seg] = round(sales_by_seg[seg] / orders_by_seg.get(seg, 1), 2)

        # Segment × Category
        seg_cat = multi_group_by(self.rows, ['Segment', 'Category'], 'Sales')

        return {
            'sales_by_segment': sales_by_seg,
            'profit_by_segment': profit_by_seg,
            'orders_by_segment': orders_by_seg,
            'avg_order_value': avg_order,
            'segment_category_sales': seg_cat,
        }

    # ── Discount Impact ────────────────────────────────────────────────
    def analyze_discount_impact(self) -> dict:
        """Analyze how discount level affects profit margin."""
        # Group by discount ranges
        discount_bins = {
            'No Discount (0%)': [],
            'Low (1-20%)': [],
            'Medium (21-40%)': [],
            'High (41-60%)': [],
            'Very High (60%+)': [],
        }

        for row in self.rows:
            d = safe_float(row.get('Discount', 0))
            if d == 0:
                discount_bins['No Discount (0%)'].append(row)
            elif d <= 0.2:
                discount_bins['Low (1-20%)'].append(row)
            elif d <= 0.4:
                discount_bins['Medium (21-40%)'].append(row)
            elif d <= 0.6:
                discount_bins['High (41-60%)'].append(row)
            else:
                discount_bins['Very High (60%+)'].append(row)

        impact = {}
        for bin_name, bin_rows in discount_bins.items():
            n = len(bin_rows)
            if n == 0:
                impact[bin_name] = {'count': 0, 'total_sales': 0,
                                    'total_profit': 0, 'margin': 0}
                continue
            sales = sum(safe_float(r['Sales']) for r in bin_rows)
            profit = sum(safe_float(r['Profit']) for r in bin_rows)
            impact[bin_name] = {
                'count': n,
                'total_sales': round(sales, 2),
                'total_profit': round(profit, 2),
                'margin': round(profit / sales * 100, 2) if sales else 0,
            }

        # Discount by category
        disc_by_cat = {}
        for cat in ['Furniture', 'Office Supplies', 'Technology']:
            cat_rows = filter_rows(self.rows, Category=cat)
            discounts = [safe_float(r['Discount']) for r in cat_rows]
            disc_by_cat[cat] = round(sum(discounts) / len(discounts) * 100, 1) if discounts else 0

        return {
            'discount_bins': impact,
            'avg_discount_by_category': disc_by_cat,
        }

    # ── Top 10 Products by Sales ──────────────────────────────────────
    def analyze_top10(self) -> dict:
        """Top 10 sub-categories by sales and profit."""
        top_sales = top_n(self.rows, 'Sub-Category', 'Sales', 10)
        top_profit = top_n(self.rows, 'Sub-Category', 'Profit', 10)
        top_qty = top_n(self.rows, 'Sub-Category', 'Quantity', 10)

        return {
            'top10_sales': top_sales,
            'top10_profit': top_profit,
            'top10_quantity': top_qty,
        }

    # ── Loss-Making Products ──────────────────────────────────────────
    def analyze_loss_makers(self) -> dict:
        """Identify loss-making sub-categories and analyze why."""
        # Loss by sub-category
        loss_by_sub = defaultdict(float)
        loss_count_by_sub = defaultdict(int)

        for row in self.rows:
            profit = safe_float(row.get('Profit', 0))
            if profit < 0:
                sub = row.get('Sub-Category', 'Unknown')
                loss_by_sub[sub] += profit
                loss_count_by_sub[sub] += 1

        sorted_losses = sorted(loss_by_sub.items(), key=lambda x: x[1])

        # Loss transactions with high discount as key driver
        loss_rows = [r for r in self.rows if safe_float(r.get('Profit', 0)) < 0]
        loss_with_high_disc = len([r for r in loss_rows
                                    if safe_float(r.get('Discount', 0)) >= 0.4])

        return {
            'loss_by_subcategory': dict(sorted_losses),
            'total_loss_amount': round(sum(v for v in loss_by_sub.values()), 2),
            'loss_transaction_count': len(loss_rows),
            'loss_with_high_discount': loss_with_high_disc,
            'loss_high_discount_pct': pct_of_total(loss_with_high_disc, len(loss_rows)),
        }

    # ── Pareto Analysis (80/20) ───────────────────────────────────────
    def analyze_pareto(self) -> dict:
        """Pareto analysis: does 20% of sub-categories drive 80% of sales?"""
        sales_by_sub = sorted(sum_by(self.rows, 'Sub-Category', 'Sales').items(),
                              key=lambda x: x[1], reverse=True)
        total_sales = sum(v for _, v in sales_by_sub)

        cumulative = []
        cum = 0
        for i, (sub, sales) in enumerate(sales_by_sub, 1):
            cum += sales
            cumulative.append({
                'rank': i,
                'sub_category': sub,
                'sales': round(sales, 2),
                'cum_pct': round(cum / total_sales * 100, 1),
                'pct_of_total': round(sales / total_sales * 100, 1),
            })

        # Find how many items make up 80%
        items_for_80 = 0
        cum_check = 0
        for item in cumulative:
            cum_check = item['cum_pct']
            items_for_80 += 1
            if cum_check >= 80:
                break

        total_items = len(sales_by_sub)
        return {
            'pareto_data': cumulative,
            'items_for_80pct': items_for_80,
            'total_items': total_items,
            'pct_items_for_80': round(items_for_80 / total_items * 100, 1),
            'total_sales': round(total_sales, 2),
        }

    # ── Ship Mode Analysis ────────────────────────────────────────────
    def analyze_ship_mode(self) -> dict:
        """Sales and profit by shipping mode."""
        sales_by_mode = sum_by(self.rows, 'Ship Mode', 'Sales')
        profit_by_mode = sum_by(self.rows, 'Ship Mode', 'Profit')
        orders_by_mode = count_by(self.rows, 'Ship Mode')

        # Avg order value per mode
        avg_by_mode = {}
        for mode in sales_by_mode:
            n = orders_by_mode.get(mode, 1)
            avg_by_mode[mode] = round(sales_by_mode[mode] / n, 2)

        return {
            'sales_by_ship_mode': sales_by_mode,
            'profit_by_ship_mode': profit_by_mode,
            'orders_by_ship_mode': orders_by_mode,
            'avg_order_by_ship_mode': avg_by_mode,
        }

    # ── Profit Margin Analysis ────────────────────────────────────────
    def analyze_margin(self) -> dict:
        """Deep dive on profit margins across dimensions."""
        # Margin by Region
        margin_by_region = {}
        for region in ['West', 'East', 'Central', 'South']:
            region_rows = filter_rows(self.rows, Region=region)
            sales = sum(safe_float(r['Sales']) for r in region_rows)
            profit = sum(safe_float(r['Profit']) for r in region_rows)
            margin_by_region[region] = round(profit / sales * 100, 2) if sales else 0

        # Margin by Sub-Category (sorted worst to best)
        margin_by_sub = {}
        for sub in set(r['Sub-Category'] for r in self.rows):
            sub_rows = filter_rows(self.rows, **{'Sub-Category': sub})
            sales = sum(safe_float(r['Sales']) for r in sub_rows)
            profit = sum(safe_float(r['Profit']) for r in sub_rows)
            margin_by_sub[sub] = round(profit / sales * 100, 2) if sales else 0

        sorted_margins = sorted(margin_by_sub.items(), key=lambda x: x[1])

        return {
            'margin_by_region': margin_by_region,
            'margin_by_subcategory': dict(sorted_margins),
            'best_margin_sub': sorted_margins[-1] if sorted_margins else ('', 0),
            'worst_margin_sub': sorted_margins[0] if sorted_margins else ('', 0),
        }
