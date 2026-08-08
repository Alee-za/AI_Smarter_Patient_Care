
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.data_loader import load_sample
from src.engine import ClinicalDataEngine, quality_report

def test_timeline():
    e = ClinicalDataEngine(load_sample())
    df = e.timeline("1001")
    assert len(df) > 0
    assert list(df["event_time_dt"]) == sorted(df["event_time_dt"])

def test_provenance():
    e = ClinicalDataEngine(load_sample())
    results, abstain = e.search("creatinine", subject_id="1001")
    assert not abstain
    assert results
    assert results[0].source_table
    assert results[0].source_id
    assert results[0].event_time

def test_abstention():
    e = ClinicalDataEngine(load_sample())
    results, abstain = e.search("quantum banana spacecraft", subject_id="1001")
    assert abstain
    assert results == []

def test_quality_report():
    r = quality_report(load_sample())
    assert r["rows"] > 0
    assert r["subjects"] > 0
