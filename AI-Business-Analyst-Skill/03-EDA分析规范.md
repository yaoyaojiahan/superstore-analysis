# 03 — EDA 分析规范

> **描述性 EDA（12 维度）+ 诊断性下钻（8 维度）= 20 维度完整分析**

---

## 一、描述性 EDA（12 维度）

### 维度 1：销售总览
```python
total_sales, total_profit, profit_margin, total_orders, avg_order_value
```
**输出**：6 个 KPI + 品类/区域销售字典

### 维度 2：利润分析
```python
loss_count, loss_ratio, loss_amount, profit_stats (mean/median/std/q1/q3)
profit_by_region_category  # 2D 交叉
```
**关键**：loss_ratio > 10% → 🚨 CEO 级警报

### 维度 3：区域分析
```python
sales/profit/orders/margin by Region + sales/profit by State
```
**输出**：4 区域 × 4 指标 + 州级 Top/Bottom

### 维度 4：品类分析
```python
sales/profit/quantity/margin by Category
```
**关键**：找出利润率最低的品类

### 维度 5：子品类分析
```python
sales/profit/quantity/margin by Sub-Category (17 items)
```
**输出**：17 子品类排名表

### 维度 6：客群分析
```python
sales/profit/orders/avg_order_value by Segment
segment_category_sales  # 2D 交叉
```

### 维度 7：折扣影响
```python
discount_bins = ['0%', '1-20%', '21-40%', '41-60%', '>60%']
per_bin: {count, total_sales, total_profit, margin}
avg_discount by Category
```
**关键**：这是核心发现区域——哪个折扣段开始亏？

### 维度 8：帕累托分析
```python
pareto_data: [{sub_category, sales, cum_pct}]
items_for_80pct, pct_items_for_80
```

### 维度 9：亏损分析
```python
loss_by_subcategory (只有负利润)
total_loss_amount, loss_transaction_count
loss_with_high_discount, loss_high_discount_pct
```

### 维度 10：物流分析
```python
sales/profit/orders/avg_order by Ship Mode
```

### 维度 11：利润率分析
```python
margin by Region, margin by Sub-Category (sorted)
best_margin_sub, worst_margin_sub
```

### 维度 12：Top 10
```python
top10_sales, top10_profit, top10_quantity
```

---

## 二、诊断性下钻（8 维度）

### 下钻维度对照表

| # | 维度组合 | 矩阵大小 | 核心问题 |
|---|---------|---------|----------|
| 1 | Category × Discount Bin | 3 × 5 | 哪个品类打到几折开始亏？ |
| 2 | Sub-Category × Region | 17 × 4 | 哪个产品在哪个区域亏最多？ |
| 3 | Segment × Discount Bin | 3 × 5 | 哪个客群被过度打折？ |
| 4 | Sub-Category × Discount Bin | 17 × 5 | 哪些产品需要永不打折？ |
| 5 | Region × Discount Bin | 4 × 5 | 哪个区域折扣失控？ |
| 6 | Top 5 Loss-Maker 根因 | 5 组合 | 每类亏损的根因是什么？ |
| 7 | Discount Elasticity | 连续 | 最优折扣甜点在哪？ |
| 8 | State × Category | 49 × 3 | 哪些州在出血？ |

### 下钻 1：品类 × 折扣

```
输出：3×5 利润率矩阵
关键发现格式：
"Furniture 在「中折扣(21-40%)」段亏损率 95.4%——意味着即使是正常促销也几乎单单纯亏"
```

### 下钻 2：子品类 × 区域

```
输出：17×4 利润矩阵，取 Top 10 最差组合
关键发现格式：
"Tables × East = -$11,025（单组合最差），建议优先排查 East 的 Tables 定价与物流"
```

### 下钻 3：客群 × 折扣

```
输出：3×5 利润率矩阵
关键发现格式：
"所有客群在高折扣段 100% 亏损——证明折扣问题是系统性的，非客群差异"
```

### 下钻 4：子品类 × 折扣 → 永不打折清单

```
逻辑：如果子品类在 >20% 折扣段利润率 < 0 → 列入清单
输出：永不打折清单（分 🔴严重 / 🟡关注 两级）
```

### 下钻 5：区域 × 折扣

```
输出：4×5 矩阵
关键发现："Central 区域高折扣段亏损 $40,793，是 West 的 3 倍"
```

### 下钻 6：Top 5 亏损品根因诊断

```
每类亏损品输出：
- by_region: 区域分布
- by_discount: 折扣段分布
- by_segment: 客群分布
- root_cause: 自动诊断标签

诊断逻辑：
- 如果 >50% 亏损来自 >40% 折扣 → "高折扣驱动（政策可控）"
- 如果集中在某区域 → "区域驱动（需结构性调整）"
- 否则 → "多因素综合"
```

### 下钻 7：折扣弹性

```
按 5% 折扣间隔分组：
{discount_pct, sales, profit, margin, count, avg_profit}

找到 sweet_spot：利润率 > 0 且销量最高的折扣点
```

### 下钻 8：州 × 品类

```
输出：Top 15 最差 State × Category 组合
```

---

## 三、关键原则

1. **多维度是区分"初级分析"和"高级分析"的分水岭**
2. **每个交叉矩阵必须配一句商业解读**
3. **下钻结论必须区分"政策可控"和"结构性调整"**
4. **亏损品根因诊断不能只有数字——必须给出诊断标签**
