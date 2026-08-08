
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


EVENT_PRIORITY = {
    "admission": 1,
    "transfer": 2,
    "diagnosis": 3,
    "procedure": 4,
    "laboratory": 5,
    "medication": 6,
    "icu_observation": 7,
}


@dataclass
class Evidence:
    score: float
    text: str
    source_table: str
    source_field: str
    source_id: str
    subject_id: str
    hadm_id: str
    event_time: str
    event_type: str


class ClinicalDataEngine:
    """
    Transparent local research engine.

    AI component:
      - TF-IDF vector retrieval over structured event descriptions.
      - Query-to-event matching is local and reproducible.
      - A confidence threshold causes abstention rather than unsupported answers.

    No patient-level data is sent to an external model/API.
    """

    def __init__(self, events: pd.DataFrame):
        self.events = events.copy()
        for c in ["subject_id", "hadm_id", "source_id", "source_table", "source_field",
                  "event_type", "event_time", "text"]:
            if c not in self.events.columns:
                self.events[c] = ""
        self.events["text"] = self.events["text"].fillna("").astype(str)
        self.events["subject_id"] = self.events["subject_id"].astype(str)
        self.events["hadm_id"] = self.events["hadm_id"].fillna("").astype(str)
        self.events["event_time_dt"] = pd.to_datetime(
            self.events["event_time"], errors="coerce"
        )
        self.events = self.events.sort_values(
            ["subject_id", "event_time_dt", "event_type"], na_position="last"
        ).reset_index(drop=True)

        self.vectorizer = TfidfVectorizer(
            lowercase=True, ngram_range=(1, 2), min_df=1, sublinear_tf=True
        )
        self.matrix = self.vectorizer.fit_transform(self.events["text"].tolist())

    def subjects(self) -> List[str]:
        return sorted(self.events["subject_id"].dropna().unique().tolist())

    def timeline(self, subject_id: str, hadm_id: Optional[str] = None) -> pd.DataFrame:
        df = self.events[self.events["subject_id"] == str(subject_id)].copy()
        if hadm_id and hadm_id != "All":
            df = df[df["hadm_id"] == str(hadm_id)]
        return df.sort_values(["event_time_dt", "event_type"], na_position="last")

    def search(
        self,
        query: str,
        subject_id: Optional[str] = None,
        hadm_id: Optional[str] = None,
        top_k: int = 8,
        threshold: float = 0.13,
    ) -> Tuple[List[Evidence], bool]:
        query = query.strip()
        if not query:
            return [], True

        sims = cosine_similarity(self.vectorizer.transform([query]), self.matrix)[0]
        idx = np.argsort(-sims)

        candidates = []
        for i in idx:
            row = self.events.iloc[int(i)]
            if subject_id and str(row["subject_id"]) != str(subject_id):
                continue
            if hadm_id and hadm_id != "All" and str(row["hadm_id"]) != str(hadm_id):
                continue
            candidates.append((float(sims[i]), row))
            if len(candidates) >= top_k:
                break

        if not candidates:
            return [], True

        # Abstain when the best match is too weak.
        abstain = candidates[0][0] < threshold
        results = []
        if not abstain:
            for score, row in candidates:
                if score < max(threshold * 0.72, 0.05):
                    continue
                results.append(
                    Evidence(
                        score=score,
                        text=str(row["text"]),
                        source_table=str(row["source_table"]),
                        source_field=str(row["source_field"]),
                        source_id=str(row["source_id"]),
                        subject_id=str(row["subject_id"]),
                        hadm_id=str(row["hadm_id"]),
                        event_time=str(row["event_time"]),
                        event_type=str(row["event_type"]),
                    )
                )
        return results, abstain

    @staticmethod
    def keyword_search(events: pd.DataFrame, query: str, top_k: int = 8) -> List[Evidence]:
        """Simple baseline used in evaluation."""
        terms = [t.lower() for t in re.findall(r"[a-zA-Z0-9_.-]+", query) if len(t) > 2]
        rows = []
        for _, row in events.iterrows():
            text = str(row.get("text", "")).lower()
            score = sum(1 for t in terms if t in text)
            if score:
                rows.append((score, row))
        rows.sort(key=lambda x: x[0], reverse=True)
        return [
            Evidence(
                score=float(score),
                text=str(row["text"]),
                source_table=str(row["source_table"]),
                source_field=str(row["source_field"]),
                source_id=str(row["source_id"]),
                subject_id=str(row["subject_id"]),
                hadm_id=str(row["hadm_id"]),
                event_time=str(row["event_time"]),
                event_type=str(row["event_type"]),
            )
            for score, row in rows[:top_k]
        ]


