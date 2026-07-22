"""
visualizer.py — Plotly Visualization Engine
===========================================
Generates publication-quality Plotly charts for the Superstore analysis.
All charts use a consistent McKinsey-inspired corporate color palette.

Chart types:
- KPI indicator cards (text-based)
- Bar charts (horizontal & vertical)
- Treemap
- Waterfall chart
- Pareto chart (bar + line combo)
- Scatter plots
- Donut/pie charts
- Heatmap (text table)

Each function returns a Plotly Figure object.

Author: Yao Jiahan
Date: 2026-07-21
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import plotly.graph_objects as go
# Note: plotly.express requires numpy; we use pure plotly.graph_objects instead
from plotly.subplots import make_subplots
from config.settings import COLORS, PLOTLY_TEMPLATE

# ── Color shortcuts ────────────────────────────────────────────────────────
C = COLORS
PALETTE = C['palette']


def apply_template(fig: go.Figure) -> go.Figure:
    """Apply consistent corporate styling to a figure."""
    fig.update_layout(
        font={'family': 'Segoe UI, Arial, sans-serif', 'color': C['dark']},
        plot_bgcolor=C['white'],
        paper_bgcolor=C['white'],
        margin={'l': 60, 'r': 30, 't': 60, 'b': 50},
        title={'font': {'size': 18, 'color': C['primary']}},
        xaxis={
            'gridcolor': '#E5E7EB',
            'linecolor': '#D1D5DB',
            'title_font': {'color': C['neutral']},
        },
        yaxis={
            'gridcolor': '#E5E7EB',
            'linecolor': '#D1D5DB',
            'title_font': {'color': C['neutral']},
        },
        legend={'font': {'color': C['neutral']}},
        hoverlabel={'font': {'family': 'Segoe UI, Arial, sans-serif'}},
    )
    return fig


# ── KPI Cards ─────────────────────────────────────────────────────────────
def create_kpi_cards(kpis: dict) -> go.Figure:
    """Create KPI summary cards as a subplot."""
    n = len(kpis)
    cols = min(n, 5)
    rows = (n + cols - 1) // cols

    fig = make_subplots(
        rows=rows, cols=cols,
        subplot_titles=list(kpis.keys()),
        specs=[[{'type': 'indicator'} for _ in range(cols)] for _ in range(rows)]
    )

    # Actually use annotations for KPI cards
    fig = go.Figure()
    for i, (label, value) in enumerate(kpis.items()):
        fig.add_trace(go.Indicator(
            mode='number',
            value=value if isinstance(value, (int, float)) else 0,
            title={'text': label, 'font': {'size': 12, 'color': C['neutral']}},
            number={'font': {'size': 32, 'color': C['primary']},
                    'prefix': '$' if 'Sales' in label or 'Profit' in label or 'Value' in label else '',
                    'valueformat': ',.0f' if isinstance(value, (int, float)) and value > 100 else '.2f'},
            domain={'row': 0, 'column': i}
        ))

    fig.update_layout(
        grid={'rows': 1, 'columns': n, 'pattern': 'independent'},
        height=160,
        margin={'l': 20, 'r': 20, 't': 40, 'b': 20},
    )
    return apply_template(fig)


# ── Horizontal Bar Chart ──────────────────────────────────────────────────
def create_hbar(labels: list, values: list, title: str = '',
                xaxis_title: str = '', color: str = None,
                sort: bool = True) -> go.Figure:
    """Create a horizontal bar chart."""
    if sort:
        pairs = sorted(zip(values, labels), reverse=True)
        values, labels = zip(*pairs) if pairs else ([], [])
        values, labels = list(values), list(labels)

    colors_used = [color or PALETTE[i % len(PALETTE)] for i in range(len(labels))]

    fig = go.Figure(go.Bar(
        y=labels,
        x=values,
        orientation='h',
        marker={'color': colors_used,
                'line': {'width': 0}},
        text=[f'${v:,.0f}' if abs(v) > 1 else f'{v:.1f}%' for v in values],
        textposition='outside',
        textfont={'color': C['dark'], 'size': 11},
        hovertemplate='%{y}: %{x:$,.2f}<extra></extra>',
    ))

    fig.update_layout(
        title={'text': title, 'x': 0},
        xaxis_title=xaxis_title,
        yaxis={'autorange': 'reversed'},
        height=max(400, len(labels) * 35),
        showlegend=False,
    )
    return apply_template(fig)


# ── Vertical Bar Chart ────────────────────────────────────────────────────
def create_vbar(labels: list, values: list, title: str = '',
                yaxis_title: str = '', color: str = None) -> go.Figure:
    """Create a vertical bar chart."""
    colors_used = [color or PALETTE[i % len(PALETTE)] for i in range(len(labels))]

    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker={'color': colors_used, 'line': {'width': 0}},
        text=[f'${v:,.0f}' if abs(v) > 1 else f'{v:.1f}' for v in values],
        textposition='outside',
        textfont={'color': C['dark'], 'size': 11},
        hovertemplate='%{x}: %{y:$,.2f}<extra></extra>',
    ))

    fig.update_layout(
        title={'text': title, 'x': 0},
        yaxis_title=yaxis_title,
        height=450,
        showlegend=False,
    )
    return apply_template(fig)


# ── Grouped Bar Chart ─────────────────────────────────────────────────────
def create_grouped_bar(categories: list, series: dict, title: str = '',
                       yaxis_title: str = '') -> go.Figure:
    """Create a grouped bar chart with multiple series."""
    fig = go.Figure()

    for i, (name, values) in enumerate(series.items()):
        fig.add_trace(go.Bar(
            x=categories,
            y=values,
            name=name,
            marker={'color': PALETTE[i % len(PALETTE)]},
            text=[f'${v:,.0f}' if abs(v) > 1 else f'{v:.1f}' for v in values],
            textposition='outside',
            textfont={'size': 10},
        ))

    fig.update_layout(
        title={'text': title, 'x': 0},
        yaxis_title=yaxis_title,
        barmode='group',
        height=450,
        legend={'orientation': 'h', 'yanchor': 'bottom', 'y': 1.02},
    )
    return apply_template(fig)


# ── Treemap ───────────────────────────────────────────────────────────────
def create_treemap(labels: list, parents: list, values: list,
                   title: str = '') -> go.Figure:
    """Create a treemap visualization."""
    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        textinfo='label+value+percent parent',
        hovertemplate='%{label}<br>Sales: $%{value:,.0f}<br>Share: %{percentParent:.1%}<extra></extra>',
        marker={'colors': PALETTE[:len(set(parents))] * 10},
        branchvalues='total',
    ))

    fig.update_layout(
        title={'text': title, 'x': 0},
        height=500,
        margin={'l': 10, 'r': 10, 't': 50, 'b': 10},
    )
    return apply_template(fig)


# ── Pareto Chart (Bar + Line) ─────────────────────────────────────────────
def create_pareto(data: list[dict], title: str = 'Pareto Analysis') -> go.Figure:
    """Create a Pareto chart with bars (individual) and line (cumulative)."""
    sub_cats = [d['sub_category'] for d in data]
    sales = [d['sales'] for d in data]
    cum_pcts = [d['cum_pct'] for d in data]

    fig = make_subplots(specs=[[{'secondary_y': True}]])

    fig.add_trace(go.Bar(
        x=sub_cats, y=sales, name='Sales',
        marker={'color': C['primary'], 'opacity': 0.8},
        hovertemplate='%{x}: $%{y:,.0f}<extra></extra>',
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=sub_cats, y=cum_pcts, name='Cumulative %',
        mode='lines+markers',
        line={'color': C['danger'], 'width': 3},
        marker={'size': 6, 'color': C['danger']},
        hovertemplate='%{x}: %{y:.1f}%<extra></extra>',
    ), secondary_y=True)

    # 80% reference line
    fig.add_hline(y=80, line_dash='dash', line_color=C['accent'],
                  annotation_text='80% Target',
                  annotation_position='bottom right',
                  secondary_y=True)

    fig.update_layout(
        title={'text': title, 'x': 0},
        height=500,
        showlegend=True,
        legend={'orientation': 'h', 'y': 1.05},
    )
    fig.update_yaxes(title_text='Sales ($)', secondary_y=False)
    fig.update_yaxes(title_text='Cumulative %', secondary_y=True, range=[0, 105])
    return apply_template(fig)


# ── Donut Chart ───────────────────────────────────────────────────────────
def create_donut(labels: list, values: list, title: str = '',
                 hole: float = 0.5) -> go.Figure:
    """Create a donut/pie chart."""
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=hole,
        marker={'colors': PALETTE[:len(labels)]},
        textinfo='label+percent',
        hovertemplate='%{label}: $%{value:,.0f} (%{percent})<extra></extra>',
        textfont={'size': 12},
    ))

    fig.update_layout(
        title={'text': title, 'x': 0},
        height=450,
        showlegend=True,
    )
    return apply_template(fig)


# ── Scatter Plot ──────────────────────────────────────────────────────────
def create_scatter(x: list, y: list, title: str = '',
                   xaxis_title: str = '', yaxis_title: str = '',
                   color_values: list = None, color_label: str = '',
                   size_values: list = None, size_label: str = '') -> go.Figure:
    """Create a scatter plot, optionally with color and size dimensions."""
    fig = go.Figure(go.Scatter(
        x=x, y=y,
        mode='markers',
        marker={
            'size': size_values or 8,
            'color': color_values or C['secondary'],
            'colorscale': [[0, C['danger']], [0.5, C['warning']], [1, C['accent']]],
            'showscale': color_values is not None,
            'colorbar': {'title': color_label} if color_label else None,
            'opacity': 0.6,
            'line': {'width': 0.5, 'color': C['dark']},
        },
        text=[f'{x[i]:.1f}, {y[i]:.1f}' for i in range(len(x))],
        hovertemplate=f'%{{text}}<extra></extra>',
    ))

    fig.update_layout(
        title={'text': title, 'x': 0},
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        height=450,
    )
    return apply_template(fig)


# ── Heatmap-style Table ──────────────────────────────────────────────────
def create_heatmap_table(headers: list, cells: list[list],
                         title: str = '',
                         col_colors: list = None) -> go.Figure:
    """Create a styled table with conditional formatting."""
    if col_colors is None:
        col_colors = [C['primary']] * len(headers)

    fill_colors = []
    for col_idx, col_data in enumerate(cells):
        col_fills = []
        for val in col_data:
            if isinstance(val, (int, float)) and val < 0:
                col_fills.append('#FEE2E2')  # Light red
            elif isinstance(val, (int, float)) and val > 1000:
                col_fills.append('#D1FAE5')  # Light green
            else:
                col_fills.append(C['white'])
        fill_colors.append(col_fills)

    fig = go.Figure(go.Table(
        header={
            'values': headers,
            'fill_color': C['primary'],
            'font': {'color': C['white'], 'size': 12},
            'align': 'center',
            'height': 35,
        },
        cells={
            'values': cells,
            'fill_color': fill_colors,
            'font': {'color': C['dark'], 'size': 11},
            'align': 'center',
            'height': 30,
            'format': [[',.2f' if isinstance(v, float) else '' for v in col] for col in cells],
        }
    ))

    fig.update_layout(
        title={'text': title, 'x': 0},
        height=300 + len(cells[0]) * 30 if cells else 400,
    )
    return apply_template(fig)


# ── Waterfall / Profit by Category ────────────────────────────────────────
def create_profit_waterfall(labels: list, values: list,
                            title: str = 'Profit Breakdown') -> go.Figure:
    """Create a waterfall chart for profit breakdown."""
    # Color based on positive/negative
    colors = [C['accent'] if v >= 0 else C['danger'] for v in values]

    fig = go.Figure(go.Waterfall(
        name='Profit',
        orientation='v',
        x=labels,
        y=values,
        text=[f'${v:,.0f}' for v in values],
        textposition='outside',
        connector={'line': {'color': C['neutral'], 'width': 1, 'dash': 'dot'}},
        increasing={'marker': {'color': C['accent']}},
        decreasing={'marker': {'color': C['danger']}},
    ))

    fig.update_layout(
        title={'text': title, 'x': 0},
        yaxis_title='Profit ($)',
        height=450,
        showlegend=False,
    )
    return apply_template(fig)


# ── Region Map (simplified) ───────────────────────────────────────────────
def create_region_chart(region_sales: dict, region_profit: dict,
                        title: str = 'Regional Performance') -> go.Figure:
    """Create a dual-axis chart showing sales and profit margin by region."""
    regions = list(region_sales.keys())
    sales_vals = [region_sales[r] for r in regions]
    margins = [round(region_profit.get(r, 0) / region_sales[r] * 100, 1)
               if region_sales.get(r, 0) else 0 for r in regions]

    fig = make_subplots(specs=[[{'secondary_y': True}]])

    fig.add_trace(go.Bar(
        x=regions, y=sales_vals, name='Sales',
        marker={'color': C['secondary'], 'opacity': 0.8},
        text=[f'${v:,.0f}' for v in sales_vals],
        textposition='outside',
        textfont={'size': 11},
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=regions, y=margins, name='Profit Margin %',
        mode='lines+markers',
        line={'color': C['accent'], 'width': 3},
        marker={'size': 10, 'color': [C['accent'] if m >= 0 else C['danger'] for m in margins]},
        text=[f'{m:.1f}%' for m in margins],
        textposition='top center',
    ), secondary_y=True)

    fig.update_layout(
        title={'text': title, 'x': 0},
        height=450,
        legend={'orientation': 'h', 'y': 1.05},
    )
    fig.update_yaxes(title_text='Sales ($)', secondary_y=False)
    fig.update_yaxes(title_text='Profit Margin (%)', secondary_y=True)
    return apply_template(fig)
