
from pathlib import Path
import sys
import pandas as pd
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.data_loader import load_sample
from src.engine import ClinicalDataEngine

def main():
    events = load_sample()
    engine = ClinicalDataEngine(events)
    cases = [
        ("creatinine lab", "1001", "L1001"),
        ("antibiotic medication", "1001", "M1001"),
        ("ICU observation", "1001", "C1001"),
        ("admission emergency", "1003", "A1003"),
        ("procedure code", "1006", "P6001"),
    ]

    rows = []
    for q, subject, expected_id in cases:
        results, abstain = engine.search(q, subject_id=subject, top_k=5)
        ids = [r.source_id for r in results]
        rows.append({
            "query": q,
            "subject_id": subject,
            "expected_source_id": expected_id,
            "abstained": abstain,
            "top1_hit": bool(ids) and ids[0] == expected_id,
            "provenance_complete": all(
                all(getattr(r, x, "") != "" for x in
                    ["source_table","source_field","source_id","subject_id","event_time"])
                for r in results
            ) if results else True,
            "returned": ",".join(ids),
        })

    out = pd.DataFrame(rows)
    print(out.to_string(index=False))
    print("\nSynthetic-sample metrics (NOT clinical validation):")
    print("Top-1 retrieval accuracy:", round(out.top1_hit.mean(), 3))
    print("Provenance completeness:", round(out.provenance_complete.mean(), 3))

if __name__ == "__main__":
    main()