def quality_report(events: pd.DataFrame) -> Dict:
    df = events.copy()
    report = {}
    report["rows"] = int(len(df))
    report["subjects"] = int(df["subject_id"].nunique()) if "subject_id" in df else 0
    report["tables"] = int(df["source_table"].nunique()) if "source_table" in df else 0
    report["missing_event_time"] = int(pd.to_datetime(df["event_time"], errors="coerce").isna().sum())
    report["missing_subject_id"] = int(df["subject_id"].isna().sum()) if "subject_id" in df else 0
    key_cols = [c for c in ["subject_id", "hadm_id", "source_table", "source_id"] if c in df]
    report["duplicate_source_keys"] = int(df.duplicated(key_cols).sum()) if key_cols else 0

    dt = pd.to_datetime(df["event_time"], errors="coerce")
    report["event_time_min"] = str(dt.min()) if dt.notna().any() else "N/A"
    report["event_time_max"] = str(dt.max()) if dt.notna().any() else "N/A"

    missing = (
        df.isna().mean().sort_values(ascending=False).rename("missing_rate").reset_index()
        .rename(columns={"index": "field"})
    )
    report["missingness"] = missing
    return report


def make_event_table_from_mimic(
    hosp_dir: str,
    icu_dir: str,
    max_rows_per_table: int = 50000,
) -> pd.DataFrame:
    """
    Lightweight adapter for common MIMIC-IV Demo v2.2 CSV files.

    It preserves source table/field/id references and does not modify source rows.
    Large high-frequency tables are capped only for interactive UI speed; the
    full CSVs remain untouched on disk.
    """
    from pathlib import Path
    import gzip

    hosp = Path(hosp_dir)
    icu = Path(icu_dir)

    def read_csv(name: str, folder: Path):
        p = folder / name
        if not p.exists():
            return None
        return pd.read_csv(p, compression="gzip" if str(p).endswith(".gz") else None, low_memory=False)

    frames = []

    def add(df, table, time_col, text_fn, id_col=""):
        if df is None or df.empty or "subject_id" not in df.columns:
            return
        if len(df) > max_rows_per_table:
            df = df.sort_values(time_col, na_position="last").head(max_rows_per_table).copy()
        out = pd.DataFrame()
        out["subject_id"] = df["subject_id"].astype(str)
        out["hadm_id"] = df["hadm_id"].astype(str) if "hadm_id" in df else ""
        out["event_time"] = df[time_col] if time_col in df else pd.NaT
        out["event_type"] = table
        out["source_table"] = table
        out["source_field"] = time_col
        if id_col and id_col in df.columns:
            out["source_id"] = df[id_col].astype(str)
        else:
            out["source_id"] = [f"{table}:{i}" for i in df.index]
        out["text"] = df.apply(text_fn, axis=1)
        frames.append(out)

    admissions = read_csv("admissions.csv.gz", hosp)
    add(admissions, "admissions", "admittime",
        lambda r: f"Admission type {r.get('admission_type','')}; admission location {r.get('admission_location','')}; discharge location {r.get('discharge_location','')}",
        "hadm_id")

    transfers = read_csv("transfers.csv.gz", hosp)
    add(transfers, "transfers", "intime",
        lambda r: f"Transfer event; care unit {r.get('careunit','')}; event type {r.get('event_type','')}; out time {r.get('outtime','')}",
        "transfer_id")

    diagnoses = read_csv("diagnoses_icd.csv.gz", hosp)
    add(diagnoses, "diagnoses_icd", "chartdate",
        lambda r: f"Diagnosis code {r.get('icd_code','')}; version {r.get('icd_version','')}; sequence {r.get('seq_num','')}",
        "row_id" if "row_id" in (diagnoses.columns if diagnoses is not None else []) else "subject_id")

    procedures = read_csv("procedures_icd.csv.gz", hosp)
    add(procedures, "procedures_icd", "chartdate",
        lambda r: f"Procedure code {r.get('icd_code','')}; version {r.get('icd_version','')}; sequence {r.get('seq_num','')}",
        "row_id" if "row_id" in (procedures.columns if procedures is not None else []) else "subject_id")

    labs = read_csv("labevents.csv.gz", hosp)
    add(labs, "labevents", "charttime",
        lambda r: f"Lab item {r.get('itemid','')}; value {r.get('value','')}; numeric value {r.get('valuenum','')}; unit {r.get('valueuom','')}; flag {r.get('flag','')}",
        "labevent_id")

    prescriptions = read_csv("prescriptions.csv.gz", hosp)
    add(prescriptions, "prescriptions", "starttime",
        lambda r: f"Medication {r.get('drug','')}; route {r.get('route','')}; dose {r.get('dose_val_rx','')} {r.get('dose_unit_rx','')}; frequency {r.get('frequency','')}",
        "pharmacy_id")

    icustays = read_csv("icustays.csv.gz", icu)
    add(icustays, "icustays", "intime",
        lambda r: f"ICU stay; first care unit {r.get('first_careunit','')}; last care unit {r.get('last_careunit','')}; out time {r.get('outtime','')}",
        "stay_id")

    chartevents = read_csv("chartevents.csv.gz", icu)
    add(chartevents, "chartevents", "charttime",
        lambda r: f"ICU observation item {r.get('itemid','')}; value {r.get('value','')}; numeric value {r.get('valuenum','')}; unit {r.get('valueuom','')}",
        "chart_id")

    if not frames:
        raise FileNotFoundError("No supported MIMIC-IV CSV files found.")
    return pd.concat(frames, ignore_index=True)
