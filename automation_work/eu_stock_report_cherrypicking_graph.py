"""
Creates an Excel file with a line chart showing price differences for each stock over time.
Reads daily sheets from "EU_StockPrices_Report_CherryPicking.xlsx" in
C:/Users/I070494/Downloads/AI_EU_StockPrices_Report, and writes the chart to
"EU_StockPrices_Report_CherryPicking_Graph_DDMMYYYY.xlsx" in the same folder.
Each stock is shown in a different color.
"""

import os
from pathlib import Path
from datetime import datetime
import pandas as pd  # type: ignore
from openpyxl import Workbook  # type: ignore
from openpyxl.chart import LineChart, Reference, Series  # type: ignore
from openpyxl.chart.label import DataLabelList  # type: ignore

# Paths
DIR = Path(r"C:\Users\I070494\Downloads\AI_EU_StockPrices_Report")
SRC_FILE = DIR / "EU_StockPrices_Report_CherryPicking.xlsx"
TODAY = datetime.now().strftime("%d%m%Y")
OUT_FILE = DIR / f"EU_StockPrices_Report_CherryPicking_Graph_{TODAY}.xlsx"

# Colors for up to 15 stocks (hex)
COLORS = [
    "FF0000", "00B050", "0070C0", "FFC000", "7030A0", "00FFFF", "FF00FF",
    "C00000", "00C0C0", "C0C000", "0000FF", "008000", "800080", "808000", "800000"
]

def read_all_days(src_file):
    """Read all sheets, using row 2 as header. Return dict: {sheet_name: DataFrame}"""
    xls = pd.ExcelFile(src_file)
    sheets = {}
    for name in xls.sheet_names:
        # Use header=1 to read column names from row 2
        df = pd.read_excel(xls, sheet_name=name, header=1)
        sheets[name] = df
    return sheets

def build_price_diff_table(sheets):
    """
    Returns DataFrame: rows=days, columns=tickers, values=price diff.
    Skips sheets without 'Ticker' or 'Price Diff' columns.
    """
    days = []
    tickers = set()
    for day, df in sheets.items():
        # Skip sheets missing required columns
        if not all(col in df.columns for col in ["Ticker", "Price Diff"]):
            print(f"Skipping sheet '{day}' (missing columns)")
            continue
        days.append(day)
        tickers.update(df["Ticker"].dropna().unique())
    days.sort()
    tickers = sorted(list(tickers))
    table = pd.DataFrame(index=days, columns=tickers)
    for day, df in sheets.items():
        if not all(col in df.columns for col in ["Ticker", "Price Diff"]):
            continue
        for _, row in df.iterrows():
            t = row.get("Ticker")
            v = row.get("Price Diff")
            if pd.notna(t) and pd.notna(v):
                table.at[day, t] = v
    return table

def write_excel_with_chart(table, out_file):
    """
    Writes table to Excel and adds a detailed, readable line chart for price diff of each stock.
    Chart is large, has legend, axis titles, and shows data labels for each point.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "PriceDiffs"

    # Write header
    ws.append(["Day"] + list(table.columns))
    # Write data
    for idx, row in table.iterrows():
        ws.append([idx] + [row[t] for t in table.columns])

    # Create chart
    chart = LineChart()
    chart.title = "Price Diff Over Time (per Stock)"
    chart.y_axis.title = "Price Diff (EUR)"
    chart.x_axis.title = "Day"
    chart.width = 40    # make chart wider
    chart.height = 20   # make chart taller
    chart.legend.position = "r"  # legend on right
    chart.legend.overlay = False

    n_rows = len(table.index)
    n_cols = len(table.columns)
    cats = Reference(ws, min_col=1, min_row=2, max_row=n_rows+1)

    # Add series for each ticker with a different color and show data labels
    for i in range(n_cols):
        values = Reference(ws, min_col=2+i, min_row=2, max_row=n_rows+1)
        ser = Series(values, title=table.columns[i])
        color = COLORS[i % len(COLORS)]
        ser.graphicalProperties.line.solidFill = color
        ser.graphicalProperties.line.width = 30000  # thicker lines for visibility
        # Show value labels for each point
        ser.dLbls = DataLabelList()
        ser.dLbls.showVal = True
        chart.series.append(ser)
    chart.set_categories(cats)
    ws.add_chart(chart, "E2")

    wb.save(out_file)

def main():
    if not SRC_FILE.exists():
        print(f"Source file {SRC_FILE} does not exist.")
        return
    if OUT_FILE.exists():
        print(f"Output file already exists: {OUT_FILE}")
        return
    sheets = read_all_days(SRC_FILE)
    table = build_price_diff_table(sheets)
    write_excel_with_chart(table, OUT_FILE)
    print(f"Excel with chart saved: {OUT_FILE}")

if __name__ == "__main__":
    main()