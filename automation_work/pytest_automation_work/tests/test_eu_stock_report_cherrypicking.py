import subprocess
import tempfile
import shutil
from pathlib import Path

def test_cherrypicking_creates_excel():
    # Arrange
    script_path = Path(__file__).parent.parent.parent / "automation_work" / "eu_stock_report_cherrypicking.py"
    temp_dir = tempfile.TemporaryDirectory()
    out_dir = Path(temp_dir.name)
    expected_file = out_dir / "EU_StockPrices_Report_CherryPicking.xlsx"

    # Patch environment so script writes to temp dir
    # (Assumes OUT_DIR is set at the top of the script)
    # We use PYTHONPATH to allow import if needed
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

    # Assert
    assert expected_file.exists(), f"Expected Excel file not created: {expected_file}"
    temp_dir.cleanup()