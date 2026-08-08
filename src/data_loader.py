
from pathlib import Path
import pandas as pd
from .engine import make_event_table_from_mimic

def load_sample():
    return pd.read_csv(Path(__file__).resolve().parents[1] / "data" / "sample" / "events.csv")

def load_data(data_root: str):
    root = Path(data_root)
    hosp = root / "hosp"
    icu = root / "icu"
    if hosp.exists() and icu.exists():
        return make_event_table_from_mimic(str(hosp), str(icu))
    return load_sample()
