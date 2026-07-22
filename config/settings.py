"""
settings.py — Project Configuration
====================================
Centralized configuration for the Superstore Business Analysis project.

Author: Yao Jiahan
Date: 2026-07-21
"""

import os

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
IMAGES_DIR = os.path.join(BASE_DIR, 'images')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

DATA_FILE = os.path.join(DATA_DIR, 'Superstore.csv')

# ── Color Palette — McKinsey-inspired corporate palette ────────────────────
COLORS = {
    'primary': '#003366',        # Deep navy
    'secondary': '#0066CC',      # Medium blue
    'accent': '#00A86B',         # Green accent (profit)
    'danger': '#DC3545',         # Red (loss)
    'warning': '#FFC107',        # Amber (caution)
    'neutral': '#6C757D',        # Gray
    'light': '#F8F9FA',          # Light gray background
    'dark': '#212529',           # Near black
    'white': '#FFFFFF',

    # Categorical palette (McKinsey-inspired)
    'palette': ['#003366', '#0066CC', '#00A86B', '#FF6B35',
                '#8B5CF6', '#EC4899', '#10B981', '#F59E0B',
                '#6366F1', '#EF4444', '#06B6D4', '#84CC16'],
}

# ── Plotly Template ────────────────────────────────────────────────────────
PLOTLY_TEMPLATE = {
    'layout': {
        'font': {'family': 'Segoe UI, Arial, sans-serif', 'color': '#212529'},
        'title': {'font': {'size': 18, 'color': '#003366'}},
        'plot_bgcolor': '#FFFFFF',
        'paper_bgcolor': '#FFFFFF',
        'xaxis': {
            'gridcolor': '#E5E7EB',
            'linecolor': '#D1D5DB',
            'title_font': {'color': '#6C757D'},
        },
        'yaxis': {
            'gridcolor': '#E5E7EB',
            'linecolor': '#D1D5DB',
            'title_font': {'color': '#6C757D'},
        },
        'legend': {
            'font': {'color': '#6C757D'},
        },
        'margin': {'l': 60, 'r': 30, 't': 60, 'b': 50},
    }
}

# ── Business Constants ─────────────────────────────────────────────────────
SEGMENTS = ['Consumer', 'Corporate', 'Home Office']
REGIONS = ['West', 'East', 'Central', 'South']
CATEGORIES = ['Furniture', 'Office Supplies', 'Technology']
SHIP_MODES = ['Standard Class', 'Second Class', 'First Class', 'Same Day']

# Loss threshold for identifying problem products
LOSS_THRESHOLD = 0  # Profit < 0

# High discount threshold
HIGH_DISCOUNT_THRESHOLD = 0.40  # 40%+ discount
