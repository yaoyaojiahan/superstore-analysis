"""
data_loader.py — Data Loading & Preprocessing
=============================================
Loads the Superstore CSV, performs type conversions, and enriches
the dataset with derived columns for analysis.

Author: Yao Jiahan
Date: 2026-07-21
"""

import os
import sys

# Add parent to path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import load_csv, safe_float, safe_int
from config.settings import DATA_FILE


class SuperstoreData:
    """
    Loads and manages the Superstore dataset.
    Provides typed access to all rows and pre-computed groupings.
    """

    def __init__(self, filepath: str = None):
        self.filepath = filepath or DATA_FILE
        self.headers: list[str] = []
        self.rows: list[dict] = []
        self._loaded = False

    def load(self) -> 'SuperstoreData':
        """Load CSV and convert numeric columns to proper types."""
        self.headers, raw_rows = load_csv(self.filepath)

        # Convert numeric columns in-place
        numeric_cols = ['Sales', 'Quantity', 'Discount', 'Profit',
                        'Postal Code']
        for row in raw_rows:
            for col in numeric_cols:
                if col in row:
                    try:
                        if col == 'Quantity' or col == 'Postal Code':
                            row[col] = safe_int(row[col])
                        else:
                            row[col] = safe_float(row[col])
                    except (ValueError, KeyError):
                        row[col] = 0 if col != 'Postal Code' else 0

        self.rows = raw_rows
        self._loaded = True
        return self

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, idx) -> dict:
        return self.rows[idx]

    def get_column(self, name: str) -> list:
        """Extract a column as a list of values."""
        return [row.get(name, None) for row in self.rows]

    def get_numeric(self, name: str) -> list[float]:
        """Extract a numeric column as a list of floats."""
        return [safe_float(row.get(name, 0)) for row in self.rows]

    def summary(self) -> dict:
        """Return a summary of the dataset."""
        if not self._loaded:
            self.load()
        return {
            'file': os.path.basename(self.filepath),
            'rows': len(self.rows),
            'columns': len(self.headers),
            'column_names': self.headers,
            'numeric_columns': ['Sales', 'Quantity', 'Discount', 'Profit'],
            'categorical_columns': ['Ship Mode', 'Segment', 'Country',
                                    'City', 'State', 'Region',
                                    'Category', 'Sub-Category'],
        }
