"""
main.py — Retail Profit Optimization System Pipeline
=====================================================
AI 驱动的零售利润优化决策系统。
分析管道：加载 → 质量 → EDA → 洞察 → 下钻诊断 → 可视化

Usage:
    python main.py              # Run full pipeline (20 analysis dimensions)
    python main.py --export     # Also export 18 charts as HTML

Author: Yao Jiahan
Date: 2026-07-22
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
from src.drilldown import run_all_drilldowns
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
    import plotly.io as pio
    pio.json.config.default_engine = 'json'  # Fix for Python 3.14 / orjson compat
    
    path = os.path.join(IMAGES_DIR, f'{name}.html')
    html = fig.to_html(include_plotlyjs='cdn', full_html=True)
    # Fix Plotly template bug: {{responsive: true}} → {responsive: true}
    html = html.replace('{{responsive: true}}', '{responsive: true}')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
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

    # ── Step 5: Multi-Dimensional Drill-Down ─────────────────────────────
    print("\n" + "─" * 70)
    print("  STEP 5: MULTI-DIMENSIONAL DRILL-DOWN (CEO Diagnostic)")
    print("─" * 70)
    drilldown_results = run_all_drilldowns(data)

    # ── Step 6: Generate Visualizations ────────────────────────────────
    print("\n" + "─" * 70)
    print("  STEP 6: GENERATING VISUALIZATIONS")
    print("─" * 70)

    charts = generate_all_charts(eda_results, drilldown_results, data)

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
    print(f"  Drill-Downs:    8 dimensions")
    print("█" * 70 + "\n")

    return {
        'data': data,
        'quality': quality_report,
        'eda': eda_results,
        'insights': all_insights,
        'drilldown': drilldown_results,
        'charts': charts,
    }


def generate_all_charts(eda: dict, drill: dict, data) -> dict:
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
            title='品类销售分布'
        )

    # 2. Profit by Category (Waterfall)
    profit_by_cat = so.get('profit_by_category', {})
    if profit_by_cat:
        charts['02_profit_waterfall'] = create_profit_waterfall(
            labels=list(profit_by_cat.keys()),
            values=list(profit_by_cat.values()),
            title='品类利润贡献'
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
            title='品类表现：销售额 vs 利润率',
            yaxis_title='金额 ($)'
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
            title='子品类销售额排名',
            xaxis_title='总销售额 ($)'
        )

    # 5. Profit by Sub-Category (Horizontal Bar)
    profit_by_sub = sca.get('profit_by_subcategory', {})
    if profit_by_sub:
        sorted_profits = sorted(profit_by_sub.items(), key=lambda x: x[1], reverse=True)
        charts['05_subcategory_profit'] = create_hbar(
            labels=[s for s, _ in sorted_profits],
            values=[v for _, v in sorted_profits],
            title='子品类利润排名',
            xaxis_title='总利润 ($)',
            color=COLORS['accent']
        )

    # 6. Regional Performance (Dual-axis)
    sales_region = ra.get('sales_by_region', {})
    profit_region = ra.get('profit_by_region', {})
    if sales_region:
        charts['06_regional_performance'] = create_region_chart(
            region_sales=sales_region,
            region_profit=profit_region,
            title='区域表现：销售额 + 利润率'
        )

    # 7. Segment Donut Chart
    sales_seg = seg.get('sales_by_segment', {})
    if sales_seg:
        charts['07_segment_donut'] = create_donut(
            labels=list(sales_seg.keys()),
            values=list(sales_seg.values()),
            title='客户细分销售分布'
        )

    # 8. Discount Impact
    disc_bins = di.get('discount_bins', {})
    if disc_bins:
        bin_names = list(disc_bins.keys())
        margins = [disc_bins[b]['margin'] for b in bin_names]
        charts['08_discount_impact'] = create_vbar(
            labels=bin_names,
            values=margins,
            title='折扣力度 vs 利润率',
            yaxis_title='利润率 (%)',
            color=COLORS['danger']
        )

    # 9. Pareto Chart
    pareto_data = pareto.get('pareto_data', [])
    if pareto_data:
        charts['09_pareto'] = create_pareto(
            data=pareto_data,
            title='帕累托分析：销售集中度（80/20 法则）'
        )

    # 10. Loss-Making Sub-Categories
    loss_data = eda.get('loss_makers', {}).get('loss_by_subcategory', {})
    if loss_data:
        sorted_loss = sorted(loss_data.items(), key=lambda x: x[1])
        charts['10_loss_makers'] = create_hbar(
            labels=[s for s, _ in sorted_loss],
            values=[v for _, v in sorted_loss],
            title='亏损子品类（表现最差）',
            xaxis_title='总亏损 ($)',
            color=COLORS['danger']
        )

    # 11. Ship Mode Distribution
    ship_sales = sm.get('sales_by_ship_mode', {})
    if ship_sales:
        charts['11_ship_mode'] = create_donut(
            labels=list(ship_sales.keys()),
            values=list(ship_sales.values()),
            title='物流方式销售分布'
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
        title='折扣率 vs 利润（每点 = 一笔交易）',
        xaxis_title='折扣率',
        yaxis_title='利润 ($)',
        color_values=d_sample,
        color_label='Discount',
        size_values=[max(3, min(20, abs(p) / 50)) for p in p_sample],
    )
    
    # ═══════════════════════════════════════════════════════════════════════
    # 下钻分析图表 (13-18)
    # ═══════════════════════════════════════════════════════════════════════
    
    # 13. 品类 × 折扣 利润热力图
    cat_disc = drill.get('category_discount', {})
    if cat_disc.get('raw_matrix'):
        cats = cat_disc['categories']
        bins = cat_disc['bins']
        headers = ['品类\\折扣段'] + bins
        cells = []
        for cat in cats:
            row = [cat]
            for b in bins:
                key = (cat, b)
                val = cat_disc['raw_matrix'].get(key, {})
                margin = val.get('margin', 0)
                row.append(f"{margin}%")
            cells.append(row)
        # 转置为 plotly table 格式
        table_cells = [headers]
        for i in range(len(bins) + 1):
            col = [cells[j][i] for j in range(len(cats))]
            table_cells.append(col)
        
        # 用数值矩阵做热力表格
        matrix_values = []
        for cat in cats:
            row_vals = []
            for b in bins:
                key = (cat, b)
                val = cat_disc['raw_matrix'].get(key, {})
                row_vals.append(val.get('margin', 0))
            matrix_values.append(row_vals)
        
        charts['13_category_discount_heatmap'] = create_heatmap_table(
            headers=['品类'] + bins,
            cells=[
                [cats[i] for i in range(len(cats))],  # col 0: 品类名
                *[[matrix_values[i][j] for i in range(len(cats))] for j in range(len(bins))]
            ],
            title='品类 × 折扣段 利润率矩阵 (%)'
        )
    
    # 14. 子品类 × 区域 亏损 Top 10
    sub_region = drill.get('subcategory_region', {})
    worst_combo = sub_region.get('worst_combinations', [])
    if worst_combo:
        labels_14 = [f"{w['sub_category']} · {w['region']}" for w in worst_combo]
        values_14 = [abs(w['profit']) for w in worst_combo]
        charts['14_subcategory_region_loss'] = create_hbar(
            labels=labels_14,
            values=values_14,
            title='子品类 × 区域 亏损 Top 10（问题定位）',
            xaxis_title='亏损金额 ($)',
            color=COLORS['danger']
        )
    
    # 15. 客群 × 折扣 利润对比
    seg_disc = drill.get('segment_discount', {})
    if seg_disc.get('raw_matrix'):
        segments = seg_disc['segments']
        disc_bins = seg_disc['bins']
        series = {}
        for seg in segments:
            margins = []
            for b in disc_bins:
                k = seg + '|' + b
                margins.append(seg_disc['raw_matrix'].get(k, {}).get('margin', 0))
            series[seg] = margins
        charts['15_segment_discount'] = create_grouped_bar(
            categories=disc_bins,
            series=series,
            title='客群 × 折扣段 利润率对比',
            yaxis_title='利润率 (%)'
        )
    
    # 16. 永不打折清单
    never = drill.get('subcategory_discount', {}).get('never_discount', [])
    if never:
        table_headers = ['子品类', '严重度', '折扣段', '利润率', '交易数']
        table_rows = [[], [], [], [], []]
        for item in never:
            for alert in item['alerts']:
                table_rows[0].append(item['sub_category'])
                table_rows[1].append(item['severity'])
                table_rows[2].append(alert['discount_bin'])
                table_rows[3].append(f"{alert['margin']}%")
                table_rows[4].append(str(alert['count']))
        charts['16_never_discount'] = create_heatmap_table(
            headers=table_headers,
            cells=table_rows,
            title='⚠️ 建议永不打折 / 严格管控清单'
        )
    
    # 17. 亏损品诊断面板
    diag = drill.get('loss_maker_diagnostics', {}).get('diagnostics', {})
    if diag:
        sub_names = list(diag.keys())
        loss_values = [abs(diag[s]['total_loss']) for s in sub_names]
        charts['17_loss_diagnostics'] = create_hbar(
            labels=sub_names,
            values=loss_values,
            title='Top 5 亏损品类诊断（点击下钻查看根因）',
            xaxis_title='亏损金额 ($)',
            color=COLORS['danger']
        )
    
    # 18. 折扣弹性曲线
    elas = drill.get('discount_elasticity', {}).get('data', [])
    if elas:
        disc_pcts = [e['discount_pct'] for e in elas]
        margins = [e['margin'] for e in elas]
        counts = [e['count'] for e in elas]
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        from src.visualizer import apply_template
        
        fig18 = make_subplots(specs=[[{'secondary_y': True}]])
        fig18.add_trace(go.Bar(
            x=disc_pcts, y=counts, name='订单量',
            marker_color=COLORS['secondary'], opacity=0.6
        ), secondary_y=False)
        fig18.add_trace(go.Scatter(
            x=disc_pcts, y=margins, name='利润率 %',
            mode='lines+markers', line={'color': COLORS['danger'], 'width': 3},
            marker={'size': 8}
        ), secondary_y=True)
        fig18.add_hline(y=0, line_dash='dash', line_color=COLORS['neutral'],
                        annotation_text='盈亏平衡线', secondary_y=True)
        fig18.update_layout(
            title={'text': '折扣弹性分析：利润率 vs 订单量', 'x': 0, 'font': {'size': 18, 'color': COLORS['primary']}},
            height=450, showlegend=True,
            legend={'orientation': 'h', 'y': 1.05}
        )
        fig18.update_xaxes(title_text='折扣率 (%)')
        fig18.update_yaxes(title_text='订单量', secondary_y=False)
        fig18.update_yaxes(title_text='利润率 (%)', secondary_y=True)
        charts['18_discount_elasticity'] = apply_template(fig18)
    
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
