"""
main.py — Superstore Business Analysis Pipeline
===============================================
Master orchestrator that runs the complete analysis pipeline:
1. Load Data → 2. Quality Check → 3. EDA → 4. Insights → 5. Visualizations

Usage:
    python main.py              # Run full pipeline
    python main.py --export     # Also export charts as HTML

Author: Yao Jiahan
Date: 2026-07-21
"""

import os
import sys
import json
import argparse

# Ensure project root is in path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from src.data_loader import SuperstoreData
from src.data_quality import DataQualityReport
from src.eda import EDAAnalyzer
from src.insights import BusinessInsights
from src.visualizer import (
    create_hbar, create_vbar, create_donut, create_treemap,
    create_pareto, create_scatter, create_grouped_bar,
    create_profit_waterfall, create_region_chart,
    create_heatmap_table
)
from config.settings import COLORS, IMAGES_DIR

# Ensure images directory exists
os.makedirs(IMAGES_DIR, exist_ok=True)


def fmt_dollar(val: float) -> str:
    """Format as dollar string."""
    if abs(val) >= 1e6:
        return f"${val/1e6:.2f}M"
    elif abs(val) >= 1e3:
        return f"${val/1e3:.1f}K"
    return f"${val:.2f}"


def export_chart(fig, name: str):
    """Export a Plotly figure as HTML for portfolio embedding."""
    path = os.path.join(IMAGES_DIR, f'{name}.html')
    fig.write_html(path, include_plotlyjs='cdn', full_html=True)
    print(f"    ✓ Exported: {path}")


def run_pipeline(export: bool = False):
    """Execute the complete analysis pipeline."""
    print("\n" + "█" * 70)
    print("█  SUPERSTORE BUSINESS ANALYSIS — COMPLETE PIPELINE")
    print("█" * 70)

    # ── Step 1: Load Data ──────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("  STEP 1: DATA LOADING")
    print("─" * 70)
    data = SuperstoreData().load()
    summary = data.summary()
    print(f"  ✓ Loaded {summary['rows']:,} rows × {summary['columns']} columns")
    print(f"  ✓ Columns: {', '.join(summary['column_names'])}")

    # ── Step 2: Data Quality ──────────────────────────────────────────
    print("\n" + "─" * 70)
    print("  STEP 2: DATA QUALITY ASSESSMENT")
    print("─" * 70)
    dq = DataQualityReport(data)
    quality_report = dq.run_all_checks()

    # ── Step 3: EDA ───────────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("  STEP 3: EXPLORATORY DATA ANALYSIS")
    print("─" * 70)
    eda = EDAAnalyzer(data)
    eda_results = eda.run_all()

    # ── Step 4: Business Insights ─────────────────────────────────────
    print("\n" + "─" * 70)
    print("  STEP 4: BUSINESS INSIGHT GENERATION")
    print("─" * 70)
    insights = BusinessInsights(eda_results)
    all_insights = insights.generate_all()
    insights.print_summary()

    # ── Step 5: Generate Visualizations ────────────────────────────────
    print("\n" + "─" * 70)
    print("  STEP 5: GENERATING VISUALIZATIONS")
    print("─" * 70)

    charts = generate_all_charts(eda_results, data)

    if export:
        for name, fig in charts.items():
            export_chart(fig, name)

    # ── Summary ───────────────────────────────────────────────────────
    print("\n" + "█" * 70)
    print("█  PIPELINE COMPLETE")
    print("█" * 70)
    so = eda_results.get('sales_overview', {})
    print(f"  Total Sales:    ${so.get('total_sales', 0):,.0f}")
    print(f"  Total Profit:   ${so.get('total_profit', 0):,.0f}")
    print(f"  Profit Margin:  {so.get('profit_margin', 0)}%")
    print(f"  Total Orders:   {so.get('total_orders', 0):,}")
    print(f"  Insights:       {len(all_insights)}")
    print(f"  Charts:         {len(charts)}")
    print("█" * 70 + "\n")

    return {
        'data': data,
        'quality': quality_report,
        'eda': eda_results,
        'insights': all_insights,
        'charts': charts,
    }


