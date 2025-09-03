import subprocess
import tempfile
import shutil
from pathlib import Path
import os

def test_cherrypicking_graph_creates_excel():
    # Arrange
    script_path = Path(__file__).parent.parent.parent / "automation_work" / "eu_stock_report_cherrypicking_graph.py"
    src_excel = Path(__file__).parent.parent.parent / "automation_work" / "EU_StockPrices_Report_CherryPicking.xlsx"
    temp_dir = tempfile.TemporaryDirectory()
    out_dir = Path(temp_dir.name)
    # Copy source Excel to temp dir
    shutil.copy(src_excel, out_dir / src_excel.name)
    expected_prefix = "EU_StockPrices_Report_CherryPicking_Graph_"
    # Patch environment so script writes to temp dir
    env = dict(**os.environ, USERPROFILE=str(out_dir.parent), HOME=str(out_dir.parent))

    # Copy script to temp dir and run it there
    shutil.copy(script_path, out_dir / script_path.name)
    proc = subprocess.run(
        ["python", str(out_dir / script_path.name)],
        cwd=out_dir,
        env=env,
        capture_output=True,
        text=True,
        timeout=120
    )

    # Assert: check that a file with the expected prefix exists
    found = any(f.name.startswith(expected_prefix) and f.suffix == ".xlsx" for f in out_dir.iterdir())
    assert found, f"No output Excel file with prefix '{expected_prefix}' was created in {out_dir}"
    temp_dir.cleanup()