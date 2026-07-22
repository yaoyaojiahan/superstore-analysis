"""
insights.py — Business Insight Generator
========================================
For each analysis dimension, generates:
- Business Insight (what the data tells us about the business)
- Business Recommendation (what action to take)

Follows the McKinsey "Insight → So What → Now What" framework.

Author: Yao Jiahan
Date: 2026-07-21
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import top_n


class BusinessInsights:
    """Generates structured business insights from EDA results."""

    def __init__(self, eda_results: dict):
        self.r = eda_results
        self.insights = []

    def generate_all(self) -> list[dict]:
        """Generate all business insights as a structured list."""
        self.insights = []

        self._insight_sales_overview()
        self._insight_profit()
        self._insight_regional()
        self._insight_category()
        self._insight_discount()
        self._insight_pareto()
        self._insight_loss_makers()
        self._insight_segment()
        self._insight_ship_mode()

        return self.insights

    def _add(self, section: str, chart_title: str,
             insight: str, recommendation: str):
        """Add an insight entry."""
        self.insights.append({
            'section': section,
            'chart': chart_title,
            'insight': insight,
            'recommendation': recommendation,
        })

    # ── Sales Overview Insight ─────────────────────────────────────────
    def _insight_sales_overview(self):
        so = self.r.get('sales_overview', {})
        total_sales = so.get('total_sales', 0)
        profit_margin = so.get('profit_margin', 0)
        avg_order = so.get('avg_order_value', 0)

        self._add(
            'Sales Overview',
            'KPI Summary Dashboard',
            f"Total sales revenue of ${total_sales:,.0f} with a net profit margin of "
            f"{profit_margin}%. The average order value is ${avg_order:.2f}. "
            f"The business is profitable overall, but margin compression is evident "
            f"in certain product categories that significantly drag down bottom-line performance.",
            f"Implement a margin-based KPI dashboard to monitor real-time profitability. "
            f"Set a minimum profit margin threshold of 10% for all product lines and "
            f"flag any sub-category falling below this for immediate review."
        )

    # ── Profit Insight ─────────────────────────────────────────────────
    def _insight_profit(self):
        pa = self.r.get('profit_analysis', {})
        loss_ratio = pa.get('loss_ratio', 0)
        loss_amount = pa.get('loss_amount', 0)
        total_profit = pa.get('total_profit', 0)

        self._add(
            'Profit Analysis',
            'Profit Waterfall by Category',
            f"While total profit is ${total_profit:,.0f}, {loss_ratio}% of all transactions "
            f"are unprofitable, resulting in ${abs(loss_amount):,.0f} in total losses. "
            f"This 'leaky bucket' problem means the profitable transactions are subsidizing "
            f"the loss-making ones. The primary driver of these losses is excessive discounting "
            f"on already low-margin products.",
            f"Launch a 'Stop the Bleeding' initiative: (1) Set discount caps at 30% for "
            f"sub-categories with margin < 15%. (2) Implement a discount approval workflow "
            f"for any discount exceeding 40%. (3) Quarterly review of loss-making SKUs "
            f"with a decision to either reprice, rebundle, or discontinue."
        )

    # ── Regional Insight ───────────────────────────────────────────────
    def _insight_regional(self):
        ra = self.r.get('regional_analysis', {})
        margins = ra.get('margin_by_region', {})
        sales_by_state = ra.get('sales_by_state', {})

        best_region = max(margins, key=margins.get) if margins else 'N/A'
        worst_region = min(margins, key=margins.get) if margins else 'N/A'
        top_states = sorted(sales_by_state.items(),
                            key=lambda x: x[1], reverse=True)[:3]

        self._add(
            'Regional Analysis',
            'Regional Sales & Profit Margin',
            f"Performance varies significantly across regions. {best_region} leads with "
            f"the highest profit margin, while {worst_region} trails. The top 3 states by "
            f"sales are: {', '.join(f'{s} (${v:,.0f})' for s, v in top_states)}. "
            f"This geographic concentration presents both an opportunity "
            f"(double down on strong markets) and a risk (over-reliance on key states).",
            f"Develop a two-pronged regional strategy: (1) For high-performing regions, "
            f"invest in targeted marketing and loyalty programs to drive repeat purchases. "
            f"(2) For underperforming regions, conduct a root-cause analysis — "
            f"is it pricing, shipping costs, competition, or product mix? "
            f"Pilot a localized discount strategy in one underperforming region."
        )

    # ── Category Insight ───────────────────────────────────────────────
    def _insight_category(self):
        ca = self.r.get('category_analysis', {})
        margins = ca.get('margin_by_category', {})
        sales = ca.get('sales_by_category', {})

        best_cat = max(margins, key=margins.get) if margins else 'N/A'
        worst_cat = min(margins, key=margins.get) if margins else 'N/A'

        self._add(
            'Category Analysis',
            'Category Sales & Margin Comparison',
            f"Categories show stark margin differences: {best_cat} is the most profitable "
            f"category, while {worst_cat} has the lowest margins. The sales volume vs. "
            f"profitability trade-off is clearly visible — some high-volume categories "
            f"contribute disproportionately low profit. This suggests a product mix "
            f"optimization opportunity.",
            f"Reallocate promotional budget toward high-margin categories. "
            f"For the low-margin category ({worst_cat}), explore: "
            f"(1) Supplier renegotiation to improve COGS, "
            f"(2) Bundling with high-margin accessories, "
            f"(3) Minimum order quantities to improve unit economics."
        )

    # ── Discount Impact Insight ────────────────────────────────────────
    def _insight_discount(self):
        di = self.r.get('discount_impact', {})
        bins = di.get('discount_bins', {})
        high = bins.get('High (41-60%)', {})
        very_high = bins.get('Very High (60%+)', {})

        self._add(
            'Discount Impact',
            'Profit Margin by Discount Level',
            f"Discounts above 40% are margin-destroying. Orders with 41-60% discount achieve "
            f"a profit margin of only {high.get('margin', 0)}%, while those above 60% "
            f"discount run at {very_high.get('margin', 0)}% margin — effectively losing money "
            f"on every transaction. The data confirms a classic retail pattern: deep "
            f"discounts do not drive enough incremental volume to offset margin erosion.",
            f"Implement a 'Smart Discounting' policy: (1) Maximum discount of 40% for all "
            f"products without manager approval. (2) Tiered discount based on product margin "
            f"— high-margin products can sustain deeper discounts. (3) A/B test different "
            f"discount levels to find the optimal price elasticity point. "
            f"(4) Track Discount-to-Profit ratio as a new KPI."
        )

    # ── Pareto Insight ─────────────────────────────────────────────────
    def _insight_pareto(self):
        pareto = self.r.get('pareto_analysis', {})
        items_for_80 = pareto.get('items_for_80', 0)
        total_items = pareto.get('total_items', 1)
        pct = pareto.get('pct_items_for_80', 0)

        # Count how many items reach 80%
        count_80 = sum(1 for item in pareto.get('pareto_data', [])
                      if item.get('cum_pct', 0) >= 80) or items_for_80

        self._add(
            'Pareto Analysis (80/20 Rule)',
            'Pareto Chart — Cumulative Sales Concentration',
            f"The Pareto principle holds strongly: approximately "
            f"{pct}% of sub-categories generate 80% of total sales revenue. "
            f"This concentration means that a small subset of products drives the "
            f"vast majority of business value. The long tail of low-contributing "
            f"sub-categories consumes operational resources with minimal return.",
            f"Apply a category management framework: (1) 'Stars' (Top 20%): Protect at all "
            f"costs — ensure inventory, competitive pricing, and marketing support. "
            f"(2) 'Cash Cows' (Middle 30%): Maintain with minimal investment. "
            f"(3) 'Question Marks' (Bottom 50%): Evaluate for discontinuation or radical "
            f"restructuring. This portfolio approach will free up working capital and "
            f"reduce operational complexity."
        )

    # ── Loss-Makers Insight ────────────────────────────────────────────
    def _insight_loss_makers(self):
        lm = self.r.get('loss_makers', {})
        losses = lm.get('loss_by_subcategory', {})
        high_disc_pct = lm.get('loss_high_discount_pct', 0)
        total_loss = abs(lm.get('total_loss_amount', 0))

        top_losers = sorted(losses.items(), key=lambda x: x[1])[:5]

        self._add(
            'Loss-Making Products',
            'Bottom 10 Sub-Categories by Profit',
            f"The biggest loss-makers are: {', '.join(f'{s} (${v:,.0f})' for s, v in top_losers)}. "
            f"A staggering {high_disc_pct}% of all loss-making transactions involve "
            f"discounts of 40% or higher. Total losses from these underperforming "
            f"sub-categories amount to ${total_loss:,.0f} — money that could be "
            f"redeployed toward growth initiatives.",
            f"Immediate actions on loss-making sub-categories: "
            f"(1) Freeze all promotional discounts > 30% on these items. "
            f"(2) Conduct a supplier cost review for the top 3 loss-makers. "
            f"(3) Test price increases of 5-10% on inelastic products. "
            f"(4) Bundle loss-leaders with high-margin items rather than "
            f"discounting them individually. Target: reduce loss contributions "
            f"by 50% within two quarters."
        )

    # ── Segment Insight ────────────────────────────────────────────────
    def _insight_segment(self):
        seg = self.r.get('segment_analysis', {})
        sales_by_seg = seg.get('sales_by_segment', {})
        avg_order = seg.get('avg_order_value', {})

        self._add(
            'Customer Segment Analysis',
            'Sales & Profit by Customer Segment',
            f"Consumer segment dominates with ${sales_by_seg.get('Consumer', 0):,.0f} in sales. "
            f"Average order values vary by segment: "
            f"{', '.join(f'{k}: ${v:,.0f}' for k, v in avg_order.items())}. "
            f"The Corporate and Home Office segments, while smaller in volume, "
            f"may offer higher lifetime value due to recurring B2B purchasing patterns.",
            f"Segment-specific strategies: (1) Consumer: Launch a loyalty/rewards program "
            f"to increase purchase frequency. (2) Corporate: Develop a B2B catalog with "
            f"volume pricing and dedicated account management. (3) Home Office: "
            f"Create 'Work From Home' bundles targeting the growing remote work market. "
            f"Track Customer Lifetime Value (CLV) by segment as a strategic KPI."
        )

    # ── Ship Mode Insight ──────────────────────────────────────────────
    def _insight_ship_mode(self):
        sm = self.r.get('ship_mode_analysis', {})
        orders = sm.get('orders_by_ship_mode', {})

        standard = orders.get('Standard Class', 0)
        same_day = orders.get('Same Day', 0)
        total = sum(orders.values())

        self._add(
            'Shipping Mode Analysis',
            'Sales Distribution by Ship Mode',
            f"Standard Class dominates shipping preferences ({standard/total*100:.0f}% "
            f"of orders), while Same Day delivery accounts for only "
            f"{same_day/total*100:.0f}% of orders but likely at a premium price point. "
            f"Shipping mode preference varies by region and segment, offering "
            f"opportunities for differentiated logistics strategies.",
            f"Optimize shipping strategy: (1) Negotiate volume discounts with Standard "
            f"Class carriers given the high volume. (2) Offer free Standard Class shipping "
            f"above a minimum order threshold to increase average order value. "
            f"(3) Market Same Day delivery as a premium upsell in high-density urban areas "
            f"where logistics costs are lower."
        )

    def print_summary(self):
        """Print all insights to console."""
        print("\n" + "=" * 70)
        print("  BUSINESS INSIGHTS & RECOMMENDATIONS")
        print("=" * 70)

        for i, ins in enumerate(self.insights, 1):
            print(f"\n{'─' * 70}")
            print(f"  [{i}] {ins['section']}")
            print(f"{'─' * 70}")
            print(f"\n  📊 Chart: {ins['chart']}")
            print(f"\n  💡 Business Insight:")
            print(f"     {ins['insight']}")
            print(f"\n  🎯 Business Recommendation:")
            print(f"     {ins['recommendation']}")

        print(f"\n{'=' * 70}")
        print(f"  Total: {len(self.insights)} insights generated")
        print(f"{'=' * 70}\n")
