"""
drilldown.py — Multi-Dimensional Profit Diagnostic Engine
==========================================================
从"描述性分析"升级为"诊断性分析"的核心模块。

回答 CEO 级问题：
- 哪个品类 × 哪个折扣段 × 哪个区域 在亏钱？
- 哪些产品应该被列入"永不打折"清单？
- 每个亏损品类的根因是什么？（折扣？区域？客群？）

所有分析复用现有 utils/helpers.py 的 multi_group_by / filter_rows。

Author: Yao Jiahan
Date: 2026-07-22
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collections import defaultdict
from utils.helpers import (
    multi_group_by, filter_rows, sum_by, count_by, avg_by
)


# ── 折扣分箱工具 ────────────────────────────────────────────────────────────
DISCOUNT_BINS = [
    ('无折扣 (0%)',        lambda d: d == 0),
    ('低折扣 (1-20%)',     lambda d: 0 < d <= 0.20),
    ('中折扣 (21-40%)',    lambda d: 0.20 < d <= 0.40),
    ('高折扣 (41-60%)',    lambda d: 0.40 < d <= 0.60),
    ('极高折扣 (>60%)',    lambda d: d > 0.60),
]

def _bin_discount(d: float) -> str:
    for name, fn in DISCOUNT_BINS:
        if fn(d):
            return name
    return '未知'


# ══════════════════════════════════════════════════════════════════════════════
# 分析 1：品类 × 折扣 利润热力图
# ══════════════════════════════════════════════════════════════════════════════
def analyze_category_discount(rows: list[dict]) -> dict:
    """返回 3(Category) × 5(Discount Bin) 的利润矩阵。

    Returns:
        {
            'matrix': {(category, discount_bin): {
                'sales': float, 'profit': float, 'margin': float,
                'count': int, 'loss_count': int, 'loss_rate': float
            }},
            'categories': ['Furniture', 'Office Supplies', 'Technology'],
            'bins': ['无折扣 (0%)', '低折扣 (1-20%)', ...],
            'summary': '关键发现：Furniture 在高折扣段 100% 亏损'
        }
    """
    # 按 Category + Discount Bin 做 2D 聚合
    profit_by_cat_bin = defaultdict(lambda: {'profit': 0.0, 'sales': 0.0, 'count': 0, 'loss_count': 0})
    
    for row in rows:
        cat = row['Category']
        disc = float(row['Discount'])
        profit = float(row['Profit'])
        sales = float(row['Sales'])
        bin_name = _bin_discount(disc)
        key = (cat, bin_name)
        
        profit_by_cat_bin[key]['profit'] += profit
        profit_by_cat_bin[key]['sales'] += sales
        profit_by_cat_bin[key]['count'] += 1
        if profit < 0:
            profit_by_cat_bin[key]['loss_count'] += 1
    
    # 计算 margin 和 loss_rate
    matrix = {}
    for key, vals in profit_by_cat_bin.items():
        vals['margin'] = round(vals['profit'] / vals['sales'] * 100, 1) if vals['sales'] else 0
        vals['loss_rate'] = round(vals['loss_count'] / vals['count'] * 100, 1) if vals['count'] else 0
        matrix[key] = vals
    
    categories = ['Furniture', 'Office Supplies', 'Technology']
    bins = [b[0] for b in DISCOUNT_BINS]
    
    # 生成关键发现
    findings = []
    for cat in categories:
        for b in bins:
            key = (cat, b)
            if key in matrix and matrix[key]['loss_rate'] >= 90:
                findings.append(f"{cat} 在「{b}」段亏损率 {matrix[key]['loss_rate']}%")
    
    return {
        'matrix': {str(k[0]) + '|' + k[1]: v for k, v in matrix.items()},
        'raw_matrix': matrix,
        'categories': categories,
        'bins': bins,
        'findings': findings,
        'summary': '；'.join(findings[:5]) if findings else '各品类折扣结构正常'
    }


# ══════════════════════════════════════════════════════════════════════════════
# 分析 2：子品类 × 区域 亏损矩阵
# ══════════════════════════════════════════════════════════════════════════════
def analyze_subcategory_region(rows: list[dict]) -> dict:
    """返回 17(Sub-Category) × 4(Region) 的利润矩阵。

    找出"哪个产品在哪个区域亏最多"——这是最直接的干预清单。
    """
    # 用 multi_group_by 做 2D 聚合
    profit_matrix = multi_group_by(rows, ['Sub-Category', 'Region'], 'Profit', 'sum')
    sales_matrix = multi_group_by(rows, ['Sub-Category', 'Region'], 'Sales', 'sum')
    count_matrix = multi_group_by(rows, ['Sub-Category', 'Region'], 'Profit', 'count')
    
    matrix = {}
    for key, profit in profit_matrix.items():
        sales = sales_matrix.get(key, 0)
        count = count_matrix.get(key, 0)
        matrix[key] = {
            'profit': round(profit, 2),
            'sales': round(sales, 2),
            'margin': round(profit / sales * 100, 1) if sales else 0,
            'count': int(count)
        }
    
    # 找出亏损最严重的 Top 10 (sub_category, region) 组合
    worst = sorted(
        [(k, v) for k, v in matrix.items() if v['profit'] < 0],
        key=lambda x: x[1]['profit']
    )[:10]
    
    return {
        'matrix': {str(k[0]) + '|' + k[1]: v for k, v in matrix.items()},
        'raw_matrix': matrix,
        'sub_categories': sorted(set(k[0] for k in matrix.keys())),
        'regions': ['West', 'East', 'Central', 'South'],
        'worst_combinations': [
            {'sub_category': k[0], 'region': k[1], **v} for k, v in worst
        ],
        'summary': f"最差组合：{worst[0][0][0]}在{worst[0][0][1]}亏损${abs(worst[0][1]['profit']):,.0f}" if worst else '无亏损组合'
    }


# ══════════════════════════════════════════════════════════════════════════════
# 分析 3：客群 × 折扣 利润矩阵
# ══════════════════════════════════════════════════════════════════════════════
def analyze_segment_discount(rows: list[dict]) -> dict:
    """返回 3(Segment) × 5(Discount Bin) 的利润/交易矩阵。

    CEO 问题：我们是否在给某些客群过度打折？
    """
    matrix = defaultdict(lambda: {'profit': 0.0, 'sales': 0.0, 'count': 0, 'loss_count': 0})
    
    for row in rows:
        seg = row['Segment']
        disc = float(row['Discount'])
        profit = float(row['Profit'])
        sales = float(row['Sales'])
        bin_name = _bin_discount(disc)
        key = (seg, bin_name)
        
        matrix[key]['profit'] += profit
        matrix[key]['sales'] += sales
        matrix[key]['count'] += 1
        if profit < 0:
            matrix[key]['loss_count'] += 1
    
    result = {}
    for key, vals in matrix.items():
        vals['margin'] = round(vals['profit'] / vals['sales'] * 100, 1) if vals['sales'] else 0
        vals['avg_profit_per_order'] = round(vals['profit'] / vals['count'], 2) if vals['count'] else 0
        vals['loss_rate'] = round(vals['loss_count'] / vals['count'] * 100, 1) if vals['count'] else 0
        result[str(key[0]) + '|' + key[1]] = vals
    
    segments = ['Consumer', 'Corporate', 'Home Office']
    bins = [b[0] for b in DISCOUNT_BINS]
    
    # 找出每个客群在高折扣段的表现
    findings = []
    for seg in segments:
        for b in bins[-2:]:  # 高折扣 + 极高折扣
            k = seg + '|' + b
            if k in result and result[k]['loss_rate'] >= 80:
                findings.append(f"{seg} 客群在「{b}」段亏损率 {result[k]['loss_rate']}%")
    
    return {
        'raw_matrix': result,
        'segments': segments,
        'bins': bins,
        'findings': findings,
        'summary': '；'.join(findings) if findings else '各客群折扣结构正常'
    }


# ══════════════════════════════════════════════════════════════════════════════
# 分析 4：子品类 × 折扣 —— "永不打折清单"
# ══════════════════════════════════════════════════════════════════════════════
def analyze_subcategory_discount(rows: list[dict]) -> dict:
    """返回每个子品类在不同折扣段的利润率，生成"永不打折清单"。

    核心逻辑：如果某产品在 >20% 折扣时利润率 < 0，则该产品应被列入警戒清单。
    """
    matrix = defaultdict(lambda: {'profit': 0.0, 'sales': 0.0, 'count': 0})
    
    for row in rows:
        sub = row['Sub-Category']
        disc = float(row['Discount'])
        profit = float(row['Profit'])
        sales = float(row['Sales'])
        bin_name = _bin_discount(disc)
        key = (sub, bin_name)
        
        matrix[key]['profit'] += profit
        matrix[key]['sales'] += sales
        matrix[key]['count'] += 1
    
    result = {}
    for key, vals in matrix.items():
        vals['margin'] = round(vals['profit'] / vals['sales'] * 100, 1) if vals['sales'] else 0
        result[str(key[0]) + '|' + key[1]] = vals
    
    # 生成"永不打折清单"：在中/高/极高折扣段利润率为负的子品类
    sub_categories = sorted(set(k[0] for k in matrix.keys()))
    bins = [b[0] for b in DISCOUNT_BINS]
    
    never_discount = []
    for sub in sub_categories:
        alerts = []
        for b in bins[2:]:  # 中折扣及以上
            k = sub + '|' + b
            if k in result and result[k]['margin'] < 0 and result[k]['count'] >= 5:
                alerts.append({'discount_bin': b, 'margin': result[k]['margin'], 'count': result[k]['count']})
        if alerts:
            never_discount.append({
                'sub_category': sub,
                'alerts': alerts,
                'severity': '🔴 严重' if any(a['margin'] < -50 for a in alerts) else '🟡 关注'
            })
    
    return {
        'raw_matrix': result,
        'sub_categories': sub_categories,
        'bins': bins,
        'never_discount': never_discount,
        'summary': f"{len(never_discount)} 个子品类需折扣管控"
    }


# ══════════════════════════════════════════════════════════════════════════════
# 分析 5：区域 × 折扣 矩阵
# ══════════════════════════════════════════════════════════════════════════════
def analyze_region_discount(rows: list[dict]) -> dict:
    """4(Region) × 5(Discount Bin) 利润矩阵。

    各区域是否存在系统性过度折扣？
    """
    matrix = defaultdict(lambda: {'profit': 0.0, 'sales': 0.0, 'count': 0, 'loss_count': 0})
    
    for row in rows:
        region = row['Region']
        disc = float(row['Discount'])
        profit = float(row['Profit'])
        sales = float(row['Sales'])
        bin_name = _bin_discount(disc)
        key = (region, bin_name)
        
        matrix[key]['profit'] += profit
        matrix[key]['sales'] += sales
        matrix[key]['count'] += 1
        if profit < 0:
            matrix[key]['loss_count'] += 1
    
    result = {}
    for key, vals in matrix.items():
        vals['margin'] = round(vals['profit'] / vals['sales'] * 100, 1) if vals['sales'] else 0
        vals['loss_rate'] = round(vals['loss_count'] / vals['count'] * 100, 1) if vals['count'] else 0
        result[str(key[0]) + '|' + key[1]] = vals
    
    regions = ['West', 'East', 'Central', 'South']
    bins = [b[0] for b in DISCOUNT_BINS]
    
    # 各区域高折扣段利润对比
    high_disc_compare = {}
    for r in regions:
        total_profit_high = sum(
            result.get(r + '|' + b, {}).get('profit', 0) for b in bins[-2:]
        )
        high_disc_compare[r] = round(total_profit_high, 2)
    
    return {
        'raw_matrix': result,
        'regions': regions,
        'bins': bins,
        'high_discount_profit': high_disc_compare,
        'summary': f"高折扣段亏损最严重区域：{min(high_disc_compare, key=high_disc_compare.get)} (${high_disc_compare[min(high_disc_compare, key=high_disc_compare.get)]:,.0f})"
    }


# ══════════════════════════════════════════════════════════════════════════════
# 分析 6：Top 5 亏损品诊断面板
# ══════════════════════════════════════════════════════════════════════════════
def analyze_loss_maker_diagnostics(rows: list[dict]) -> dict:
    """对 Top 5 亏损子品类，分别诊断其亏损根因。

    每个亏损品类输出：
    - 按区域的亏损分布
    - 按折扣段的亏损分布
    - 按客群的亏损分布
    """
    # 找出 Top 5 亏损子品类
    loss_by_sub = sum_by(
        [r for r in rows if float(r['Profit']) < 0],
        'Sub-Category', 'Profit'
    )
    top5 = sorted(loss_by_sub.items(), key=lambda x: x[1])[:5]
    
    diagnostics = {}
    for sub_cat, total_loss in top5:
        sub_rows = [r for r in rows if r['Sub-Category'] == sub_cat]
        loss_rows = [r for r in sub_rows if float(r['Profit']) < 0]
        
        # 区域分布
        region_loss = sum_by(loss_rows, 'Region', 'Profit')
        # 折扣分布
        disc_dist = defaultdict(lambda: {'count': 0, 'loss': 0.0})
        for r in loss_rows:
            bin_name = _bin_discount(float(r['Discount']))
            disc_dist[bin_name]['count'] += 1
            disc_dist[bin_name]['loss'] += float(r['Profit'])
        # 客群分布
        seg_loss = sum_by(loss_rows, 'Segment', 'Profit')
        
        diagnostics[sub_cat] = {
            'total_loss': round(total_loss, 2),
            'loss_count': len(loss_rows),
            'total_count': len(sub_rows),
            'loss_rate': round(len(loss_rows) / len(sub_rows) * 100, 1),
            'by_region': {k: round(v, 2) for k, v in sorted(region_loss.items(), key=lambda x: x[1])},
            'by_discount': {k: {'count': v['count'], 'loss': round(v['loss'], 2)} for k, v in disc_dist.items()},
            'by_segment': {k: round(v, 2) for k, v in sorted(seg_loss.items(), key=lambda x: x[1])},
            'root_cause': _diagnose_root_cause(sub_cat, disc_dist, region_loss, seg_loss)
        }
    
    return {
        'top5': [s for s, _ in top5],
        'diagnostics': diagnostics,
        'summary': f"Top 5 亏损品类合计亏损 ${sum(v['total_loss'] for v in diagnostics.values()):,.0f}"
    }


def _diagnose_root_cause(sub_cat: str, disc_dist: dict, region_loss: dict, seg_loss: dict) -> str:
    """根据数据自动诊断亏损根因。"""
    causes = []
    
    # 检查是否高折扣驱动
    high_disc_loss = sum(
        v['loss'] for k, v in disc_dist.items()
        if '高折扣' in k or '极高' in k
    )
    total_loss = sum(v['loss'] for v in disc_dist.values())
    if total_loss < 0 and high_disc_loss / total_loss > 0.5:
        causes.append(f"高折扣驱动（{abs(high_disc_loss)/abs(total_loss)*100:.0f}% 亏损来自 >40% 折扣）")
    
    # 检查是否集中在某区域
    if region_loss:
        worst_region = min(region_loss, key=region_loss.get)
        if len(region_loss) >= 3:
            causes.append(f"集中在 {worst_region} 区域")
    
    # 检查是否集中在某客群
    if seg_loss and len(seg_loss) >= 2:
        worst_seg = min(seg_loss, key=seg_loss.get)
        causes.append(f"{worst_seg} 客群亏损最重")
    
    return ' + '.join(causes) if causes else '多因素综合'


# ══════════════════════════════════════════════════════════════════════════════
# 分析 7：折扣弹性分析
# ══════════════════════════════════════════════════════════════════════════════
def analyze_discount_elasticity(rows: list[dict]) -> dict:
    """分析折扣增量对销量和利润的边际效应，找到最优折扣甜点。

    按折扣率分组（每 5% 一组），计算单位利润和销量。
    """
    # 按 5% 折扣间隔分组
    bins = defaultdict(lambda: {'sales': 0.0, 'profit': 0.0, 'quantity': 0, 'count': 0})
    
    for row in rows:
        disc = float(row['Discount'])
        disc_group = round(disc * 100 / 5) * 5  # 取 5% 整倍数
        if disc_group > 80:
            disc_group = 80
        bins[disc_group]['sales'] += float(row['Sales'])
        bins[disc_group]['profit'] += float(row['Profit'])
        bins[disc_group]['quantity'] += int(float(row['Quantity']))
        bins[disc_group]['count'] += 1
    
    result = []
    for disc_pct in sorted(bins.keys()):
        v = bins[disc_pct]
        result.append({
            'discount_pct': disc_pct,
            'sales': round(v['sales'], 2),
            'profit': round(v['profit'], 2),
            'margin': round(v['profit'] / v['sales'] * 100, 1) if v['sales'] else 0,
            'quantity': v['quantity'],
            'count': v['count'],
            'avg_profit_per_order': round(v['profit'] / v['count'], 2) if v['count'] else 0
        })
    
    # 找出最优折扣甜点（利润率 > 0 且销量最高的折扣点）
    sweet_spot = None
    best_combo = 0
    for r in result:
        if r['margin'] > 0:
            combo = r['margin'] * r['count'] / 1000  # 综合评分
            if combo > best_combo:
                best_combo = combo
                sweet_spot = r['discount_pct']
    
    return {
        'data': result,
        'sweet_spot': sweet_spot,
        'summary': f"最优折扣甜点约 {sweet_spot}%（利润率与销量最佳平衡点）" if sweet_spot else '未找到最优折扣点'
    }


# ══════════════════════════════════════════════════════════════════════════════
# 分析 8：州 × 品类 地理亏损分析
# ══════════════════════════════════════════════════════════════════════════════
def analyze_state_category(rows: list[dict]) -> dict:
    """State × Category 级利润矩阵，找出地理微观危机点。"""
    profit_matrix = multi_group_by(rows, ['State', 'Category'], 'Profit', 'sum')
    
    # 找出亏损最严重的 Top 15 (state, category) 组合
    worst = sorted(
        [(k, v) for k, v in profit_matrix.items() if v < 0],
        key=lambda x: x[1]
    )[:15]
    
    return {
        'raw_matrix': {str(k[0]) + '|' + k[1]: round(v, 2) for k, v in profit_matrix.items()},
        'worst_states': [
            {'state': k[0], 'category': k[1], 'loss': round(v, 2)}
            for k, v in worst
        ],
        'summary': f"{len(worst)} 个州-品类组合出现亏损" if worst else '无州级亏损'
    }


# ══════════════════════════════════════════════════════════════════════════════
# 主入口：运行所有下钻分析
# ══════════════════════════════════════════════════════════════════════════════
def run_all_drilldowns(data) -> dict:
    """运行全部 8 个下钻分析，返回结果字典。

    Args:
        data: SuperstoreData 实例

    Returns:
        {'category_discount': ..., 'subcategory_region': ..., ...}
    """
    rows = data.rows
    print("\n  🔬 多维度下钻分析...")
    
    results = {}
    
    print("    → 品类 × 折扣 热力图...")
    results['category_discount'] = analyze_category_discount(rows)
    
    print("    → 子品类 × 区域 亏损矩阵...")
    results['subcategory_region'] = analyze_subcategory_region(rows)
    
    print("    → 客群 × 折扣 利润对比...")
    results['segment_discount'] = analyze_segment_discount(rows)
    
    print("    → 永不打折清单...")
    results['subcategory_discount'] = analyze_subcategory_discount(rows)
    
    print("    → 区域 × 折扣 矩阵...")
    results['region_discount'] = analyze_region_discount(rows)
    
    print("    → Top 5 亏损品诊断...")
    results['loss_maker_diagnostics'] = analyze_loss_maker_diagnostics(rows)
    
    print("    → 折扣弹性曲线...")
    results['discount_elasticity'] = analyze_discount_elasticity(rows)
    
    print("    → 州 × 品类 地理分析...")
    results['state_category'] = analyze_state_category(rows)
    
    # 打印摘要
    print("\n  📋 下钻分析摘要：")
    for name, res in results.items():
        summary = res.get('summary', 'N/A')
        print(f"    • {name}: {summary}")
    
    return results