def generate_all_charts(eda: dict, data) -> dict:
    """Generate all Plotly charts for the analysis."""
    charts = {}
    so = eda.get('sales_overview', {})
    ca = eda.get('category_analysis', {})
    sca = eda.get('subcategory_analysis', {})
    ra = eda.get('regional_analysis', {})
    pa = eda.get('profit_analysis', {})
    di = eda.get('discount_impact', {})
    seg = eda.get('segment_analysis', {})
    pareto = eda.get('pareto_analysis', {})
    sm = eda.get('ship_mode_analysis', {})
    ma = eda.get('margin_analysis', {})

    # 1. Sales by Category (Treemap)
    sales_by_cat = so.get('sales_by_category', {})
    if sales_by_cat:
        cats_labels = list(sales_by_cat.keys())
        cats_values = list(sales_by_cat.values())
        charts['01_sales_treemap'] = create_treemap(
            labels=cats_labels,
            parents=['All Products'] * len(cats_labels),
            values=cats_values,
            title='Sales Distribution by Category'
        )

    # 2. Profit by Category (Waterfall)
    profit_by_cat = so.get('profit_by_category', {})
    if profit_by_cat:
        charts['02_profit_waterfall'] = create_profit_waterfall(
            labels=list(profit_by_cat.keys()),
            values=list(profit_by_cat.values()),
            title='Profit Contribution by Category'
        )

    # 3. Category Margin Comparison (Grouped Bar)
    sales_by_cat = ca.get('sales_by_category', {})
    margins_by_cat = ca.get('margin_by_category', {})
    if sales_by_cat and margins_by_cat:
        cats = list(sales_by_cat.keys())
        charts['03_category_comparison'] = create_grouped_bar(
            categories=cats,
            series={
                'Sales ($)': [sales_by_cat.get(c, 0) for c in cats],
            },
            title='Category Performance: Sales vs Profit',
            yaxis_title='Amount ($)'
        )

    # 4. Sales by Sub-Category (Horizontal Bar)
    sales_by_sub = sca.get('sales_by_subcategory', {})
    if sales_by_sub:
        sorted_subs = sorted(sales_by_sub.items(), key=lambda x: x[1], reverse=True)
        sub_labels = [s for s, _ in sorted_subs]
        sub_values = [v for _, v in sorted_subs]
        charts['04_subcategory_sales'] = create_hbar(
            labels=sub_labels,
            values=sub_values,
            title='Sales by Sub-Category',
            xaxis_title='Total Sales ($)'
        )

    # 5. Profit by Sub-Category (Horizontal Bar)
    profit_by_sub = sca.get('profit_by_subcategory', {})
    if profit_by_sub:
        sorted_profits = sorted(profit_by_sub.items(), key=lambda x: x[1], reverse=True)
        charts['05_subcategory_profit'] = create_hbar(
            labels=[s for s, _ in sorted_profits],
            values=[v for _, v in sorted_profits],
            title='Profit by Sub-Category',
            xaxis_title='Total Profit ($)',
            color=COLORS['accent']
        )

    # 6. Regional Performance (Dual-axis)
    sales_region = ra.get('sales_by_region', {})
    profit_region = ra.get('profit_by_region', {})
    if sales_region:
        charts['06_regional_performance'] = create_region_chart(
            region_sales=sales_region,
            region_profit=profit_region,
            title='Regional Performance: Sales & Profit Margin'
        )

    # 7. Segment Donut Chart
    sales_seg = seg.get('sales_by_segment', {})
    if sales_seg:
        charts['07_segment_donut'] = create_donut(
            labels=list(sales_seg.keys()),
            values=list(sales_seg.values()),
            title='Sales Distribution by Customer Segment'
        )

    # 8. Discount Impact
    disc_bins = di.get('discount_bins', {})
    if disc_bins:
        bin_names = list(disc_bins.keys())
        margins = [disc_bins[b]['margin'] for b in bin_names]
        charts['08_discount_impact'] = create_vbar(
            labels=bin_names,
            values=margins,
            title='Profit Margin by Discount Level',
            yaxis_title='Profit Margin (%)',
            color=COLORS['danger']
        )

    # 9. Pareto Chart
    pareto_data = pareto.get('pareto_data', [])
    if pareto_data:
        charts['09_pareto'] = create_pareto(
            data=pareto_data,
            title='Pareto Analysis: Sales Concentration (80/20 Rule)'
        )

    # 10. Loss-Making Sub-Categories
    loss_data = eda.get('loss_makers', {}).get('loss_by_subcategory', {})
    if loss_data:
        sorted_loss = sorted(loss_data.items(), key=lambda x: x[1])
        charts['10_loss_makers'] = create_hbar(
            labels=[s for s, _ in sorted_loss],
            values=[v for _, v in sorted_loss],
            title='Loss-Making Sub-Categories (Bottom Performers)',
            xaxis_title='Total Loss ($)',
            color=COLORS['danger']
        )

    # 11. Ship Mode Distribution
    ship_sales = sm.get('sales_by_ship_mode', {})
    if ship_sales:
        charts['11_ship_mode'] = create_donut(
            labels=list(ship_sales.keys()),
            values=list(ship_sales.values()),
            title='Sales Distribution by Shipping Mode'
        )

    # 12. Scatter: Discount vs Profit
    discounts = data.get_numeric('Discount')
    profits = data.get_numeric('Profit')
    sales = data.get_numeric('Sales')
    # Sample to avoid overcrowding
    sample_n = min(2000, len(discounts))
    step = max(1, len(discounts) // sample_n)
    d_sample = discounts[::step]
    p_sample = profits[::step]
    s_sample = sales[::step]

    charts['12_discount_vs_profit'] = create_scatter(
        x=d_sample,
        y=p_sample,
        title='Discount Rate vs Profit (Each dot = one transaction)',
        xaxis_title='Discount Rate',
        yaxis_title='Profit ($)',
        color_values=d_sample,
        color_label='Discount',
        size_values=[max(3, min(20, abs(p) / 50)) for p in p_sample],
    )

    print(f"  ✓ Generated {len(charts)} charts")
    return charts


# ── Main ──────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Superstore Business Analysis Pipeline')
    parser.add_argument('--export', action='store_true',
                        help='Export charts as HTML files')
    args = parser.parse_args()

    results = run_pipeline(export=args.export)
